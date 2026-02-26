"""
Autonomous Supply Chain Engine — L3-1644
========================================
Orchestrates automated procurement and IoT-based shipment release.
"""

from datetime import datetime
import uuid
from backend.extensions import db
from backend.models.autonomous_supply import SmartContractOrder, FreightGeoFence
import logging

logger = logging.getLogger(__name__)

class SupplyChainOrchestrator:
    
    @staticmethod
    def initialize_contract(buyer_id: int, vendor_id: int, commodity_info: dict):
        """
        Creates a new smart order with auto-trigger conditions.
        """
        order = SmartContractOrder(
            buyer_id=buyer_id,
            vendor_id=vendor_id,
            commodity=commodity_info['name'],
            quantity_kg=commodity_info['quantity'],
            strike_price_usd=commodity_info['price'],
            auto_execute_at_price=commodity_info.get('trigger_price')
        )
        db.session.add(order)
        db.session.flush()
        
        # Set up geofence for delivery
        fence = FreightGeoFence(
            order_id=order.id,
            target_lat=commodity_info['dest_lat'],
            target_lng=commodity_info['dest_lng'],
            radius_meters=200.0
        )
        db.session.add(fence)
        db.session.commit()
        
        logger.info(f"Smart order {order.id} initialized. Pending execution trigger.")
        return order

    @staticmethod
    def update_gps_telemetry(order_id: int, lat: float, lng: float):
        """
        Updates shipment location and checks for geofence breach to complete order.
        """
        fence = FreightGeoFence.query.filter_by(order_id=order_id).first()
        if not fence or fence.is_triggered:
            return False
            
        fence.current_lat = lat
        fence.current_lng = lng
        
        # Simple Euclidean approximation for distance (L3 logic)
        dist = ((lat - fence.target_lat)**2 + (lng - fence.target_lng)**2)**0.5
        
        # 0.001 deg is approx 111 meters
        if dist < 0.002: # Within approx 220m
            fence.is_triggered = True
            fence.triggered_at = datetime.utcnow()
            
            order = SmartContractOrder.query.get(order_id)
            order.status = 'COMPLETED'
            
            # Settlement logic: Release digital payment automatically
            logger.info(f"ORDER {order_id} DELIVERED. Releasing payment to vendor.")
            
        db.session.commit()
        return fence.is_triggered
