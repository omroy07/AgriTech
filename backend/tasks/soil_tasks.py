from backend.celery_app import celery_app
from backend.models.soil_health import SoilTest
from backend.models.farm import Farm
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.generate_seasonal_soil_reports')
def generate_seasonal_soil_reports_task():
    """Generates monthly soil health summaries for all farms with recent tests."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_tests = SoilTest.query.filter(SoilTest.created_at >= thirty_days_ago).all()
    
    farm_ids = set([t.farm_id for t in recent_tests])
    for farm_id in farm_ids:
        # In a real app, this would trigger email or PDF generation
        logger.info(f"Generating seasonal soil health report for Farm #{farm_id}")
        
    return {'status': 'success', 'farms_processed': len(farm_ids)}

@celery_app.task(name='tasks.fertilizer_application_reminder')
def fertilizer_application_reminder_task():
    """Reminds farmers to apply recommended fertilizers if not logged within 7 days of test."""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    pending_applications = SoilTest.query.filter(
        SoilTest.created_at <= seven_days_ago,
        SoilTest.created_at > seven_days_ago - timedelta(days=1)
    ).all()
    
    notified = 0
    for test in pending_applications:
        # Check if application log exists
        from backend.models.soil_health import ApplicationLog
        has_log = ApplicationLog.query.filter_by(soil_test_id=test.id).first()
        if not has_log:
            logger.info(f"Sending fertilizer application reminder for Test #{test.id} (Farm #{test.farm_id})")
            notified += 1
            
    return {'status': 'success', 'reminders_sent': notified}
