"""
FX Service: Foreign exchange rate management and real-time delta calculation.

This service handles:
- FX rate storage and retrieval
- Real-time rate updates
- FX delta calculations on asset movement
- Cross-rate computation
- Historical rate lookups
"""

from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
import logging

from backend.extensions import db
from backend.models.ledger import (
    FXRate, FXValuationSnapshot, Vault, VaultCurrencyPosition,
    LedgerAccount, TransactionType
)

logger = logging.getLogger(__name__)


class FXService:
    """Service for managing foreign exchange rates and valuations."""
    
    # Default supported currencies
    SUPPORTED_CURRENCIES = [
        'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
        'CNY', 'INR', 'BRL', 'MXN', 'ZAR', 'SGD', 'HKD', 'KRW'
    ]
    
    # Rate precision
    RATE_PRECISION = Decimal('0.00000001')
    
    @staticmethod
    def store_rate(
        from_currency: str,
        to_currency: str,
        rate: Decimal,
        rate_date: date = None,
        source: str = None,
        mark_current: bool = True
    ) -> FXRate:
        """
        Store an FX rate.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            rate: Exchange rate (1 from_currency = rate to_currency)
            rate_date: Date of rate (defaults to today)
            source: Source of rate (ECB, Reuters, etc.)
            mark_current: Mark as current rate
            
        Returns:
            Created/updated FXRate instance
        """
        rate_date = rate_date or date.today()
        
        # Check for existing rate
        existing = FXRate.query.filter_by(
            from_currency=from_currency,
            to_currency=to_currency,
            rate_date=rate_date
        ).first()
        
        if existing:
            existing.rate = rate
            existing.source = source
            existing.rate_time = datetime.utcnow()
            fx_rate = existing
        else:
            fx_rate = FXRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=rate,
                rate_date=rate_date,
                source=source
            )
            db.session.add(fx_rate)
        
        if mark_current:
            # Unmark other current rates for this pair
            FXRate.query.filter_by(
                from_currency=from_currency,
                to_currency=to_currency,
                is_current=True
            ).update({'is_current': False})
            
            fx_rate.is_current = True
        
        db.session.commit()
        
        logger.info(
            f"Stored FX rate: {from_currency}/{to_currency} = {rate} "
            f"({rate_date}, source={source})"
        )
        
        return fx_rate
    
    @staticmethod
    def store_rates_batch(rates: List[Dict]) -> int:
        """
        Store multiple FX rates in batch.
        
        Args:
            rates: List of dicts with from_currency, to_currency, rate, etc.
            
        Returns:
            Number of rates stored
        """
        count = 0
        for rate_data in rates:
            try:
                FXService.store_rate(
                    from_currency=rate_data['from_currency'],
                    to_currency=rate_data['to_currency'],
                    rate=Decimal(str(rate_data['rate'])),
                    rate_date=rate_data.get('rate_date'),
                    source=rate_data.get('source'),
                    mark_current=rate_data.get('mark_current', True)
                )
                count += 1
            except Exception as e:
                logger.error(f"Failed to store rate {rate_data}: {e}")
        
        return count
    
    @staticmethod
    def get_rate(
        from_currency: str,
        to_currency: str,
        rate_date: date = None
    ) -> Optional[Decimal]:
        """
        Get FX rate for currency pair.
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            rate_date: Specific date (defaults to current)
            
        Returns:
            Exchange rate or None
        """
        if from_currency == to_currency:
            return Decimal('1')
        
        if rate_date:
            fx_rate = FXRate.query.filter_by(
                from_currency=from_currency,
                to_currency=to_currency,
                rate_date=rate_date
            ).first()
        else:
            fx_rate = FXRate.query.filter_by(
                from_currency=from_currency,
                to_currency=to_currency,
                is_current=True
            ).first()
        
        if fx_rate:
            return Decimal(str(fx_rate.rate))
        
        # Try inverse
        inverse = FXService._get_inverse_rate(from_currency, to_currency, rate_date)
        if inverse:
            return inverse
        
        # Try cross rate through USD if not direct
        if from_currency != 'USD' and to_currency != 'USD':
            cross = FXService._get_cross_rate(from_currency, to_currency, rate_date)
            if cross:
                return cross
        
        return None
    
    @staticmethod
    def _get_inverse_rate(
        from_currency: str,
        to_currency: str,
        rate_date: date = None
    ) -> Optional[Decimal]:
        """Calculate rate from inverse pair."""
        if rate_date:
            inverse = FXRate.query.filter_by(
                from_currency=to_currency,
                to_currency=from_currency,
                rate_date=rate_date
            ).first()
        else:
            inverse = FXRate.query.filter_by(
                from_currency=to_currency,
                to_currency=from_currency,
                is_current=True
            ).first()
        
        if inverse and inverse.rate > 0:
            return (Decimal('1') / Decimal(str(inverse.rate))).quantize(
                FXService.RATE_PRECISION, rounding=ROUND_HALF_UP
            )
        
        return None
    
    @staticmethod
    def _get_cross_rate(
        from_currency: str,
        to_currency: str,
        rate_date: date = None
    ) -> Optional[Decimal]:
        """Calculate cross rate through USD."""
        from_usd = FXService.get_rate(from_currency, 'USD', rate_date)
        usd_to = FXService.get_rate('USD', to_currency, rate_date)
        
        if from_usd and usd_to:
            return (from_usd * usd_to).quantize(
                FXService.RATE_PRECISION, rounding=ROUND_HALF_UP
            )
        
        return None
    
    @staticmethod
    def get_all_current_rates(base_currency: str = 'USD') -> Dict[str, Decimal]:
        """
        Get all current rates against a base currency.
        
        Returns:
            Dict of currency -> rate
        """
        rates = {}
        
        for currency in FXService.SUPPORTED_CURRENCIES:
            if currency == base_currency:
                rates[currency] = Decimal('1')
            else:
                rate = FXService.get_rate(currency, base_currency)
                if rate:
                    rates[currency] = rate
        
        return rates
    
    @staticmethod
    def get_rate_history(
        from_currency: str,
        to_currency: str,
        start_date: date,
        end_date: date = None
    ) -> List[Dict]:
        """
        Get historical rates for a currency pair.
        """
        end_date = end_date or date.today()
        
        rates = FXRate.query.filter(
            FXRate.from_currency == from_currency,
            FXRate.to_currency == to_currency,
            FXRate.rate_date >= start_date,
            FXRate.rate_date <= end_date
        ).order_by(FXRate.rate_date).all()
        
        return [r.to_dict() for r in rates]
    
    @staticmethod
    def calculate_fx_delta(
        amount: Decimal,
        original_rate: Decimal,
        current_rate: Decimal,
        base_currency: str = 'USD'
    ) -> Dict:
        """
        Calculate FX gain/loss delta for a position.
        
        Args:
            amount: Amount in foreign currency
            original_rate: Rate when position was acquired
            current_rate: Current rate
            base_currency: Base currency for reporting
            
        Returns:
            Dict with delta calculations
        """
        original_value = amount * original_rate
        current_value = amount * current_rate
        delta = current_value - original_value
        
        delta_pct = Decimal('0')
        if original_value > 0:
            delta_pct = (delta / original_value * 100).quantize(
                Decimal('0.0001'), rounding=ROUND_HALF_UP
            )
        
        return {
            'amount': float(amount),
            'original_rate': float(original_rate),
            'current_rate': float(current_rate),
            'original_value': float(original_value),
            'current_value': float(current_value),
            'delta': float(delta),
            'delta_pct': float(delta_pct),
            'base_currency': base_currency,
            'is_gain': delta > 0
        }
    
    @staticmethod
    def calculate_movement_fx_delta(
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        acquisition_rate: Decimal,
        movement_rate: Decimal
    ) -> Dict:
        """
        Calculate FX delta when moving assets.
        
        This is called when funds move between currencies or vaults
        to calculate realized FX gain/loss.
        
        Args:
            amount: Amount being moved
            from_currency: Source currency
            to_currency: Target currency
            acquisition_rate: Rate when originally acquired
            movement_rate: Rate at time of movement
            
        Returns:
            Dict with realized gain/loss details
        """
        if from_currency == to_currency:
            return {
                'amount': float(amount),
                'realized_gain_loss': 0,
                'from_currency': from_currency,
                'to_currency': to_currency
            }
        
        # Value at acquisition
        original_value = amount * acquisition_rate
        
        # Value at movement
        movement_value = amount * movement_rate
        
        # Realized gain/loss
        realized = movement_value - original_value
        
        return {
            'amount': float(amount),
            'from_currency': from_currency,
            'to_currency': to_currency,
            'acquisition_rate': float(acquisition_rate),
            'movement_rate': float(movement_rate),
            'original_value': float(original_value),
            'movement_value': float(movement_value),
            'realized_gain_loss': float(realized),
            'is_gain': realized > 0
        }
    
    @staticmethod
    def revalue_all_positions(
        base_currency: str = 'USD',
        current_rates: Dict[str, Decimal] = None
    ) -> Dict:
        """
        Revalue all multi-currency positions across all vaults.
        
        Triggers recursive ledger revaluation when rates shift.
        
        Args:
            base_currency: Base currency for reporting
            current_rates: Current rates (or fetch fresh)
            
        Returns:
            Summary of revaluations
        """
        from backend.services.vault_service import VaultService
        
        # Get current rates if not provided
        if not current_rates:
            current_rates = FXService.get_all_current_rates(base_currency)
        
        # Find all vaults with auto-revaluation enabled
        vaults = Vault.query.filter_by(
            auto_fx_revaluation=True,
            is_active=True
        ).all()
        
        results = {
            'vaults_processed': 0,
            'positions_revalued': 0,
            'total_unrealized_gain': Decimal('0'),
            'vault_details': []
        }
        
        for vault in vaults:
            try:
                revaluations = VaultService.revalue_positions(vault, current_rates)
                
                vault_gain = sum(r['delta'] for r in revaluations)
                
                results['vaults_processed'] += 1
                results['positions_revalued'] += len(revaluations)
                results['total_unrealized_gain'] += Decimal(str(vault_gain))
                
                if revaluations:
                    results['vault_details'].append({
                        'vault_id': vault.vault_id,
                        'vault_name': vault.name,
                        'positions_revalued': len(revaluations),
                        'total_delta': vault_gain,
                        'revaluations': revaluations
                    })
            except Exception as e:
                logger.error(f"Failed to revalue vault {vault.vault_id}: {e}")
        
        results['total_unrealized_gain'] = float(results['total_unrealized_gain'])
        
        logger.info(
            f"Revalued {results['positions_revalued']} positions across "
            f"{results['vaults_processed']} vaults, total delta={results['total_unrealized_gain']}"
        )
        
        return results
    
    @staticmethod
    def get_fx_exposure_report(
        entity_type: str = None,
        entity_id: int = None,
        base_currency: str = 'USD'
    ) -> Dict:
        """
        Generate FX exposure report.
        
        Shows currency positions and potential gain/loss at different rate scenarios.
        """
        query = VaultCurrencyPosition.query
        
        if entity_type and entity_id:
            query = query.join(Vault).filter(
                Vault.owner_type == entity_type,
                Vault.owner_id == entity_id
            )
        
        positions = query.all()
        
        current_rates = FXService.get_all_current_rates(base_currency)
        
        exposure = {
            'base_currency': base_currency,
            'positions': [],
            'total_exposure': Decimal('0'),
            'currency_breakdown': {}
        }
        
        for position in positions:
            from backend.services.vault_service import VaultService
            
            balance = VaultService.get_position_balance(position)
            if balance <= 0:
                continue
            
            currency = position.currency
            rate = current_rates.get(currency, Decimal('1'))
            base_value = balance * rate
            
            # Scenario analysis
            scenarios = FXService._calculate_rate_scenarios(
                balance, rate, base_currency
            )
            
            position_data = {
                'vault_id': position.vault.vault_id if position.vault else None,
                'currency': currency,
                'balance': float(balance),
                'current_rate': float(rate),
                'base_value': float(base_value),
                'cost_basis_rate': float(position.cost_basis_rate) if position.cost_basis_rate else None,
                'unrealized_gain': float(position.cumulative_unrealized_fx_gain),
                'scenarios': scenarios
            }
            
            exposure['positions'].append(position_data)
            exposure['total_exposure'] += base_value
            
            if currency not in exposure['currency_breakdown']:
                exposure['currency_breakdown'][currency] = {
                    'total_balance': Decimal('0'),
                    'total_base_value': Decimal('0')
                }
            
            exposure['currency_breakdown'][currency]['total_balance'] += balance
            exposure['currency_breakdown'][currency]['total_base_value'] += base_value
        
        exposure['total_exposure'] = float(exposure['total_exposure'])
        
        # Convert currency breakdown to serializable format
        for currency in exposure['currency_breakdown']:
            exposure['currency_breakdown'][currency] = {
                'total_balance': float(exposure['currency_breakdown'][currency]['total_balance']),
                'total_base_value': float(exposure['currency_breakdown'][currency]['total_base_value'])
            }
        
        return exposure
    
    @staticmethod
    def _calculate_rate_scenarios(
        amount: Decimal,
        current_rate: Decimal,
        base_currency: str
    ) -> List[Dict]:
        """Calculate value at different rate scenarios."""
        scenarios = []
        
        # -10%, -5%, current, +5%, +10%
        for pct_change in [-10, -5, 0, 5, 10]:
            rate_multiplier = Decimal('1') + (Decimal(str(pct_change)) / 100)
            scenario_rate = current_rate * rate_multiplier
            scenario_value = amount * scenario_rate
            change = scenario_value - (amount * current_rate)
            
            scenarios.append({
                'rate_change_pct': pct_change,
                'scenario_rate': float(scenario_rate),
                'scenario_value': float(scenario_value),
                'value_change': float(change)
            })
        
        return scenarios
    
    @staticmethod
    def create_fx_snapshot(
        entity_type: str,
        entity_id: int,
        currency: str,
        position_amount: Decimal,
        original_rate: Decimal,
        current_rate: Decimal,
        base_currency: str = 'USD'
    ) -> FXValuationSnapshot:
        """
        Create an FX valuation snapshot for audit purposes.
        """
        original_value = position_amount * original_rate
        current_value = position_amount * current_rate
        unrealized = current_value - original_value
        
        unrealized_pct = Decimal('0')
        if original_value > 0:
            unrealized_pct = (unrealized / original_value * 100).quantize(
                Decimal('0.0001'), rounding=ROUND_HALF_UP
            )
        
        snapshot = FXValuationSnapshot(
            entity_type=entity_type,
            entity_id=entity_id,
            currency=currency,
            position_amount=position_amount,
            original_fx_rate=original_rate,
            current_fx_rate=current_rate,
            base_currency=base_currency,
            original_base_value=original_value,
            current_base_value=current_value,
            unrealized_gain_loss=unrealized,
            unrealized_gain_loss_pct=unrealized_pct
        )
        
        db.session.add(snapshot)
        db.session.commit()
        
        return snapshot
    
    @staticmethod
    def get_valuation_history(
        entity_type: str,
        entity_id: int,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get FX valuation history for an entity."""
        query = FXValuationSnapshot.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        if start_date:
            query = query.filter(FXValuationSnapshot.snapshot_date >= start_date)
        if end_date:
            query = query.filter(FXValuationSnapshot.snapshot_date <= end_date)
        
        snapshots = query.order_by(
            FXValuationSnapshot.snapshot_date.desc()
        ).limit(limit).all()
        
        return [s.to_dict() for s in snapshots]
