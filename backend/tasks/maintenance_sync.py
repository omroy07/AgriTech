from backend.celery_app import celery_app
from backend.models.equipment import Equipment, EngineHourLog
from backend.services.predictive_maintenance import PredictiveMaintenance
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.maintenance_sync')
def maintenance_sync():
    """
    Daily task to scan machinery usage and update microscopic wear/depreciation.
    """
    logger.info("Starting Daily Equipment Maintenance Sync...")
    
    # Process logs from the last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_logs = EngineHourLog.query.filter(EngineHourLog.logged_at >= yesterday).all()
    
    sync_count = 0
    for log in new_logs:
        usage = log.hours_end - log.hours_start
        if usage > 0:
            equipment = Equipment.query.get(log.equipment_id)
            if equipment:
                PredictiveMaintenance.calculate_wear_impact(
                    equipment_id=equipment.id,
                    usage_hours=usage,
                    farm_id=equipment.owner_id
                )
                sync_count += 1
                
    logger.info(f"Synchronized depreciation for {sync_count} equipment logs.")
    return {'status': 'completed', 'updated_count': sync_count}
