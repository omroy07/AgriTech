"""
Autonomous Supply Chain Models — L3-1644
=======================================
Smart-contract driven automatic procurement and smart-lock freight.
"""

from datetime import datetime
from backend.extensions import db

class SmartContractOrder(db.Model):
    __tablename__ = 'smart_contract_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    commodity = db.Column(db.String(100), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    strike_price_usd = db.Column(db.Float, nullable=False)
    
    # Auto-conditions
    auto_execute_at_price = db.Column(db.Float)
    
    # Status: PENDING_TRIGGER -> FUNDED -> SHIPPED -> COMPLETED
    status = db.Column(db.String(30), default='PENDING_TRIGGER')
    
    freight_locked_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FreightGeoFence(db.Model):
    """
    Electronic seals that trigger fund release on reaching destination.
    """
    __tablename__ = 'freight_geofences'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('smart_contract_orders.id'), nullable=False)
    
    target_lat = db.Column(db.Float, nullable=False)
    target_lng = db.Column(db.Float, nullable=False)
    radius_meters = db.Column(db.Float, default=500.0)
    
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    
    is_triggered = db.Column(db.Boolean, default=False)
    triggered_at = db.Column(db.DateTime)
