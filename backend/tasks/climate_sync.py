"""
Climate Sync Celery Tasks — L3-1630
=====================================
Periodic tasks that drive the Yield Resilience Engine autonomously.
"""

from backend.celery_app import celery_app
from backend.models.weather import (
    ClimateTelemetryEvent, ForceMajeureAlert, ParametricPolicyTrigger
)
from backend.models.insurance_v2 import CropPolicy, PolicyStatus
from backend.models.market import ForwardContract
from backend.services.yield_resilience_service import YieldResilienceEngine
from backend.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.climate_sweep')
def climate_sweep():
    """
    Hourly task: re-evaluates all farms with recent extreme events.
    Detects new Force Majeure streaks and triggers parametric settlements.
    """
    logger.info("═══ Starting Climate Sweep ═══")
    cutoff = datetime.utcnow() - timedelta(hours=25)

    # Farms with recent extreme events
    affected_farm_ids = db.session.query(
        ClimateTelemetryEvent.farm_id
    ).filter(
        ClimateTelemetryEvent.is_extreme == True,   # noqa
        ClimateTelemetryEvent.recorded_at >= cutoff
    ).distinct().all()

    stats = {'farms_evaluated': 0, 'alerts_raised': 0, 'settlements_posted': 0}

    for (farm_id,) in affected_farm_ids:
        yar = YieldResilienceEngine.compute_yield_at_risk(farm_id)
        stats['farms_evaluated'] += 1

        # Count new auto-settlements triggered this cycle
        new_settlements = db.session.query(
            func.count()
        ).select_from(
            __import__('backend.models.insurance_v2', fromlist=['ParametricAutoSettlement'])
            .ParametricAutoSettlement
        ).filter_by(
            # settlements from last hour
        ).scalar() or 0

        if yar['active_force_majeure_alerts'] > 0:
            stats['alerts_raised'] += yar['active_force_majeure_alerts']

    db.session.commit()
    logger.info(f"═══ Climate Sweep Complete: {stats} ═══")
    return stats


@celery_app.task(name='tasks.yield_at_risk_refresh')
def yield_at_risk_refresh():
    """
    Daily task: refreshes Yield-at-Risk scores for all farms with open contracts
    and updates ForwardContract climate_risk_discount values from latest telemetry.
    """
    logger.info("═══ Starting YaR Daily Refresh ═══")

    # Get all farms with open contracts
    farm_ids = db.session.query(ForwardContract.farm_id).filter(
        ForwardContract.status.in_(['OPEN', 'SIGNED'])
    ).distinct().all()

    updated = 0
    for (farm_id,) in farm_ids:
        yar = YieldResilienceEngine.compute_yield_at_risk(farm_id)
        risk_tier = yar['risk_tier']

        # Apply rolling YaR to open contracts
        contracts = ForwardContract.query.filter(
            ForwardContract.farm_id == farm_id,
            ForwardContract.status.in_(['OPEN', 'SIGNED']),
            ForwardContract.force_majeure_suspended == False  # noqa
        ).all()

        for contract in contracts:
            extreme_count = yar['extreme_events_7d']
            yar_pct = min(50.0, extreme_count * 2.5)  # 2.5% per extreme event, cap 50%
            contract.yield_at_risk_pct = yar_pct
            updated += 1

        logger.info(f"[YaRRefresh] Farm {farm_id} | Tier: {risk_tier} | Contracts updated: {len(contracts)}")

    db.session.commit()
    logger.info(f"═══ YaR Refresh: {updated} contracts updated ═══")
    return {'contracts_updated': updated}


@celery_app.task(name='tasks.force_majeure_expiry_check')
def force_majeure_expiry_check():
    """
    Daily task: expires Force Majeure alerts older than 30 days
    and reinstates suspended ForwardContracts where conditions have normalised.
    """
    expiry_threshold = datetime.utcnow() - timedelta(days=30)
    old_alerts = ForceMajeureAlert.query.filter(
        ForceMajeureAlert.status == 'ACTIVE',
        ForceMajeureAlert.triggered_at <= expiry_threshold
    ).all()

    for alert in old_alerts:
        alert.status = 'EXPIRED'
        alert.resolved_at = datetime.utcnow()

        # Reinstate suspended contracts for this farm
        suspended = ForwardContract.query.filter_by(
            farm_id=alert.farm_id,
            force_majeure_suspended=True
        ).all()
        for contract in suspended:
            contract.force_majeure_suspended = False
            contract.climate_risk_discount = 0.0
            logger.info(f"[FMExpiry] Contract {contract.id} reinstated for Farm {alert.farm_id}")

    db.session.commit()
    logger.info(f"[FMExpiry] Expired {len(old_alerts)} stale Force Majeure alerts.")
    return {'expired_alerts': len(old_alerts)}
