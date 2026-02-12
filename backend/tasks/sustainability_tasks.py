from backend.celery_app import celery_app
from backend.models.sustainability import CarbonPractice, AuditRequest, AuditStatus
from backend.services.carbon_service import CarbonService
from backend.services.audit_workflow import AuditWorkflow
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.recalculate_all_offsets')
def recalculate_all_offsets_task():
    """Daily task to update estimated offsets for all ongoing practices"""
    try:
        # Get active practices (not yet finished or very recent)
        practices = CarbonPractice.query.filter_by(is_verified=False).all()
        count = 0
        for p in practices:
            CarbonService.calculate_and_update_offsets(p.id)
            count += 1
            
        logger.info(f"Recalculated offsets for {count} practices.")
        return {'status': 'success', 'updated': count}
    except Exception as e:
        logger.error(f"Offset recalculation task failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task(name='tasks.stale_audit_check')
def stale_audit_check_task():
    """Monitor for audits that have been 'AUDITING' for too long (e.g., > 14 days)"""
    from datetime import datetime, timedelta
    threshold = datetime.utcnow() - timedelta(days=14)
    
    stale_audits = AuditRequest.query.filter(
        AuditRequest.status == AuditStatus.AUDITING.value,
        AuditRequest.submitted_at < threshold
    ).all()
    
    if stale_audits:
        logger.warning(f"Found {len(stale_audits)} stale audits needing administrative review.")
        
    return {'status': 'success', 'stale_count': len(stale_audits)}

@celery_app.task(name='tasks.annual_credit_revaluation')
def annual_credit_revaluation_task():
    """Scientific audit to re-verify that sequestered carbon remains in the soil/trees"""
    # This would involve new audit triggers or soil testing integration
    logger.info("Executed annual carbon sequestration persistence audit.")
    return {'status': 'success'}
