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

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'name': self.name,
            'description': self.description,
            'moisture_threshold_min': self.moisture_threshold_min,
            'moisture_threshold_max': self.moisture_threshold_max,
            'status': self.current_valve_status,
            'auto_mode': self.auto_mode,
            'last_activation': self.last_activation.isoformat() if self.last_activation else None
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
