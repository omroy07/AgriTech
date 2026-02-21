from backend.celery_app import celery_app
from backend.models.irrigation import WaterRightsQuota, IrrigationZone
from backend.models.farm import Farm
from backend.services.notification_service import NotificationService
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.water_quota_sync')
def water_quota_sync():
    """
    Periodic task to sync water usage against quotas and enforce hydro-locks.
    """
    logger.info("Synchronizing Regional Water Quotas...")
    
    quotas = WaterRightsQuota.query.filter_by(status='ACTIVE').all()
    lock_count = 0
    
    for quota in quotas:
        # Calculate utilization
        usage_ratio = quota.used_quota_liters / quota.total_quota_liters
        farm = Farm.query.get(quota.farm_id)
        
        # Broadcast warning alerts (L3-1605 Requirement)
        if usage_ratio >= 0.90 and usage_ratio < 1.0:
            NotificationService.broadcast_hydro_lock_warning(quota.farm_id, usage_ratio)
        elif usage_ratio >= 1.0:
            # TRIGGER HYDRO-LOCK
            quota.status = 'EXHAUSTED'
            
            # Lock all irrigation zones for this farm
            zones = IrrigationZone.query.filter_by(farm_id=quota.farm_id).all()
            for zone in zones:
                zone.banned_by_system = True
                zone.current_valve_status = 'closed'
                zone.auto_mode = False # Force manual intervention after lockout
            
            NotificationService.create_notification(
                title="HYDRO-LOCK ENFORCED",
                message=f"Water quota for Farm {farm.name} EXHAUSTED. All irrigation zones have been locked by the regional aquifer authority.",
                notification_type="LOCKED",
                user_id=farm.id
            )
            lock_count += 1
            
    db.session.commit()
    return {'status': 'completed', 'locks_triggered': lock_count}
