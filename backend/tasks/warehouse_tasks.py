from backend.celery_app import celery_app
from backend.models.warehouse import StockItem, WarehouseLocation
from backend.services.inventory_service import InventoryService
from backend.extensions import db
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.daily_expiry_alerts')
def daily_expiry_alerts_task():
    """
    Sends alerts for stock items expiring within 7 days.
    """
    warehouses = WarehouseLocation.query.all()
    total_alerts = 0
    
    for warehouse in warehouses:
        expiring = InventoryService.get_expiring_stock(warehouse.id, days_threshold=7)
        for item in expiring:
            logger.warning(f"Expiry Alert: {item['item']['name']} (SKU: {item['item']['sku']}) expires in {item['days_left']} days at Warehouse #{warehouse.id}")
            total_alerts += 1
    
    return {'status': 'success', 'alerts_sent': total_alerts}

@celery_app.task(name='tasks.automated_reorder_notifications')
def automated_reorder_notifications_task():
    """
    Checks all stock items and triggers reorder notifications for items below reorder point.
    """
    items = StockItem.query.filter(
        StockItem.reorder_point.isnot(None)
    ).all()
    
    reorder_needed = 0
    for item in items:
        if item.current_quantity <= item.reorder_point:
            logger.info(f"Reorder Notification: {item.item_name} (SKU: {item.sku}) - Current: {item.current_quantity}, Reorder Point: {item.reorder_point}")
            # In real app: send email/notification to procurement team
            reorder_needed += 1
    
    return {'status': 'success', 'reorder_notifications': reorder_needed}

@celery_app.task(name='tasks.monthly_reconciliation_reminder')
def monthly_reconciliation_reminder_task():
    """
    Sends monthly reminders to warehouse managers to perform stock reconciliation.
    """
    warehouses = WarehouseLocation.query.all()
    
    for warehouse in warehouses:
        logger.info(f"Reconciliation Reminder: Warehouse #{warehouse.id} ({warehouse.name}) - Monthly audit due")
        # In real app: send email to warehouse.manager_id
    
    return {'status': 'success', 'reminders_sent': len(warehouses)}
