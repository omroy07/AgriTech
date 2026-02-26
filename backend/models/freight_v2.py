"""
Freight Pairing & Vehicle Network Models — L3-1644
=================================================
Manages autonomous vehicle pairing for supply chain orders.
"""

from datetime import datetime
from backend.extensions import db

class AutonomousVehicle(db.Model):
    __tablename__ = 'autonomous_vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50)) # DRONE, TRUCK, AGV
    
    current_capacity_kg = db.Column(db.Float)
    battery_level_pct = db.Column(db.Float)
    
    # Status: IDLE, IN_TRANSIT, CHARGING, MAINTENANCE
    status = db.Column(db.String(20), default='IDLE')
    
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    
    last_ping = db.Column(db.DateTime, default=datetime.utcnow)

class VehicleMission(db.Model):
    __tablename__ = 'vehicle_missions'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('autonomous_vehicles.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('smart_contract_orders.id'), nullable=False)
    
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    distance_traveled_km = db.Column(db.Float, default=0.0)
    energy_consumed_kwh = db.Column(db.Float, default=0.0)
