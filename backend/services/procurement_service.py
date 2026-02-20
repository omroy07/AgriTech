from datetime import datetime
from backend.extensions import db
from backend.models.procurement import BulkOrder, OrderEvent, OrderStatus, ProcurementItem
from backend.services.pricing_engine import PricingEngine
import logging

logger = logging.getLogger(__name__)

class ProcurementService:
    @staticmethod
    def create_order(buyer_id, item_id, quantity, address):
        """Initiate a bulk order request"""
        try:
            item = ProcurementItem.query.get(item_id)
            if not item:
                return None, "Item not found"
            
            unit_price = PricingEngine.calculate_unit_price(item, quantity)
            subtotal = unit_price * quantity
            tax = PricingEngine.calculate_tax(subtotal)
            shipping = PricingEngine.estimate_shipping("Warehouse", address, quantity) # Simple mock
            
            order = BulkOrder(
                buyer_id=buyer_id,
                vendor_id=item.vendor_id,
                item_id=item_id,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=subtotal + tax + shipping,
                tax_amount=tax,
                shipping_cost=shipping,
                delivery_address=address,
                status=OrderStatus.PROPOSED.value
            )
            
            db.session.add(order)
            db.session.flush()
            
            # Log initial event
            event = OrderEvent(
                order_id=order.id,
                to_status=OrderStatus.PROPOSED.value,
                comment="Order initiated by buyer"
            )
            db.session.add(event)
            db.session.commit()
            return order, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def transition_order(order_id, to_status, comment=None):
        """State machine management for order lifecycles"""
        order = BulkOrder.query.get(order_id)
        if not order:
            return False, "Order not found"
            
        from_status = order.status
        # Basic validation of transition can be added here
        
        order.status = to_status
        event = OrderEvent(
            order_id=order.id,
            from_status=from_status,
            to_status=to_status,
            comment=comment
        )
        db.session.add(event)
        db.session.commit()
        return True, None

    @staticmethod
    def get_order_history(order_id):
        """Get audit trail for an order"""
        return OrderEvent.query.filter_by(order_id=order_id).order_by(OrderEvent.timestamp.asc()).all()
