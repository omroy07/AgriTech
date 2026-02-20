from backend.celery_app import celery_app
from backend.services.risk_adjustment_service import RiskAdjustmentService
from backend.models.insurance import InsurancePolicy
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.insurance_risk_recalc')
def insurance_risk_recalc():
    """
    Periodic task to recalculate risk scores and premiums for all active policies.
    Runs every 6 hours.
    """
    logger.info("Starting Periodic Insurance Risk Recalculation...")
    active_policies = InsurancePolicy.query.filter_by(status='ACTIVE', is_suspended=False).all()
    count = 0
    
    for policy in active_policies:
        try:
            RiskAdjustmentService.calculate_actuarial_flux(policy.id)
            count += 1
        except Exception as e:
            logger.error(f"Risk recalculation failed for policy {policy.id}: {str(e)}")
            
    return {'status': 'completed', 'policies_updated': count}

@celery_app.task(name='tasks.monitor_logistics_batch_risk')
def monitor_logistics_batch_risk(batch_id):
    """
    Async task triggered when a batch movement is recorded.
    Checks for temperature or route safety to suspend insurance if needed.
    """
    RiskAdjustmentService.monitor_logistics_safety(batch_id)
    return {'status': 'processed', 'batch_id': batch_id}
