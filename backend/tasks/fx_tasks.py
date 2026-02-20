"""
FX Rate Sync Tasks: Background jobs for FX rate syncing and ledger revaluation.

This module provides:
- Scheduled FX rate fetching from external APIs
- Recursive ledger revaluation when rates shift
- Rate monitoring and alerting
- Historical rate backfill
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List
import logging
import requests

from backend.celery_app import celery
from backend.extensions import db
from backend.services.fx_service import FXService
from backend.services.vault_service import VaultService
from backend.models.ledger import Vault, VaultCurrencyPosition, FXRate

logger = logging.getLogger(__name__)


# FX API Configuration (example using exchangerate-api.com)
FX_API_BASE_URL = "https://api.exchangerate-api.com/v4/latest"
FX_API_BACKUP_URL = "https://open.er-api.com/v6/latest"


@celery.task(name='fx.sync_rates')
def sync_fx_rates_task(base_currency: str = 'USD') -> Dict:
    """
    Fetch current FX rates from external API and store them.
    
    This task should run on a schedule (e.g., every hour or at market open).
    """
    logger.info(f"Starting FX rate sync for base currency: {base_currency}")
    
    rates_fetched = 0
    errors = []
    
    try:
        # Try primary API
        rates = _fetch_rates_from_api(base_currency)
        
        if not rates:
            # Try backup API
            rates = _fetch_rates_from_backup_api(base_currency)
        
        if not rates:
            raise Exception("Failed to fetch rates from all APIs")
        
        # Store rates
        for currency, rate in rates.items():
            try:
                FXService.store_rate(
                    from_currency=currency,
                    to_currency=base_currency,
                    rate=Decimal(str(rate)),
                    rate_date=date.today(),
                    source='api_sync',
                    mark_current=True
                )
                rates_fetched += 1
            except Exception as e:
                errors.append(f"{currency}: {str(e)}")
        
        logger.info(f"FX rate sync completed: {rates_fetched} rates updated")
        
        # Trigger revaluation if rates have changed significantly
        if rates_fetched > 0:
            trigger_ledger_revaluation_task.delay()
        
        return {
            'status': 'success',
            'rates_fetched': rates_fetched,
            'base_currency': base_currency,
            'errors': errors,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"FX rate sync failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'rates_fetched': rates_fetched,
            'timestamp': datetime.utcnow().isoformat()
        }


def _fetch_rates_from_api(base_currency: str) -> Dict[str, float]:
    """Fetch rates from primary API."""
    try:
        response = requests.get(
            f"{FX_API_BASE_URL}/{base_currency}",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('rates', {})
        
        logger.warning(f"Primary FX API returned {response.status_code}")
        return {}
        
    except Exception as e:
        logger.error(f"Primary FX API error: {str(e)}")
        return {}


def _fetch_rates_from_backup_api(base_currency: str) -> Dict[str, float]:
    """Fetch rates from backup API."""
    try:
        response = requests.get(
            f"{FX_API_BACKUP_URL}/{base_currency}",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('rates', {})
        
        logger.warning(f"Backup FX API returned {response.status_code}")
        return {}
        
    except Exception as e:
        logger.error(f"Backup FX API error: {str(e)}")
        return {}


@celery.task(name='fx.trigger_revaluation')
def trigger_ledger_revaluation_task() -> Dict:
    """
    Trigger recursive ledger revaluation across all vaults when rates shift.
    
    This task:
    1. Identifies all vaults with multi-currency positions
    2. Compares current rates with last revaluation rates
    3. Creates revaluation entries for positions with material changes
    4. Records FX valuation snapshots
    """
    logger.info("Starting ledger revaluation")
    
    try:
        # Get current rates
        current_rates = FXService.get_all_current_rates('USD')
        
        # Perform revaluation
        result = FXService.revalue_all_positions(
            base_currency='USD',
            current_rates=current_rates
        )
        
        logger.info(
            f"Ledger revaluation completed: "
            f"{result['vaults_processed']} vaults, "
            f"{result['positions_revalued']} positions, "
            f"total delta={result['total_unrealized_gain']}"
        )
        
        return {
            'status': 'success',
            **result,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ledger revaluation failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }


@celery.task(name='fx.revalue_vault')
def revalue_vault_task(vault_id: str) -> Dict:
    """
    Revalue a specific vault's positions.
    """
    logger.info(f"Revaluing vault: {vault_id}")
    
    try:
        vault = VaultService.get_vault(vault_id)
        
        if not vault:
            return {
                'status': 'error',
                'error': f'Vault {vault_id} not found'
            }
        
        results = VaultService.revalue_positions(vault)
        
        return {
            'status': 'success',
            'vault_id': vault_id,
            'revaluations': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vault revaluation failed: {str(e)}")
        return {
            'status': 'error',
            'vault_id': vault_id,
            'error': str(e)
        }


@celery.task(name='fx.detect_rate_shifts')
def detect_significant_rate_shifts_task(
    threshold_pct: float = 1.0
) -> Dict:
    """
    Detect significant FX rate shifts and trigger alerts/revaluations.
    
    Args:
        threshold_pct: Minimum percentage change to trigger action
        
    This monitors for large rate movements that may require
    immediate position revaluation or risk alerts.
    """
    logger.info(f"Detecting rate shifts > {threshold_pct}%")
    
    significant_shifts = []
    
    try:
        # Get yesterday's rates
        yesterday = date.today() - timedelta(days=1)
        
        for currency in FXService.SUPPORTED_CURRENCIES:
            if currency == 'USD':
                continue
            
            current_rate = FXService.get_rate(currency, 'USD')
            yesterday_rate = FXService.get_rate(currency, 'USD', yesterday)
            
            if not current_rate or not yesterday_rate:
                continue
            
            # Calculate change
            change_pct = abs(
                (float(current_rate) - float(yesterday_rate)) / float(yesterday_rate) * 100
            )
            
            if change_pct >= threshold_pct:
                significant_shifts.append({
                    'currency': currency,
                    'yesterday_rate': float(yesterday_rate),
                    'current_rate': float(current_rate),
                    'change_pct': round(change_pct, 4),
                    'direction': 'up' if current_rate > yesterday_rate else 'down'
                })
        
        if significant_shifts:
            logger.warning(
                f"Detected {len(significant_shifts)} significant rate shifts: "
                f"{[s['currency'] for s in significant_shifts]}"
            )
            
            # Trigger full revaluation
            trigger_ledger_revaluation_task.delay()
            
            # TODO: Send alerts to affected users
        
        return {
            'status': 'success',
            'threshold_pct': threshold_pct,
            'shifts_detected': len(significant_shifts),
            'shifts': significant_shifts,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Rate shift detection failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@celery.task(name='fx.backfill_rates')
def backfill_historical_rates_task(
    base_currency: str = 'USD',
    days: int = 30
) -> Dict:
    """
    Backfill historical FX rates for a specified period.
    
    Useful for initializing the system or recovering missing data.
    """
    logger.info(f"Backfilling {days} days of FX rates")
    
    rates_stored = 0
    errors = []
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            try:
                # Fetch historical rates (using historical endpoint)
                response = requests.get(
                    f"https://api.exchangerate-api.com/v4/history/{base_currency}/{current_date.isoformat()}",
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get('rates', {})
                    
                    for currency, rate in rates.items():
                        FXService.store_rate(
                            from_currency=currency,
                            to_currency=base_currency,
                            rate=Decimal(str(rate)),
                            rate_date=current_date,
                            source='historical_backfill',
                            mark_current=(current_date == end_date)
                        )
                        rates_stored += 1
                else:
                    errors.append(f"{current_date}: API returned {response.status_code}")
                    
            except Exception as e:
                errors.append(f"{current_date}: {str(e)}")
            
            current_date += timedelta(days=1)
        
        logger.info(f"Historical backfill completed: {rates_stored} rates stored")
        
        return {
            'status': 'success',
            'rates_stored': rates_stored,
            'days_processed': days,
            'errors': errors,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Historical backfill failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'rates_stored': rates_stored
        }


@celery.task(name='fx.cleanup_old_rates')
def cleanup_old_rates_task(days_to_keep: int = 365) -> Dict:
    """
    Clean up old FX rate records to manage database size.
    
    Keeps at least one rate per month for historical analysis.
    """
    logger.info(f"Cleaning up rates older than {days_to_keep} days")
    
    try:
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        # Delete old non-month-end rates
        deleted = FXRate.query.filter(
            FXRate.rate_date < cutoff_date,
            FXRate.is_current == False,
            # Keep month-end rates (day >= 28)
            db.extract('day', FXRate.rate_date) < 28
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        logger.info(f"Cleaned up {deleted} old FX rate records")
        
        return {
            'status': 'success',
            'records_deleted': deleted,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Rate cleanup failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@celery.task(name='fx.compute_exposure_alerts')
def compute_fx_exposure_alerts_task(
    threshold_pct: float = 5.0
) -> Dict:
    """
    Compute FX exposure alerts for vaults with significant currency risk.
    
    Args:
        threshold_pct: Alert when unrealized FX gain/loss exceeds this % of position
    """
    logger.info(f"Computing FX exposure alerts (threshold: {threshold_pct}%)")
    
    alerts = []
    
    try:
        # Find positions with significant unrealized gains/losses
        positions = VaultCurrencyPosition.query.filter(
            VaultCurrencyPosition.cumulative_unrealized_fx_gain != 0
        ).all()
        
        for position in positions:
            vault = position.vault
            if not vault:
                continue
            
            balance = VaultService.get_position_balance(position)
            if balance <= 0:
                continue
            
            # Calculate unrealized as % of original position
            original_value = position.cost_basis_amount or (balance * (position.cost_basis_rate or Decimal('1')))
            
            if original_value > 0:
                unrealized_pct = abs(
                    float(position.cumulative_unrealized_fx_gain) / float(original_value) * 100
                )
                
                if unrealized_pct >= threshold_pct:
                    alerts.append({
                        'vault_id': vault.vault_id,
                        'vault_name': vault.name,
                        'currency': position.currency,
                        'balance': float(balance),
                        'unrealized_gain': float(position.cumulative_unrealized_fx_gain),
                        'unrealized_pct': round(unrealized_pct, 2),
                        'is_gain': position.cumulative_unrealized_fx_gain > 0
                    })
        
        if alerts:
            logger.warning(f"Generated {len(alerts)} FX exposure alerts")
            
            # TODO: Send notifications to users
        
        return {
            'status': 'success',
            'alerts_generated': len(alerts),
            'alerts': alerts,
            'threshold_pct': threshold_pct,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"FX exposure alert computation failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


@celery.task(name='fx.daily_rate_sync')
def daily_fx_rate_sync_task() -> Dict:
    """
    Daily FX rate sync job.
    
    This is the main scheduled task that:
    1. Syncs rates from external API
    2. Detects significant shifts
    3. Triggers revaluations
    4. Computes exposure alerts
    """
    logger.info("Starting daily FX rate sync")
    
    results = {
        'sync': None,
        'shifts': None,
        'alerts': None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        # Step 1: Sync rates
        results['sync'] = sync_fx_rates_task()
        
        # Step 2: Detect significant shifts
        results['shifts'] = detect_significant_rate_shifts_task(threshold_pct=0.5)
        
        # Step 3: Compute exposure alerts
        results['alerts'] = compute_fx_exposure_alerts_task(threshold_pct=3.0)
        
        results['status'] = 'success'
        logger.info("Daily FX rate sync completed successfully")
        
    except Exception as e:
        results['status'] = 'error'
        results['error'] = str(e)
        logger.error(f"Daily FX rate sync failed: {str(e)}")
    
    return results


# Celery beat schedule entry (add to celeryconfig.py)
FX_CELERY_BEAT_SCHEDULE = {
    'daily-fx-rate-sync': {
        'task': 'fx.daily_rate_sync',
        'schedule': 3600,  # Every hour
    },
    'fx-rate-shift-detection': {
        'task': 'fx.detect_rate_shifts',
        'schedule': 1800,  # Every 30 minutes
        'kwargs': {'threshold_pct': 0.5}
    },
    'fx-exposure-alerts': {
        'task': 'fx.compute_exposure_alerts',
        'schedule': 86400,  # Daily
        'kwargs': {'threshold_pct': 5.0}
    },
    'fx-rate-cleanup': {
        'task': 'fx.cleanup_old_rates',
        'schedule': 604800,  # Weekly
        'kwargs': {'days_to_keep': 365}
    }
}
