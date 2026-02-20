from datetime import datetime, date
from backend.extensions import db
from backend.models.warehouse import StockItem, StockMovement, ReconciliationLog, WarehouseLocation
from backend.utils.stock_formulas import StockFormulas
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    @staticmethod
    def record_stock_in(stock_item_id, quantity, reference_doc, user_id):
        """Records incoming stock (purchase, transfer-in)."""
        try:
            item = StockItem.query.get(stock_item_id)
            if not item:
                return None, "Stock item not found"
            
            movement = StockMovement(
                stock_item_id=stock_item_id,
                movement_type='IN',
                quantity=quantity,
                reference_doc=reference_doc,
                performed_by=user_id
            )
            
            item.current_quantity += quantity
            db.session.add(movement)
            db.session.commit()
            
            return movement, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def record_stock_out(stock_item_id, quantity, reference_doc, user_id):
        """Records outgoing stock (sales, transfer-out) using FIFO logic."""
        try:
            item = StockItem.query.get(stock_item_id)
            if not item:
                return None, "Stock item not found"
            
            if item.current_quantity < quantity:
                return None, "Insufficient stock"
            
            movement = StockMovement(
                stock_item_id=stock_item_id,
                movement_type='OUT',
                quantity=quantity,
                reference_doc=reference_doc,
                performed_by=user_id
            )
            
            item.current_quantity -= quantity
            db.session.add(movement)
            db.session.commit()
            
            # Check if reorder needed
            if item.reorder_point and item.current_quantity <= item.reorder_point:
                logger.warning(f"Reorder Alert: {item.item_name} (SKU: {item.sku}) has fallen below reorder point.")
            
            return movement, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def perform_reconciliation(warehouse_id, user_id, physical_counts):
        """
        Performs stock reconciliation audit.
        physical_counts: dict {stock_item_id: physical_quantity}
        """
        try:
            items = StockItem.query.filter_by(warehouse_id=warehouse_id).all()
            discrepancies = 0
            total_shrinkage = 0.0
            
            for item in items:
                physical_qty = physical_counts.get(item.id, item.current_quantity)
                book_qty = item.current_quantity
                
                if physical_qty != book_qty:
                    discrepancies += 1
                    shrinkage_pct = StockFormulas.calculate_shrinkage_percentage(book_qty, physical_qty)
                    total_shrinkage += abs(book_qty - physical_qty)
                    
                    # Create adjustment movement
                    adjustment = StockMovement(
                        stock_item_id=item.id,
                        movement_type='ADJUSTMENT',
                        quantity=physical_qty - book_qty,
                        reason=f"Reconciliation: Book={book_qty}, Physical={physical_qty}, Shrinkage={shrinkage_pct}%",
                        performed_by=user_id
                    )
                    db.session.add(adjustment)
                    
                    # Update stock
                    item.current_quantity = physical_qty
            
            # Log reconciliation
            log = ReconciliationLog(
                warehouse_id=warehouse_id,
                total_items_checked=len(items),
                discrepancies_found=discrepancies,
                shrinkage_value=total_shrinkage,
                performed_by=user_id
            )
            db.session.add(log)
            db.session.commit()
            
            return log, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_expiring_stock(warehouse_id, days_threshold=30):
        """Returns stock items expiring within the specified days."""
        cutoff_date = date.today()
        items = StockItem.query.filter(
            StockItem.warehouse_id == warehouse_id,
            StockItem.expiry_date.isnot(None)
        ).all()
        
        expiring = []
        for item in items:
            days_left = StockFormulas.calculate_days_to_expiry(item.expiry_date, cutoff_date)
            if days_left <= days_threshold:
                expiring.append({
                    'item': item.to_dict(),
                    'days_left': days_left
                })
        
        return expiring
