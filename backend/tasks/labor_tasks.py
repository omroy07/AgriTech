from backend.celery_app import celery_app
from backend.models.labor import WorkerProfile, WorkShift
from backend.services.payroll_service import PayrollService
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.generate_weekly_payroll_batch')
def generate_weekly_payroll_batch_task():
    """
    Automated weekly task to generate payroll for all active workers.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    workers = WorkerProfile.query.filter_by(is_active=True).all()
    processed = 0
    
    for worker in workers:
        payroll, error = PayrollService.generate_worker_payroll(worker.id, start_date, end_date)
        if not error:
            processed += 1
            logger.info(f"Generated weekly payroll for Worker #{worker.id}")
        else:
            logger.error(f"Failed payroll for Worker #{worker.id}: {error}")
            
    return {'status': 'success', 'processed_count': processed}

@celery_app.task(name='tasks.shift_reminder_alerts')
def shift_reminder_alerts_task():
    """
    Alerts workers who haven't clocked out after 12 hours (potential staleness).
    """
    twelve_hours_ago = datetime.utcnow() - timedelta(hours=12)
    stale_shifts = WorkShift.query.filter(
        WorkShift.shift_status == 'ACTIVE',
        WorkShift.start_time <= twelve_hours_ago
    ).all()
    
    notified = 0
    for shift in stale_shifts:
        logger.warning(f"Stale shift detected for Worker #{shift.worker_id} (Duration > 12h)")
        # In real app: Push notification or auto clock-out
        notified += 1
        
    return {'status': 'success', 'stale_alerts': notified}
