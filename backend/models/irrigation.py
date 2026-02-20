from datetime import datetime
from backend.extensions import db
from enum import Enum

class ValveStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    FAULT = "fault"

class IrrigationZone(db.Model):
    __tablename__ = 'irrigation_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Configuration
    moisture_threshold_min = db.Column(db.Float, default=30.0) # Trigger "On" below this
    moisture_threshold_max = db.Column(db.Float, default=70.0) # Trigger "Off" above this
    
    current_valve_status = db.Column(db.String(20), default=ValveStatus.CLOSED.value)
    last_activation = db.Column(db.DateTime)
    
    # Automation Toggle
    auto_mode = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Change logs and sensor data
    sensor_logs = db.relationship('SensorLog', backref='zone', lazy='dynamic', cascade='all, delete-orphan')
    
    # Fertigation (L3-1547)
    fertigation_enabled = db.Column(db.Boolean, default=False)
    fertigation_valve_status = db.Column(db.String(20), default=ValveStatus.CLOSED.value)
    chemical_concentration = db.Column(db.Float, default=0.0) # ppm
    washout_risk_threshold = db.Column(db.Float, default=0.7)
    
    fertigation_logs = db.relationship('FertigationLog', backref='zone', lazy='dynamic', cascade='all, delete-orphan')
    
    # Sustainability (L3-1558)
    total_water_withdrawn = db.Column(db.Float, default=0.0) # Liters
    electricity_usage_kwh = db.Column(db.Float, default=0.0)

    def to_dict(self):
        data = {
            'id': self.id,
            'farm_id': self.farm_id,
            'name': self.name,
            'description': self.description,
            'moisture_threshold_min': self.moisture_threshold_min,
            'moisture_threshold_max': self.moisture_threshold_max,
            'status': self.current_valve_status,
            'auto_mode': self.auto_mode,
            'last_activation': self.last_activation.isoformat() if self.last_activation else None,
            'fertigation': {
                'enabled': self.fertigation_enabled,
                'status': self.fertigation_valve_status,
                'concentration': self.chemical_concentration
            }
        }
        return data

class FertigationLog(db.Model):
    __tablename__ = 'fertigation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('irrigation_zones.id'), nullable=False)
    
    injectant_type = db.Column(db.String(50)) # Nitrogen, Phosphorus, Mix
    concentration_ppm = db.Column(db.Float)
    volume_liters = db.Column(db.Float)
    
    # Runoff Metrics
    washout_risk_score = db.Column(db.Float) # Calculated at injection time
    weather_impact_factor = db.Column(db.Float) # From rain forecasts
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'injectant': self.injectant_type,
            'ppm': self.concentration_ppm,
            'volume': self.volume_liters,
            'risk': self.washout_risk_score,
            'timestamp': self.timestamp.isoformat()
        }

class SensorLog(db.Model):
    __tablename__ = 'sensor_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('irrigation_zones.id'), nullable=False)
    
    moisture = db.Column(db.Float)    # percentage
    temperature = db.Column(db.Float) # Celsius
    ph_level = db.Column(db.Float)    # 0-14
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'zone_id': self.zone_id,
            'moisture': self.moisture,
            'temperature': self.temperature,
            'ph_level': self.ph_level,
            'timestamp': self.timestamp.isoformat()
        }

class IrrigationSchedule(db.Model):
    __tablename__ = 'irrigation_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('irrigation_zones.id'), nullable=False)
    
    start_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    days_of_week = db.Column(db.String(50)) # e.g., "mon,wed,fri"
    
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
