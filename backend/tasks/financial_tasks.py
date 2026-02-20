from backend.celery_app import celery_app
from backend.services.solvency_forecaster import SolvencyForecaster
from backend.models.farm import Farm
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.generate_monthly_financial_health_certificates')
def generate_health_certificates():
    """
    Monthly task to generate 'Health Certificates' for all farms.
    Determines systemic solvency and flags issues for participating banks.
    """
    logger.info("Starting Monthly Financial Health Audit...")
    farms = Farm.query.all()
    count = 0
    
    for farm in farms:
        try:
            # Re-calculate solvency
            SolvencyForecaster.calculate_bankruptcy_risk(farm.id)
            count += 1
        except Exception as e:
            logger.error(f"Financial audit failed for Farm {farm.id}: {str(e)}")
            
    return {'status': 'completed', 'farms_audited': count}

@celery_app.task(name='tasks.asset_depreciation_run')
def run_asset_depreciation():
    """
    Weekly run to update AssetValueSnapshots across the entire fleet.
    """
    from backend.models.equipment import Equipment
    from backend.models.machinery import AssetValueSnapshot
    
    machinery = Equipment.query.all()
    for equip in machinery:
        # Simple straight-line depreciation simulation
        snap = AssetValueSnapshot(
            equipment_id=equip.id,
            current_book_value=10000.0, # Placeholder
            depreciation_accumulated=500.0,
            hours_impact_factor=0.1
        )
        db.session.add(snap)
    db.session.commit()
