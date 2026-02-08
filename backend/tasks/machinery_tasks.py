from backend.celery_app import celery_app
from backend.models.machinery import MaintenanceCycle, EngineHourLog, MaintenanceStatus
from backend.models.equipment import Equipment
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.check_maintenance_intervals')
def check_maintenance_intervals_task():
    """
    Daily scan of all machinery logs to detect overdue maintenance 
    based on cumulative engine hours.
    """
    cycles = MaintenanceCycle.query.filter(
        MaintenanceCycle.status != MaintenanceStatus.OVERDUE.value
    ).all()
    
    flagged = 0
    for cycle in cycles:
        # Calculate total hours for this equipment
        logs = EngineHourLog.query.filter_by(equipment_id=cycle.equipment_id).all()
        total_hours = sum([l.total_usage() for l in logs])
        
        next_due = cycle.last_service_hour + cycle.interval_hours
        
        if total_hours >= next_due:
            cycle.status = MaintenanceStatus.OVERDUE.value
            logger.warning(f"Maintenance Overdue: Equipment #{cycle.equipment_id} needs {cycle.service_type}")
            flagged += 1
            
    db.session.commit()
    return {'status': 'success', 'flagged_count': flagged}

@celery_app.task(name='tasks.machinery_valuation_update')
def machinery_valuation_update_task():
    """
    Monthly update to machinery resale value based on usage hours and age.
    """
    # In real app, calculate and update a 'current_value' field on Equipment
    equipment_list = Equipment.query.all()
    for e in equipment_list:
        # Simplified: Log valuation update
        logger.info(f"Updated valuation for Equipment #{e.id} based on recent hour-meter logs.")
        
    return {'status': 'success', 'processed': len(equipment_list)}
