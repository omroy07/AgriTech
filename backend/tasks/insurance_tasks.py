from backend.celery_app import celery_app
from backend.models.insurance_v2 import CropPolicy, PolicyStatus
from backend.extensions import db
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.insurance_policy_expiry_check')
def insurance_policy_expiry_check_task():
    """Automatically expire policies that have passed their end date"""
    today = date.today()
    expired_count = CropPolicy.query.filter(
        CropPolicy.status == PolicyStatus.ACTIVE.value,
        CropPolicy.end_date < today
    ).update({CropPolicy.status: PolicyStatus.EXPIRED.value})
    
    db.session.commit()
    return {'status': 'success', 'expired': expired_count}

@celery_app.task(name='tasks.weather_risk_monitor')
def weather_risk_monitor_task():
    """
    Mock task: Monitors weather triggers (drought/flood) and flags distressed 
    policies for proactive claim processing.
    """
    # In real app, fetch weather API data for farm locations
    distressed_policies = CropPolicy.query.filter_by(status=PolicyStatus.ACTIVE.value).all()
    
    flagged = 0
    for policy in distressed_policies:
        # Pseudo-logic: if high risk score and extreme weather event detected
        if policy.risk_score > 70:
            logger.warning(f"Extreme Weather Alert: Distressed crop detected for Policy #{policy.id} (Farm #{policy.farm_id})")
            flagged += 1
            
    return {'status': 'success', 'flagged_policies': flagged}
