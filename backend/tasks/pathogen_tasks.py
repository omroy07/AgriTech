from backend.celery_app import celery_app
from backend.services.pathogen_service import PathogenPropagationService
from backend.models.gews import OutbreakZone
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.pathogen_propagation_run')
def pathogen_propagation_run():
    """
    Periodic task to refresh all active outbreak zones with new environmental data.
    """
    logger.info("Starting global pathogen propagation simulation...")
    active_zones = OutbreakZone.query.filter_by(status='active').all()
    
    results = []
    for zone in active_zones:
        try:
            updated_zone = PathogenPropagationService.simulate_propagation(zone.id)
            results.append({
                'zone_id': zone.zone_id,
                'velocity': updated_zone.propagation_velocity,
                'status': updated_zone.containment_status
            })
        except Exception as e:
            logger.error(f"Failed to simulate propagation for zone {zone.zone_id}: {str(e)}")
            
    return {
        'status': 'success',
        'processed_zones': len(results),
        'summary': results
    }

@celery_app.task(name='tasks.analyze_new_incident')
def analyze_new_incident(incident_id):
    """
    Triggered whenever UDEMP detects a new disease. 
    Checks if it should start a new OutbreakZone or merge into existing.
    """
    from backend.models.gews import DiseaseIncident
    incident = DiseaseIncident.query.get(incident_id)
    if not incident:
        return
        
    # Logic to find nearby zones or create new one
    # For this L3 task, we assume the zone management is handled, 
    # but we trigger an immediate simulation update.
    if incident.outbreak_zone_id:
        pathogen_propagation_run.delay()
