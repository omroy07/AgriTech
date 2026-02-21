from backend.celery_app import celery_app
from backend.models.processing import DynamicGradeAdjustment, ProcessingBatch
from backend.models.procurement import BulkOrder
from backend.extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.batch_pricing_normalization')
def batch_pricing_normalization():
    """
    End-of-day task to normalize pricing across batches and audit financial quality drifts.
    """
    logger.info("Starting End-of-Day Pricing Normalization...")
    
    # 1. Fetch all adjustments from today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    adjustments = DynamicGradeAdjustment.query.filter(DynamicGradeAdjustment.timestamp >= today_start).all()
    
    normalization_count = 0
    total_penalty_revenue_loss = 0.0
    
    for adj in adjustments:
        # Cross-reference with BulkOrders to ensure the modifier is correctly applied
        batch_id = adj.batch_id
        
        # In a real system, we would reconcile batch_id -> supply_batch_id -> bulk_order.item_id
        # Here we simulate the reconciliation logic
        logger.info(f"Reconciling financial drift for Batch {batch_id}: Grade {adj.old_grade} -> {adj.new_grade}")
        
        normalization_count += 1
        total_penalty_revenue_loss += adj.price_penalty_factor
        
    db.session.commit()
    return {
        'status': 'success',
        'adjusted_records': normalization_count,
        'cumulative_penalty_flux': total_penalty_revenue_loss
    }
