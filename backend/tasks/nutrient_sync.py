from backend.celery_app import celery_app
from backend.models.irrigation import IrrigationZone
from backend.services.nutrient_advisor import NutrientAdvisor
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.nutrient_optimization_sweep')
def run_nutrient_sweep():
    """
    Scans enabled fertigation zones and recalibrates chemical concentrations 
    based on the latest soil and weather flux.
    """
    logger.info("🧪 [L3-1645] Initializing Soil Nutrient Optimization Sweep...")
    
    zones = IrrigationZone.query.filter_by(fertigation_enabled=True).all()
    optimizations = 0
    
    for zone in zones:
        try:
            NutrientAdvisor.calculate_injection_strategy(zone.id)
            optimizations += 1
        except Exception as e:
            logger.error(f"Failed nutrient optimization for zone {zone.id}: {e}")
            
    logger.info(f"Nutrient sweep complete. {optimizations} zones recalibrated.")
    return {'optimized_zones': optimizations}
