"""
Carbon Minting Celery Task — L3-1632
=====================================
Daily background task that scans all verified RegenerativeFarmingLogs
that have not yet been minted, triggers the Carbon Sequestration Engine,
and then auto-lists qualifying credits on the ESG marketplace.
"""

from backend.celery_app import celery_app
from backend.models.soil_health import RegenerativeFarmingLog, CarbonMintEvent
from backend.models.sustainability import ESGMarketListing
from backend.services.carbon_sequestration_engine import CarbonSequestrationEngine
from backend.services.notification_service import NotificationService
from backend.models.farm import Farm
from backend.extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.carbon_minting_sweep')
def carbon_minting_sweep():
    """
    Daily sweep: detects verified farming logs with no mint event,
    calculates sequestration, mints credits, and auto-lists on ESG market.
    """
    logger.info("═══ Starting Daily Carbon Minting Sweep ═══")

    # All verified logs not yet minted
    minted_log_ids = db.session.query(CarbonMintEvent.log_id).subquery()
    pending_logs = RegenerativeFarmingLog.query.filter(
        RegenerativeFarmingLog.verified == True,  # noqa: E712
        RegenerativeFarmingLog.id.notin_(minted_log_ids)
    ).all()

    stats = {
        'logs_processed': 0,
        'credits_minted': 0.0,
        'listings_created': 0,
        'errors': 0
    }

    for log in pending_logs:
        try:
            # 1. Mint credits
            mint_event, err = CarbonSequestrationEngine.mint_credits(log.id)
            if err:
                logger.error(f"Minting failed for Log {log.id}: {err}")
                stats['errors'] += 1
                continue

            stats['logs_processed'] += 1
            stats['credits_minted'] += mint_event.credits_minted

            # 2. Auto-list on ESG marketplace if credits ≥ 0.5 tCO2e
            if mint_event.credits_minted >= 0.5:
                listing, list_err = CarbonSequestrationEngine.list_on_esg_market(
                    mint_event_id=mint_event.id
                )
                if listing:
                    stats['listings_created'] += 1

            # 3. Notify farm owner
            farm = Farm.query.get(log.farm_id)
            if farm:
                NotificationService.create_notification(
                    title="🌱 Carbon Credits Minted",
                    message=(
                        f"{mint_event.credits_minted:.4f} tCO2e carbon credits have been minted "
                        f"for your {log.practice_type} practice on {log.area_hectares:.1f} ha. "
                        f"Estimated value: ${mint_event.total_value_usd:.2f} USD."
                    ),
                    notification_type="CARBON_CREDIT",
                    user_id=log.farm_id
                )

        except Exception as e:
            logger.error(f"Sweep error for Log {log.id}: {e}", exc_info=True)
            stats['errors'] += 1

    logger.info(f"═══ Carbon Sweep Complete: {stats} ═══")
    return stats


@celery_app.task(name='tasks.esg_listing_expiry_check')
def esg_listing_expiry_check():
    """
    Hourly task to expire stale ESG market listings past their expiry date.
    """
    now = datetime.utcnow()
    expired = ESGMarketListing.query.filter(
        ESGMarketListing.status == 'ACTIVE',
        ESGMarketListing.expires_at <= now
    ).all()

    for listing in expired:
        listing.status = 'EXPIRED'
        # Re-enable re-listing for the mint event
        if listing.mint_event_id:
            event = CarbonMintEvent.query.get(listing.mint_event_id)
            if event:
                event.listed_on_market = False

    db.session.commit()
    logger.info(f"[ESGExpiry] Expired {len(expired)} stale listings.")
    return {'expired_count': len(expired)}
