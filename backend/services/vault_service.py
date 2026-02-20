"""
Vault Service: Multi-currency vault management with ledger-based balance resolution.

This service handles:
- Vault creation and management
- Ledger-based balance reconstruction
- Multi-currency deposits and withdrawals
- Currency position tracking
- FX cost basis management
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
import uuid
import logging

from backend.extensions import db
from backend.models.ledger import (
    Vault, VaultCurrencyPosition, LedgerAccount, LedgerEntry,
    AccountType, EntryType, TransactionType, FXValuationSnapshot
)
from backend.services.ledger_service import LedgerService

logger = logging.getLogger(__name__)


class VaultService:
    """Service for managing multi-currency vaults with ledger integration."""
    
    PRECISION = Decimal('0.000001')
    
    @staticmethod
    def create_vault(
        name: str,
        owner_type: str,
        owner_id: int,
        base_currency: str = 'USD',
        allow_multi_currency: bool = True,
        auto_fx_revaluation: bool = True
    ) -> Vault:
        """
        Create a new vault with associated ledger accounts.
        
        Args:
            name: Vault name
            owner_type: Type of owner ('user', 'farm', 'organization')
            owner_id: ID of the owner
            base_currency: Primary currency for reporting
            allow_multi_currency: Allow holdings in multiple currencies
            auto_fx_revaluation: Automatically revalue on FX rate changes
            
        Returns:
            Created Vault instance
        """
        vault_id = str(uuid.uuid4())
        
        # Create main ledger account for vault
        account_code = f"VAULT-{vault_id[:8].upper()}"
        ledger_account, _ = LedgerService.get_or_create_account(
            account_code=account_code,
            name=f"Vault: {name}",
            account_type=AccountType.ASSET,
            currency=base_currency,
            entity_type='vault',
            entity_id=None,  # Will update after vault creation
            description=f"Main account for vault {name}"
        )
        
        vault = Vault(
            vault_id=vault_id,
            name=name,
            owner_type=owner_type,
            owner_id=owner_id,
            base_currency=base_currency,
            ledger_account_id=ledger_account.id,
            allow_multi_currency=allow_multi_currency,
            auto_fx_revaluation=auto_fx_revaluation
        )
        
        db.session.add(vault)
        db.session.flush()
        
        # Update ledger account with vault entity
        ledger_account.entity_id = vault.id
        
        db.session.commit()
        
        logger.info(f"Created vault {vault_id}: {name} for {owner_type}/{owner_id}")
        
        return vault
    
    @staticmethod
    def get_vault(vault_id: str) -> Optional[Vault]:
        """Get vault by vault_id."""
        return Vault.query.filter_by(vault_id=vault_id).first()
    
    @staticmethod
    def get_vault_by_id(id: int) -> Optional[Vault]:
        """Get vault by database ID."""
        return Vault.query.get(id)
    
    @staticmethod
    def get_or_create_currency_position(
        vault: Vault,
        currency: str
    ) -> Tuple[VaultCurrencyPosition, bool]:
        """
        Get or create a currency position within a vault.
        
        Returns:
            Tuple of (position, created)
        """
        position = VaultCurrencyPosition.query.filter_by(
            vault_id=vault.id,
            currency=currency
        ).first()
        
        if position:
            return position, False
        
        # Create sub-account for this currency
        account_code = f"VAULT-{vault.vault_id[:8].upper()}-{currency}"
        ledger_account, _ = LedgerService.get_or_create_account(
            account_code=account_code,
            name=f"{vault.name} - {currency}",
            account_type=AccountType.ASSET,
            currency=currency,
            parent_id=vault.ledger_account_id,
            entity_type='vault_position',
            entity_id=vault.id,
            description=f"{currency} position in vault {vault.name}"
        )
        
        position = VaultCurrencyPosition(
            vault_id=vault.id,
            currency=currency,
            ledger_account_id=ledger_account.id
        )
        
        db.session.add(position)
        db.session.commit()
        
        logger.info(f"Created currency position {currency} for vault {vault.vault_id}")
        
        return position, True
    
    @staticmethod
    def get_position_balance(position: VaultCurrencyPosition) -> Decimal:
        """
        Get balance for a currency position from ledger entries.
        
        Returns:
            Balance in position currency
        """
        if not position.ledger_account_id:
            return Decimal('0')
        
        return LedgerService.get_account_balance(position.ledger_account_id)
    
    @staticmethod
    def get_vault_balances(vault: Vault) -> Dict:
        """
        Get all currency balances for a vault.
        
        Returns:
            Dict with currency positions and values
        """
        from backend.services.fx_service import FXService
        
        positions = vault.currency_positions.all()
        
        balances = {
            'vault_id': vault.vault_id,
            'name': vault.name,
            'base_currency': vault.base_currency,
            'positions': [],
            'total_base_value': Decimal('0'),
            'unrealized_fx_gain': Decimal('0')
        }
        
        for position in positions:
            balance = VaultService.get_position_balance(position)
            
            # Get current FX rate
            if position.currency == vault.base_currency:
                current_rate = Decimal('1')
            else:
                current_rate = FXService.get_rate(
                    position.currency,
                    vault.base_currency
                ) or Decimal('1')
            
            base_value = balance * current_rate
            
            # Calculate unrealized gain/loss
            unrealized_gain = Decimal('0')
            if position.cost_basis_rate and position.cost_basis_amount:
                original_base_value = position.cost_basis_amount
                unrealized_gain = base_value - original_base_value
            
            balances['positions'].append({
                'currency': position.currency,
                'balance': float(balance),
                'fx_rate': float(current_rate),
                'base_value': float(base_value),
                'cost_basis_rate': float(position.cost_basis_rate) if position.cost_basis_rate else None,
                'unrealized_fx_gain': float(unrealized_gain),
                'cumulative_realized_fx_gain': float(position.cumulative_realized_fx_gain)
            })
            
            balances['total_base_value'] += base_value
            balances['unrealized_fx_gain'] += unrealized_gain
        
        balances['total_base_value'] = float(balances['total_base_value'])
        balances['unrealized_fx_gain'] = float(balances['unrealized_fx_gain'])
        
        return balances
    
    @staticmethod
    def deposit(
        vault: Vault,
        amount: Decimal,
        currency: str,
        fx_rate: Decimal = None,
        source_description: str = None,
        reference: str = None,
        created_by: int = None
    ) -> Dict:
        """
        Deposit funds into vault.
        
        Args:
            vault: Target vault
            amount: Amount to deposit
            currency: Currency of deposit
            fx_rate: FX rate to base currency (if different)
            source_description: Description of source
            reference: External reference number
            created_by: User ID
            
        Returns:
            Deposit result with transaction details
        """
        if vault.is_locked:
            raise ValueError(f"Vault is locked: {vault.locked_reason}")
        
        if not vault.allow_multi_currency and currency != vault.base_currency:
            raise ValueError(f"Vault does not allow multi-currency. Use {vault.base_currency}")
        
        # Get or create currency position
        position, _ = VaultService.get_or_create_currency_position(vault, currency)
        
        # Determine FX rate
        if currency == vault.base_currency:
            fx_rate = Decimal('1')
        elif not fx_rate:
            from backend.services.fx_service import FXService
            fx_rate = FXService.get_rate(currency, vault.base_currency) or Decimal('1')
        
        # Get or create external source account
        source_account, _ = LedgerService.get_or_create_account(
            account_code='3000-EXTERNAL-DEPOSITS',
            name='External Deposits',
            account_type=AccountType.EQUITY,
            currency=vault.base_currency,
            is_system=True
        )
        
        # Create ledger transaction
        entries = [
            {
                'account_id': position.ledger_account_id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': source_description or 'Deposit'
            },
            {
                'account_id': source_account.id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': f"Deposit to vault {vault.name}"
            }
        ]
        
        transaction = LedgerService.create_transaction(
            transaction_type=TransactionType.DEPOSIT,
            entries=entries,
            description=source_description or f"Deposit to {vault.name}",
            reference_number=reference,
            source_type='vault_deposit',
            source_id=vault.id,
            base_currency=vault.base_currency,
            created_by=created_by
        )
        
        # Update cost basis
        VaultService._update_cost_basis(position, amount, fx_rate)
        
        db.session.commit()
        
        new_balance = VaultService.get_position_balance(position)
        
        logger.info(
            f"Deposit to vault {vault.vault_id}: {amount} {currency} "
            f"(fx_rate={fx_rate}), new_balance={new_balance}"
        )
        
        return {
            'transaction_id': transaction.transaction_id,
            'amount': float(amount),
            'currency': currency,
            'fx_rate': float(fx_rate),
            'base_amount': float(Decimal(str(amount)) * fx_rate),
            'new_balance': float(new_balance),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def withdraw(
        vault: Vault,
        amount: Decimal,
        currency: str,
        fx_rate: Decimal = None,
        destination_description: str = None,
        reference: str = None,
        created_by: int = None
    ) -> Dict:
        """
        Withdraw funds from vault.
        
        Records realized FX gain/loss if selling foreign currency.
        """
        if vault.is_locked:
            raise ValueError(f"Vault is locked: {vault.locked_reason}")
        
        # Get currency position
        position = VaultCurrencyPosition.query.filter_by(
            vault_id=vault.id,
            currency=currency
        ).first()
        
        if not position:
            raise ValueError(f"No {currency} position in vault")
        
        current_balance = VaultService.get_position_balance(position)
        
        if current_balance < amount:
            raise ValueError(
                f"Insufficient balance: {current_balance} {currency} available, "
                f"{amount} {currency} requested"
            )
        
        # Determine FX rate
        if currency == vault.base_currency:
            fx_rate = Decimal('1')
        elif not fx_rate:
            from backend.services.fx_service import FXService
            fx_rate = FXService.get_rate(currency, vault.base_currency) or Decimal('1')
        
        # Calculate realized FX gain/loss
        realized_fx_gain = Decimal('0')
        if position.cost_basis_rate and currency != vault.base_currency:
            original_value = amount * position.cost_basis_rate
            current_value = amount * fx_rate
            realized_fx_gain = current_value - original_value
        
        # Get or create external destination account
        dest_account, _ = LedgerService.get_or_create_account(
            account_code='3001-EXTERNAL-WITHDRAWALS',
            name='External Withdrawals',
            account_type=AccountType.EQUITY,
            currency=vault.base_currency,
            is_system=True
        )
        
        entries = [
            {
                'account_id': position.ledger_account_id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': destination_description or 'Withdrawal'
            },
            {
                'account_id': dest_account.id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': f"Withdrawal from vault {vault.name}"
            }
        ]
        
        # Add FX gain/loss entry if applicable
        if realized_fx_gain != 0:
            fx_gain_account, _ = LedgerService.get_or_create_account(
                account_code='6000-FX-REALIZED-GAIN',
                name='Realized FX Gain/Loss',
                account_type=AccountType.INCOME,
                currency=vault.base_currency,
                is_system=True
            )
            
            # Adjust entries for FX gain/loss
            if realized_fx_gain > 0:
                entries.append({
                    'account_id': dest_account.id,
                    'entry_type': 'DEBIT',
                    'amount': float(abs(realized_fx_gain)),
                    'currency': vault.base_currency,
                    'fx_rate': 1.0,
                    'memo': 'Realized FX gain'
                })
                entries.append({
                    'account_id': fx_gain_account.id,
                    'entry_type': 'CREDIT',
                    'amount': float(abs(realized_fx_gain)),
                    'currency': vault.base_currency,
                    'fx_rate': 1.0,
                    'memo': 'Realized FX gain on withdrawal'
                })
            else:
                entries.append({
                    'account_id': fx_gain_account.id,
                    'entry_type': 'DEBIT',
                    'amount': float(abs(realized_fx_gain)),
                    'currency': vault.base_currency,
                    'fx_rate': 1.0,
                    'memo': 'Realized FX loss on withdrawal'
                })
                entries.append({
                    'account_id': dest_account.id,
                    'entry_type': 'CREDIT',
                    'amount': float(abs(realized_fx_gain)),
                    'currency': vault.base_currency,
                    'fx_rate': 1.0,
                    'memo': 'Realized FX loss'
                })
        
        transaction = LedgerService.create_transaction(
            transaction_type=TransactionType.WITHDRAWAL,
            entries=entries,
            description=destination_description or f"Withdrawal from {vault.name}",
            reference_number=reference,
            source_type='vault_withdrawal',
            source_id=vault.id,
            base_currency=vault.base_currency,
            created_by=created_by
        )
        
        # Update realized FX gain tracking
        if realized_fx_gain != 0:
            position.cumulative_realized_fx_gain += realized_fx_gain
            db.session.commit()
        
        new_balance = VaultService.get_position_balance(position)
        
        logger.info(
            f"Withdrawal from vault {vault.vault_id}: {amount} {currency}, "
            f"realized_fx_gain={realized_fx_gain}, new_balance={new_balance}"
        )
        
        return {
            'transaction_id': transaction.transaction_id,
            'amount': float(amount),
            'currency': currency,
            'fx_rate': float(fx_rate),
            'base_amount': float(Decimal(str(amount)) * fx_rate),
            'realized_fx_gain': float(realized_fx_gain),
            'new_balance': float(new_balance),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def transfer_between_vaults(
        source_vault: Vault,
        dest_vault: Vault,
        amount: Decimal,
        currency: str,
        fx_rate: Decimal = None,
        description: str = None,
        created_by: int = None
    ) -> Dict:
        """
        Transfer funds between two vaults.
        """
        # Validate source has sufficient balance
        source_position = VaultCurrencyPosition.query.filter_by(
            vault_id=source_vault.id,
            currency=currency
        ).first()
        
        if not source_position:
            raise ValueError(f"Source vault has no {currency} position")
        
        source_balance = VaultService.get_position_balance(source_position)
        
        if source_balance < amount:
            raise ValueError(f"Insufficient balance in source vault")
        
        # Get or create destination position
        dest_position, _ = VaultService.get_or_create_currency_position(dest_vault, currency)
        
        # Determine FX rate
        base_currency = source_vault.base_currency
        if currency == base_currency:
            fx_rate = Decimal('1')
        elif not fx_rate:
            from backend.services.fx_service import FXService
            fx_rate = FXService.get_rate(currency, base_currency) or Decimal('1')
        
        # Create transfer transaction
        entries = [
            {
                'account_id': source_position.ledger_account_id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': f"Transfer to {dest_vault.name}"
            },
            {
                'account_id': dest_position.ledger_account_id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': f"Transfer from {source_vault.name}"
            }
        ]
        
        transaction = LedgerService.create_transaction(
            transaction_type=TransactionType.TRANSFER,
            entries=entries,
            description=description or f"Transfer from {source_vault.name} to {dest_vault.name}",
            source_type='vault_transfer',
            source_id=source_vault.id,
            base_currency=base_currency,
            created_by=created_by
        )
        
        # Update cost basis for destination
        VaultService._update_cost_basis(dest_position, amount, fx_rate)
        
        db.session.commit()
        
        return {
            'transaction_id': transaction.transaction_id,
            'amount': float(amount),
            'currency': currency,
            'source_vault': source_vault.vault_id,
            'dest_vault': dest_vault.vault_id,
            'source_new_balance': float(VaultService.get_position_balance(source_position)),
            'dest_new_balance': float(VaultService.get_position_balance(dest_position)),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _update_cost_basis(
        position: VaultCurrencyPosition,
        added_amount: Decimal,
        fx_rate: Decimal
    ):
        """
        Update weighted average cost basis for a currency position.
        
        Uses FIFO/weighted average method for cost basis tracking.
        """
        current_balance = VaultService.get_position_balance(position)
        
        # Previous balance before this addition
        prev_balance = current_balance - added_amount
        
        if prev_balance <= 0:
            # First purchase, set cost basis directly
            position.cost_basis_rate = fx_rate
            position.cost_basis_amount = added_amount * fx_rate
        else:
            # Weighted average
            prev_cost = position.cost_basis_amount or (prev_balance * (position.cost_basis_rate or fx_rate))
            new_cost = added_amount * fx_rate
            
            total_cost = prev_cost + new_cost
            total_amount = current_balance
            
            position.cost_basis_rate = total_cost / total_amount if total_amount > 0 else fx_rate
            position.cost_basis_amount = total_cost
        
        position.last_fx_rate = fx_rate
        position.last_revaluation_date = datetime.utcnow()
    
    @staticmethod
    def revalue_positions(
        vault: Vault,
        current_rates: Dict[str, Decimal] = None
    ) -> List[Dict]:
        """
        Revalue all currency positions at current FX rates.
        
        Creates FX valuation snapshots and unrealized gain entries.
        
        Args:
            vault: Vault to revalue
            current_rates: Dict of currency -> base rate (or fetch current)
            
        Returns:
            List of revaluation results
        """
        from backend.services.fx_service import FXService
        
        positions = vault.currency_positions.all()
        results = []
        
        for position in positions:
            if position.currency == vault.base_currency:
                continue
            
            balance = VaultService.get_position_balance(position)
            if balance <= 0:
                continue
            
            # Get current rate
            if current_rates and position.currency in current_rates:
                new_rate = current_rates[position.currency]
            else:
                new_rate = FXService.get_rate(
                    position.currency,
                    vault.base_currency
                ) or Decimal('1')
            
            old_rate = position.last_fx_rate or position.cost_basis_rate or new_rate
            
            if old_rate == new_rate:
                continue
            
            # Calculate delta
            old_value = balance * old_rate
            new_value = balance * new_rate
            delta = new_value - old_value
            
            # Create snapshot
            snapshot = FXValuationSnapshot(
                entity_type='vault_position',
                entity_id=position.id,
                currency=position.currency,
                position_amount=balance,
                original_fx_rate=old_rate,
                current_fx_rate=new_rate,
                base_currency=vault.base_currency,
                original_base_value=old_value,
                current_base_value=new_value,
                unrealized_gain_loss=delta,
                unrealized_gain_loss_pct=(delta / old_value * 100) if old_value > 0 else 0,
                cumulative_realized_gain=position.cumulative_realized_fx_gain,
                cumulative_unrealized_gain=position.cumulative_unrealized_fx_gain + delta
            )
            
            db.session.add(snapshot)
            
            # Update position
            position.last_fx_rate = new_rate
            position.last_revaluation_date = datetime.utcnow()
            position.cumulative_unrealized_fx_gain += delta
            
            results.append({
                'currency': position.currency,
                'balance': float(balance),
                'old_rate': float(old_rate),
                'new_rate': float(new_rate),
                'old_value': float(old_value),
                'new_value': float(new_value),
                'delta': float(delta),
                'delta_pct': float((delta / old_value * 100) if old_value > 0 else 0)
            })
        
        db.session.commit()
        
        logger.info(
            f"Revalued {len(results)} positions in vault {vault.vault_id}"
        )
        
        return results
    
    @staticmethod
    def get_ledger_history(
        vault: Vault,
        currency: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get ledger transaction history for vault.
        """
        if currency:
            position = VaultCurrencyPosition.query.filter_by(
                vault_id=vault.id,
                currency=currency
            ).first()
            
            if not position:
                return []
            
            return LedgerService.get_account_statement(
                position.ledger_account_id,
                start_date,
                end_date,
                limit
            )
        
        # Get all positions
        statements = []
        for position in vault.currency_positions.all():
            stmt = LedgerService.get_account_statement(
                position.ledger_account_id,
                start_date,
                end_date,
                limit
            )
            statements.append({
                'currency': position.currency,
                'statement': stmt
            })
        
        return statements
    
    @staticmethod
    def lock_vault(vault: Vault, reason: str):
        """Lock vault to prevent transactions."""
        vault.is_locked = True
        vault.locked_reason = reason
        db.session.commit()
        logger.info(f"Locked vault {vault.vault_id}: {reason}")
    
    @staticmethod
    def unlock_vault(vault: Vault):
        """Unlock vault."""
        vault.is_locked = False
        vault.locked_reason = None
        db.session.commit()
        logger.info(f"Unlocked vault {vault.vault_id}")
