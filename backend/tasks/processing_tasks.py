from backend.celery_app import celery_app
from backend.models.processing import ProcessingBatch, ProcessingStage
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.monitor_stale_batches')
def monitor_stale_batches_task():
    """Detect batches that have been stuck in a stage for more than 48 hours"""
    threshold = datetime.utcnow() - timedelta(hours=48)
    stale_batches = ProcessingBatch.query.filter(
        ProcessingBatch.current_stage != ProcessingStage.COMPLETED.value,
        ProcessingBatch.updated_at < threshold
    ).all()
    
    for batch in stale_batches:
        logger.warning(f"Production Lag: Batch {batch.batch_number} is stale in {batch.current_stage} stage.")
        
    return {'status': 'success', 'stale_count': len(stale_batches)}

@celery_app.task(name='tasks.daily_production_report')
def daily_production_report_task():
    """Aggregate stats for completed batches in the last 24h"""
    yesterday = datetime.utcnow() - timedelta(days=1)
    batch_count = ProcessingBatch.query.filter(
        ProcessingBatch.completed_at >= yesterday
    ).count()
    
    total_output = db.session.query(db.func.sum(ProcessingBatch.current_weight))\
        .filter(ProcessingBatch.completed_at >= yesterday).scalar() or 0
        
    logger.info(f"Daily Production: Generated {batch_count} batches with {total_output} kg total yield.")
    return {
        'batches_completed': batch_count,
        'total_kg': float(total_output)
    }
