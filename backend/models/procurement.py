from datetime import datetime
from backend.extensions import db
from enum import Enum

class OrderStatus(Enum):
    PROPOSED = "proposed"      # Initial request from buyer
    VETTED = "vetted"          # Price confirmed/negotiated
    PAYMENT_PENDING = "payment_pending"
    SHIPMENT = "shipment"      # In transit
    DELIVERED = "delivered"
    SETTLED = "settled"        # Funds released to vendor
    CANCELLED = "cancelled"

class VendorProfile(db.Model):
    __tablename__ = 'vendor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    registration_id = db.Column(db.String(50), unique=True)
    rating = db.Column(db.Float, default=5.0)
    
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('ProcurementItem', backref='vendor', lazy=True)

class ProcurementItem(db.Model):
    __tablename__ = 'procurement_items'
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_profiles.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50)) # e.g., Fertilizers, Seeds, Equipment
    base_price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='unit') # kg, tonne, packet
    stock = db.Column(db.Float, default=0)
    
    # JSON for volume pricing: [{"min": 100, "price": 45}, {"min": 500, "price": 40}]
    volume_pricing = db.Column(db.Text) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BulkOrder(db.Model):
    __tablename__ = 'bulk_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_profiles.id'), nullable=False)
    
    item_id = db.Column(db.Integer, db.ForeignKey('procurement_items.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    
    unit_price = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    tax_amount = db.Column(db.Float)
    shipping_cost = db.Column(db.Float, default=0)
    
    status = db.Column(db.String(20), default=OrderStatus.PROPOSED.value)
    
    delivery_address = db.Column(db.Text)
    tracking_number = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    events = db.relationship('OrderEvent', backref='order', lazy=True)

class OrderEvent(db.Model):
    __tablename__ = 'order_events'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('bulk_orders.id'), nullable=False)
    
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20))
    comment = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
