from backend.celery_app import celery_app
# L3-1560: Predictive Harvest Velocity & Autonomous Futures Hedging
from backend.services.velocity_engine import VelocityEngine
from backend.models.farm import Farm
from backend.models.market import ForwardContract, PriceHedgingLog
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.velocity_market_sync')
def velocity_market_sync():
    """
    Daily task to update harvest indicators and adjust autonomous hedging.
    """
    logger.info("Starting Autonomous Market Sync...")
    farms = Farm.query.all()
    count = 0
    
    for farm in farms:
        try:
            # 1. Update Velocity Indicators
            readiness = VelocityEngine.calculate_harvest_readiness(farm.id)
            VelocityEngine.predict_yield_volume(farm.id)
            
            # 2. Autonomous Hedging Adjustment (L3 Requirement)
            new_ratio = VelocityEngine.calculate_hedge_ratio(farm.id)
            
            # Check if we need to auto-adjust existing open contracts
            # (Simplified logic: Log if significant change)
            last_log = PriceHedgingLog.query.filter_by(farm_id=farm.id).order_by(PriceHedgingLog.timestamp.desc()).first()
            old_ratio = last_log.new_hedge_ratio if last_log else 0.0
            
            if abs(new_ratio - old_ratio) > 0.1:
                log = PriceHedgingLog(
                    farm_id=farm.id,
                    action="AUTO_HEDGE_ADJUSTMENT",
                    old_hedge_ratio=old_ratio,
                    new_hedge_ratio=new_ratio,
                    trigger_reason="Weather Volatility Flux",
                    market_price_snapshot=15.50 # Simulated spot price
                )
                db.session.add(log)
            
            # 3. Auto-Alert if Maturity > 90%
            if readiness > 90.0:
                from backend.services.notification_service import NotificationService
                NotificationService.create_notification(
                    user_id=1, # Owner/Broker
                    title="Harvest Imminent",
                    message=f"Farm {farm.name} has reached {readiness:.1f}% maturity. Ready for futures execution.",
                    category="MARKET"
                )
                
            count += 1
        except Exception as e:
            logger.error(f"Market sync failed for Farm {farm.id}: {str(e)}")
            
    db.session.commit()
    return {'status': 'completed', 'farms_synced': count}
