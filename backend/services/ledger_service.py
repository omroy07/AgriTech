"""
Ledger Service: Core double-entry accounting logic.

This service handles:
- Creating balanced ledger transactions
- Double-entry validation
- Account balance reconstruction
- Transaction reversal
- Ledger auditing and reporting
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Tuple
import uuid
import logging

from backend.extensions import db
from backend.models.ledger import (
    LedgerAccount, LedgerTransaction, LedgerEntry,
    AccountType, EntryType, TransactionType, FXRate
)

logger = logging.getLogger(__name__)


class LedgerService:
    """Service for managing double-entry ledger transactions."""
    
    # Precision for financial calculations
    PRECISION = Decimal('0.000001')
    DISPLAY_PRECISION = Decimal('0.01')
    
    @staticmethod
    def create_account(
        account_code: str,
        name: str,
        account_type: AccountType,
        currency: str = 'USD',
        parent_id: int = None,
        entity_type: str = None,
        entity_id: int = None,
        description: str = None,
        is_system: bool = False
    ) -> LedgerAccount:
        """
        Create a new ledger account.
        
        Args:
            account_code: Unique account identifier (e.g., '1000-CASH-USD')
            name: Human-readable account name
            account_type: Type of account (ASSET, LIABILITY, etc.)
            currency: Primary currency for this account
            parent_id: Optional parent account for hierarchy
            entity_type: Type of entity this account belongs to
            entity_id: ID of the associated entity
            description: Optional account description
            is_system: If True, account cannot be deleted
            
        Returns:
            Created LedgerAccount instance
        """
        account = LedgerAccount(
            account_code=account_code,
            name=name,
            account_type=account_type,
            currency=currency,
            parent_id=parent_id,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            is_system=is_system
        )
        
        db.session.add(account)
        db.session.commit()
        
        logger.info(f"Created ledger account: {account_code} ({name})")
        return account
    
    @staticmethod
    def get_or_create_account(
        account_code: str,
        name: str,
        account_type: AccountType,
        **kwargs
    ) -> Tuple[LedgerAccount, bool]:
        """
        Get existing account or create new one.
        
        Returns:
            Tuple of (account, created) where created is True if new
        """
        account = LedgerAccount.query.filter_by(account_code=account_code).first()
        
        if account:
            return account, False
        
        account = LedgerService.create_account(
            account_code=account_code,
            name=name,
            account_type=account_type,
            **kwargs
        )
        return account, True
    
    @staticmethod
    def create_transaction(
        transaction_type: TransactionType,
        entries: List[Dict],
        description: str = None,
        reference_number: str = None,
        source_type: str = None,
        source_id: int = None,
        base_currency: str = 'USD',
        created_by: int = None,
        entry_date: datetime = None
    ) -> LedgerTransaction:
        """
        Create a balanced double-entry transaction.
        
        Args:
            transaction_type: Type of transaction
            entries: List of entry dicts with:
                - account_id: Target account ID
                - entry_type: 'DEBIT' or 'CREDIT'
                - amount: Amount in account currency
                - currency: Currency of amount
                - fx_rate: Optional FX rate to base currency
                - memo: Optional entry memo
            description: Transaction description
            reference_number: External reference (invoice, etc.)
            source_type: Type of source operation
            source_id: ID of source operation
            base_currency: Base currency for reporting
            created_by: User ID who created transaction
            entry_date: Date for entries (defaults to now)
            
        Returns:
            Created LedgerTransaction
            
        Raises:
            ValueError: If transaction is not balanced
        """
        if not entries or len(entries) < 2:
            raise ValueError("Transaction requires at least 2 entries (debit and credit)")
        
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Calculate total base amount
        total_debit_base = Decimal('0')
        total_credit_base = Decimal('0')
        
        entry_date = entry_date or datetime.utcnow()
        
        # Validate and prepare entries
        prepared_entries = []
        for entry_data in entries:
            amount = Decimal(str(entry_data['amount']))
            currency = entry_data.get('currency', base_currency)
            fx_rate = Decimal(str(entry_data.get('fx_rate', 1.0)))
            
            # Calculate base amount
            if currency == base_currency:
                base_amount = amount
            else:
                base_amount = (amount * fx_rate).quantize(
                    LedgerService.PRECISION, rounding=ROUND_HALF_UP
                )
            
            entry_type = entry_data['entry_type']
            if isinstance(entry_type, str):
                entry_type = EntryType[entry_type]
            
            if entry_type == EntryType.DEBIT:
                total_debit_base += base_amount
            else:
                total_credit_base += base_amount
            
            prepared_entries.append({
                'account_id': entry_data['account_id'],
                'entry_type': entry_type,
                'amount': amount,
                'currency': currency,
                'base_amount': base_amount,
                'base_currency': base_currency,
                'fx_rate': fx_rate,
                'memo': entry_data.get('memo'),
                'metadata_json': entry_data.get('metadata'),
                'entry_date': entry_date
            })
        
        # Validate balance (allow small rounding difference)
        if abs(total_debit_base - total_credit_base) > LedgerService.DISPLAY_PRECISION:
            raise ValueError(
                f"Transaction not balanced: Debits={total_debit_base}, "
                f"Credits={total_credit_base}, Diff={total_debit_base - total_credit_base}"
            )
        
        # Create transaction
        transaction = LedgerTransaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            source_type=source_type,
            source_id=source_id,
            description=description,
            reference_number=reference_number,
            base_currency=base_currency,
            base_amount=total_debit_base,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        
        db.session.add(transaction)
        db.session.flush()  # Get transaction ID
        
        # Create entries
        for entry_data in prepared_entries:
            entry = LedgerEntry(
                transaction_id=transaction.id,
                **entry_data
            )
            db.session.add(entry)
        
        db.session.commit()
        
        logger.info(
            f"Created ledger transaction {transaction_id}: {transaction_type.value} "
            f"with {len(entries)} entries, base_amount={total_debit_base}"
        )
        
        return transaction
    
    @staticmethod
    def get_account_balance(
        account_id: int,
        as_of_date: datetime = None,
        include_children: bool = False
    ) -> Decimal:
        """
        Calculate account balance from ledger entries.
        
        Args:
            account_id: Account to calculate balance for
            as_of_date: Optional cutoff date
            include_children: If True, include child account balances
            
        Returns:
            Account balance as Decimal
        """
        account = LedgerAccount.query.get(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        balance = account.get_balance(as_of_date)
        
        if include_children:
            for child in account.children:
                balance += LedgerService.get_account_balance(
                    child.id, as_of_date, include_children=True
                )
        
        return balance
    
    @staticmethod
    def get_account_statement(
        account_id: int,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> Dict:
        """
        Get account statement with transaction history.
        
        Returns:
            Dict with balance and transaction list
        """
        account = LedgerAccount.query.get(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        query = LedgerEntry.query.filter_by(account_id=account_id)
        
        if start_date:
            query = query.filter(LedgerEntry.entry_date >= start_date)
        if end_date:
            query = query.filter(LedgerEntry.entry_date <= end_date)
        
        entries = query.order_by(LedgerEntry.entry_date.desc()).limit(limit).all()
        
        # Calculate opening balance
        opening_balance = Decimal('0')
        if start_date:
            opening_balance = account.get_balance(start_date)
        
        # Build running balance
        running_balance = opening_balance
        statement_entries = []
        
        # Process entries in chronological order for running balance
        for entry in reversed(entries):
            if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                if entry.entry_type == EntryType.DEBIT:
                    running_balance += entry.amount
                else:
                    running_balance -= entry.amount
            else:
                if entry.entry_type == EntryType.CREDIT:
                    running_balance += entry.amount
                else:
                    running_balance -= entry.amount
            
            statement_entries.append({
                **entry.to_dict(),
                'running_balance': float(running_balance)
            })
        
        return {
            'account': account.to_dict(),
            'opening_balance': float(opening_balance),
            'closing_balance': float(running_balance),
            'entries': list(reversed(statement_entries)),
            'entry_count': len(statement_entries)
        }
    
    @staticmethod
    def reverse_transaction(
        transaction_id: int,
        reason: str = None,
        reversed_by: int = None
    ) -> LedgerTransaction:
        """
        Create a reversal transaction that negates the original.
        
        Args:
            transaction_id: ID of transaction to reverse
            reason: Reason for reversal
            reversed_by: User ID performing reversal
            
        Returns:
            New reversal transaction
        """
        original = LedgerTransaction.query.get(transaction_id)
        if not original:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        if original.is_reversed:
            raise ValueError(f"Transaction {transaction_id} is already reversed")
        
        # Create reversal entries (swap debits and credits)
        reversal_entries = []
        for entry in original.entries.all():
            reversal_entries.append({
                'account_id': entry.account_id,
                'entry_type': EntryType.CREDIT if entry.entry_type == EntryType.DEBIT else EntryType.DEBIT,
                'amount': float(entry.amount),
                'currency': entry.currency,
                'fx_rate': float(entry.fx_rate) if entry.fx_rate else 1.0,
                'memo': f"Reversal: {entry.memo or ''}"
            })
        
        # Create reversal transaction
        reversal = LedgerService.create_transaction(
            transaction_type=original.transaction_type,
            entries=reversal_entries,
            description=f"REVERSAL of {original.transaction_id}: {reason or 'No reason provided'}",
            reference_number=f"REV-{original.reference_number or original.transaction_id}",
            source_type='reversal',
            source_id=original.id,
            base_currency=original.base_currency,
            created_by=reversed_by
        )
        
        # Mark original as reversed
        original.is_reversed = True
        original.reversed_by_id = reversal.id
        db.session.commit()
        
        logger.info(f"Reversed transaction {original.transaction_id} with {reversal.transaction_id}")
        
        return reversal
    
    @staticmethod
    def record_transfer(
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        currency: str,
        description: str = None,
        fx_rate: Decimal = None,
        base_currency: str = 'USD',
        created_by: int = None
    ) -> LedgerTransaction:
        """
        Record a transfer between two accounts.
        
        This creates a balanced transaction with:
        - Credit to source account
        - Debit to destination account
        """
        from_account = LedgerAccount.query.get(from_account_id)
        to_account = LedgerAccount.query.get(to_account_id)
        
        if not from_account or not to_account:
            raise ValueError("Invalid account IDs")
        
        fx_rate = fx_rate or Decimal('1.0')
        
        entries = [
            {
                'account_id': from_account_id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': f"Transfer to {to_account.name}"
            },
            {
                'account_id': to_account_id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate),
                'memo': f"Transfer from {from_account.name}"
            }
        ]
        
        return LedgerService.create_transaction(
            transaction_type=TransactionType.TRANSFER,
            entries=entries,
            description=description or f"Transfer from {from_account.name} to {to_account.name}",
            base_currency=base_currency,
            created_by=created_by
        )
    
    @staticmethod
    def record_fx_revaluation(
        account_id: int,
        new_fx_rate: Decimal,
        old_fx_rate: Decimal,
        base_currency: str = 'USD',
        fx_gain_account_id: int = None,
        created_by: int = None
    ) -> Optional[LedgerTransaction]:
        """
        Record FX revaluation gain/loss for a currency position.
        
        Args:
            account_id: Account holding foreign currency
            new_fx_rate: New FX rate
            old_fx_rate: Previous FX rate
            base_currency: Base currency for reporting
            fx_gain_account_id: Account for FX gains/losses
            created_by: User ID
            
        Returns:
            Revaluation transaction or None if no change
        """
        account = LedgerAccount.query.get(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Get current balance in account currency
        balance = account.get_balance()
        
        if balance == 0:
            return None
        
        # Calculate revaluation amount
        old_base_value = balance * old_fx_rate
        new_base_value = balance * new_fx_rate
        fx_delta = new_base_value - old_base_value
        
        if abs(fx_delta) < LedgerService.DISPLAY_PRECISION:
            return None
        
        # Get or create FX gain/loss account
        if not fx_gain_account_id:
            fx_account, _ = LedgerService.get_or_create_account(
                account_code='6000-FX-GAIN-LOSS',
                name='FX Gain/Loss',
                account_type=AccountType.INCOME if fx_delta > 0 else AccountType.EXPENSE,
                currency=base_currency,
                is_system=True
            )
            fx_gain_account_id = fx_account.id
        
        # Create revaluation entries
        if fx_delta > 0:
            # Gain: Debit asset, Credit income
            entries = [
                {
                    'account_id': account_id,
                    'entry_type': 'DEBIT',
                    'amount': float(abs(fx_delta)),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': f"FX revaluation gain: {old_fx_rate} -> {new_fx_rate}"
                },
                {
                    'account_id': fx_gain_account_id,
                    'entry_type': 'CREDIT',
                    'amount': float(abs(fx_delta)),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': f"FX revaluation gain on {account.name}"
                }
            ]
        else:
            # Loss: Credit asset, Debit expense
            entries = [
                {
                    'account_id': account_id,
                    'entry_type': 'CREDIT',
                    'amount': float(abs(fx_delta)),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': f"FX revaluation loss: {old_fx_rate} -> {new_fx_rate}"
                },
                {
                    'account_id': fx_gain_account_id,
                    'entry_type': 'DEBIT',
                    'amount': float(abs(fx_delta)),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': f"FX revaluation loss on {account.name}"
                }
            ]
        
        transaction = LedgerService.create_transaction(
            transaction_type=TransactionType.FX_REVALUATION,
            entries=entries,
            description=f"FX revaluation for {account.name}: rate {old_fx_rate} -> {new_fx_rate}",
            base_currency=base_currency,
            created_by=created_by
        )
        
        logger.info(
            f"Recorded FX revaluation for account {account_id}: "
            f"delta={fx_delta}, old_rate={old_fx_rate}, new_rate={new_fx_rate}"
        )
        
        return transaction
    
    @staticmethod
    def get_trial_balance(
        entity_type: str = None,
        entity_id: int = None,
        as_of_date: datetime = None
    ) -> Dict:
        """
        Generate trial balance report.
        
        Returns:
            Dict with account balances grouped by type
        """
        query = LedgerAccount.query.filter_by(is_active=True)
        
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
        
        accounts = query.all()
        
        trial_balance = {
            'assets': [],
            'liabilities': [],
            'equity': [],
            'income': [],
            'expenses': [],
            'totals': {
                'total_debits': Decimal('0'),
                'total_credits': Decimal('0')
            }
        }
        
        for account in accounts:
            balance = account.get_balance(as_of_date)
            
            entry = {
                'account_code': account.account_code,
                'account_name': account.name,
                'currency': account.currency,
                'balance': float(balance),
                'debit': float(balance) if balance > 0 else 0,
                'credit': float(abs(balance)) if balance < 0 else 0
            }
            
            category = account.account_type.value.lower() + 's'
            if category == 'expensess':
                category = 'expenses'
            
            if category in trial_balance:
                trial_balance[category].append(entry)
            
            if balance > 0:
                trial_balance['totals']['total_debits'] += balance
            else:
                trial_balance['totals']['total_credits'] += abs(balance)
        
        trial_balance['totals']['total_debits'] = float(trial_balance['totals']['total_debits'])
        trial_balance['totals']['total_credits'] = float(trial_balance['totals']['total_credits'])
        trial_balance['totals']['is_balanced'] = (
            trial_balance['totals']['total_debits'] == trial_balance['totals']['total_credits']
        )
        
        return trial_balance
    
    @staticmethod
    def audit_transaction(transaction_id: int) -> Dict:
        """
        Full audit of a transaction including balance impact.
        
        Returns:
            Detailed audit information
        """
        transaction = LedgerTransaction.query.get(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        entries = transaction.entries.all()
        
        audit_result = {
            'transaction': transaction.to_dict(include_entries=True),
            'is_balanced': transaction.is_balanced(),
            'entry_count': len(entries),
            'account_impacts': []
        }
        
        for entry in entries:
            account = entry.account
            balance_before = account.get_balance(entry.entry_date) - (
                entry.amount if entry.entry_type == EntryType.DEBIT else -entry.amount
            )
            balance_after = account.get_balance(entry.entry_date)
            
            audit_result['account_impacts'].append({
                'account_code': account.account_code,
                'account_name': account.name,
                'entry_type': entry.entry_type.value,
                'amount': float(entry.amount),
                'currency': entry.currency,
                'balance_before': float(balance_before),
                'balance_after': float(balance_after)
            })
        
        return audit_result
    
    @staticmethod
    def get_ledger_summary(
        entity_type: str = None,
        entity_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Get summary statistics for ledger.
        """
        from sqlalchemy import func
        
        txn_query = LedgerTransaction.query
        
        if source_type := entity_type:
            txn_query = txn_query.filter_by(source_type=source_type)
        
        if start_date:
            txn_query = txn_query.filter(LedgerTransaction.created_at >= start_date)
        if end_date:
            txn_query = txn_query.filter(LedgerTransaction.created_at <= end_date)
        
        transaction_count = txn_query.count()
        
        volume = txn_query.with_entities(
            func.coalesce(func.sum(LedgerTransaction.base_amount), 0)
        ).scalar() or 0
        
        # Get transaction type breakdown
        type_breakdown = txn_query.with_entities(
            LedgerTransaction.transaction_type,
            func.count(LedgerTransaction.id),
            func.sum(LedgerTransaction.base_amount)
        ).group_by(LedgerTransaction.transaction_type).all()
        
        return {
            'transaction_count': transaction_count,
            'total_volume': float(volume),
            'type_breakdown': [
                {
                    'type': t[0].value,
                    'count': t[1],
                    'volume': float(t[2] or 0)
                }
                for t in type_breakdown
            ],
            'period': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            }
        }
