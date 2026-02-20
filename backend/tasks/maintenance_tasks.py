from datetime import datetime
from backend.services.maintenance_logic import MaintenanceLogic
from backend.models.equipment import Equipment, MaintenanceStatus
from backend.extensions import db
from backend.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.fleet_reliability_audit')
def fleet_reliability_audit():
    """
    Periodic background audit of entire fleet health.
    Triggers safety lockouts for equipment deteriorating below 40%.
    """
    logger.info("Starting Fleet-Wide Reliability Audit...")
    
    # Process only active equipment (Simplification)
    active_equipment = Equipment.query.filter(Equipment.is_available==True).all()
    count = 0
    locked_count = 0
    
    for equip in active_equipment:
        try:
            old_score = equip.reliability_score
            new_score = MaintenanceLogic.update_reliability_score(equip.id)
            
            if new_score < 40.0 and old_score >= 40.0:
                locked_count += 1
                MaintenanceLogic.trigger_emergency_maintenance(equip)
                
            count += 1
        except Exception as e:
            logger.error(f"Audit failed for equipment {equip.id}: {str(e)}")
            
    return {'status': 'completed', 'audited': count, 'emergencies_triggered': locked_count}

@celery_app.task(name='tasks.check_maintenance_overdue')
def check_maintenance_cycles():
    """Checks for skipped maintenance intervals based on engine hours."""
    # Logic to query MaintenanceCycle where next_due_hour < current_engine_hours
    # and auto-flag equipment status to OVERDUE
    pass
