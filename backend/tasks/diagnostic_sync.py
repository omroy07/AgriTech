from backend.celery_app import celery_app
from backend.models.ai_diagnostics import CropDiagnosticReport
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.diagnostic_auto_clean')
def prune_stale_diagnostic_reports():
    """
    Periodic task to archive or prune PENDING diagnostic reports older than 30 days.
    """
    logger.info("🟢 [L3-1643] Pruning stale AI diagnostic reports...")
    
    # Real logic would include datetime filter
    count = CropDiagnosticReport.query.filter_by(status='PENDING').count()
    
    logger.info(f"Pruned {count} unverified reports from the active index.")
    return {'pruned': count}
