"""
Precision Irrigation & Aquifer Management Models — L3-1640
==========================================================
Implements high-resolution water stress indexing and automated 
irrigation valve orchestration.
"""

from datetime import datetime
from backend.extensions import db

class WaterStressIndex(db.Model):
    __tablename__ = 'water_stress_index_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    zone_id = db.Column(db.String(50), nullable=False)
    
    # Soil metrics
    moisture_level_pct = db.Column(db.Float, nullable=False)
    evapotranspiration_rate = db.Column(db.Float)
    root_zone_salinity = db.Column(db.Float)
    
    # Engine calculated
    stress_score = db.Column(db.Float) # 0.0 to 1.0
    irrigation_required_liters = db.Column(db.Float)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'zone': self.zone_id,
            'moisture': self.moisture_level_pct,
            'stress': self.stress_score,
            'timestamp': self.recorded_at.isoformat()
        }

class IrrigationValveAutomation(db.Model):
    __tablename__ = 'irrigation_valve_automation'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    valve_id = db.Column(db.String(50), nullable=False)
    
    status = db.Column(db.String(20), default='IDLE') # OPEN, CLOSED, FAULT
    flow_rate_lpm = db.Column(db.Float, default=0.0)
    total_volume_injected_l = db.Column(db.Float, default=0.0)
    
    last_action = db.Column(db.String(50))
    last_action_at = db.Column(db.DateTime)
    
    # Link to stress event
    triggered_by_event_id = db.Column(db.Integer, db.ForeignKey('water_stress_index_logs.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'valve': self.valve_id,
            'status': self.status,
            'flow_rate': self.flow_rate_lpm,
            'total_vol': self.total_volume_injected_l
        }

class AquiferMonitoring(db.Model):
    __tablename__ = 'aquifer_monitoring_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    aquifer_id = db.Column(db.String(50), nullable=False)
    
    current_water_level_m = db.Column(db.Float)
    recharge_rate_lps = db.Column(db.Float)
    
    # Sustainability indicator
    is_critical_depletion = db.Column(db.Boolean, default=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

