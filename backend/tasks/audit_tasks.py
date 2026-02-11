from datetime import datetime, timedelta
from backend.celery_app import celery_app
from backend.extensions import db
from backend.models import AuditLog, UserSession
from backend.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.purge_stale_sessions')
def purge_stale_sessions(timeout_hours=24):
    """
    Terminates sessions that haven't shown activity for the specified period.
    """
    cutoff = datetime.utcnow() - timedelta(hours=timeout_hours)
    stale_count = UserSession.query.filter(
        UserSession.is_active == True,
        UserSession.last_activity < cutoff
    ).update({
        'is_active': False, 
        'logout_time': datetime.utcnow()
    })
    
    db.session.commit()
    logger.info(f"Purged {stale_count} stale user sessions.")
    return {'status': 'success', 'purged': stale_count}

@celery_app.task(name='tasks.generate_daily_security_audit')
def generate_daily_security_audit():
    """
    Generates a system-wide security report and logs it as a CRITICAL audit entry.
    """
    report = AuditService.generate_security_report(hours=24)
    
    # Store the report summary in the audit log itself
    AuditService.log_action(
        action="SYSTEM_SECURITY_FORENSIC_REPORT",
        risk_level="HIGH",
        meta_data=report
    )
    
    # If high threat count, register a system alert
    if report['threat_count'] > 20:
        from backend.services.alert_registry import AlertRegistry
        AlertRegistry.register_alert(
            title="High Threat Volume Detected",
            message=f"Forensic analysis detected {report['threat_count']} security incidents in the last 24h.",
            category="SECURITY",
            priority="CRITICAL"
        )
        
    return {'status': 'success', 'threats_found': report['threat_count']}

@celery_app.task(name='tasks.rotate_audit_logs')
def rotate_audit_logs(retention_days=180):
    """
    Background maintenance to prune extremely old logs.
    """
    deleted = AuditLog.archive_old_logs(days=retention_days)
    logger.info(f"Rotated {deleted} old audit log entries.")
    return {'status': 'success', 'deleted': deleted}
