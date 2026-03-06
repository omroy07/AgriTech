from backend.celery_app import celery_app
from backend.models.farm import FarmAsset
from backend.services.maintenance_forecaster import MaintenanceForecaster
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.predictive_maintenance_run')
def run_fleet_maintenance_sweep():
    """
    Automated fleet analysis task. Iterates through all machinery to update wear maps
    and detect failure risks.
    """
    logger.info("🚜 [L3-1641] Scanning fleet for mechanical anomalies...")
    
    # In a real system, we'd query assets with categories like 'Tractor'
    assets = FarmAsset.query.all() 
    
    for asset in assets:
        MaintenanceForecaster.update_wear_status(asset.id)
        # Check if we need to run a full failure inference
        MaintenanceForecaster.run_inference(asset.id)
        
    logger.info(f"Mechanical health sweep complete for {len(assets)} assets.")
    return True
