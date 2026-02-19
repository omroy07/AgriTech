from backend.celery_app import celery_app
from backend.services.fertigation_service import FertigationService
from backend.models.irrigation import IrrigationZone, FertigationLog
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.precision_fertigation_sync')
def precision_fertigation_sync():
    """
    Task to execute autonomous fertigation checks for all active zones.
    Runs frequency: Every 15 minutes.
    """
    logger.info("Starting Precision Fertigation Sync...")
    active_zones = IrrigationZone.query.filter_by(fertigation_enabled=True).all()
    count = 0
    
    for zone in active_zones:
        try:
            success = FertigationService.trigger_automated_fertigation(zone.id)
            if success:
                count += 1
        except Exception as e:
            logger.error(f"Fertigation sync failed for zone {zone.id}: {str(e)}")
            
    return {'status': 'completed', 'injections_triggered': count}

@celery_app.task(name='tasks.update_nutrient_maps')
def update_nutrient_maps():
    """
    Background task to update field-wide nutrient maps based on irrigation logs.
    Re-calculates flux indices after heavy fertigation sessions.
    """
    # Logic to aggregate recent FertigationLogs and decay the soil nitrogen levels
    # This keeps the "Virtual Soil Model" in sync between physical lab tests
    pass 
