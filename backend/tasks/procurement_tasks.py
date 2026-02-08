from backend.celery_app import celery_app
from backend.models.procurement import BulkOrder, OrderStatus
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.procurement_payment_reminders')
def procurement_payment_reminders_task():
    """Remind buyers to pay for vetted bulk orders after 24 hours"""
    threshold = datetime.utcnow() - timedelta(hours=24)
    pending_orders = BulkOrder.query.filter_by(status=OrderStatus.VETTED.value)\
        .filter(BulkOrder.updated_at < threshold).all()
        
    for order in pending_orders:
        # In a real app, send email/notification
        logger.info(f"Sent payment reminder for Order #{order.id} to Buyer #{order.buyer_id}")
        
    return {'status': 'success', 'notified': len(pending_orders)}

@celery_app.task(name='tasks.vendor_payout_settlement')
def vendor_payout_settlement_task():
    """Automatically settle funds for delivered orders after 7 days (holding period)"""
    threshold = datetime.utcnow() - timedelta(days=7)
    delivered_orders = BulkOrder.query.filter_by(status=OrderStatus.DELIVERED.value)\
        .filter(BulkOrder.updated_at < threshold).all()
        
    for order in delivered_orders:
        order.status = OrderStatus.SETTLED.value
        logger.info(f"Settle funds for Order #{order.id} to Vendor #{order.vendor_id}")
        
    db.session.commit()
    return {'status': 'success', 'settled': len(delivered_orders)}
