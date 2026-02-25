"""
IoT Predictive Maintenance Models — L3-1641
==========================================
Monitors tractor engine telemetry, vibration, and thermal profiles.
"""

from datetime import datetime
from backend.extensions import db

class AssetTelemetry(db.Model):
    __tablename__ = 'asset_telemetry_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('farm_assets.id'), nullable=False)
    
    engine_rpm = db.Column(db.Float)
    coolant_temp_c = db.Column(db.Float)
    vibration_amplitude = db.Column(db.Float)
    fuel_pressure_psi = db.Column(db.Float)
    
    # Engine hours
    cumulative_hours = db.Column(db.Float)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenancePrediction(db.Model):
    __tablename__ = 'maintenance_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('farm_assets.id'), nullable=False)
    
    # ML Outputs
    failure_probability = db.Column(db.Float) # 0.0 to 1.0
    estimated_remaining_useful_life_hrs = db.Column(db.Float)
    
    predicted_component_failure = db.Column(db.String(100)) # e.g., "Fuel Injector", "Hydraulic Pump"
    criticality_level = db.Column(db.String(20)) # LOW, MEDIUM, CRITICAL
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='PENDING') # PENDING, ACTIONED, IGNORED
