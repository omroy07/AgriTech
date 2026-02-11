from datetime import datetime
from backend.extensions import db
import json

class ClimateZone(db.Model):
    __tablename__ = 'climate_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False) # e.g., North Greenhouse, Seedling Area
    description = db.Column(db.Text)
    
    # Target Thresholds
    target_temp_min = db.Column(db.Float)
    target_temp_max = db.Column(db.Float)
    target_humidity_min = db.Column(db.Float)
    target_humidity_max = db.Column(db.Float)
    target_co2 = db.Column(db.Float) # ppm
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    nodes = db.relationship('SensorNode', backref='zone', lazy='dynamic')
    triggers = db.relationship('AutomationTrigger', backref='zone', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'name': self.name,
            'description': self.description,
            'targets': {
                'temp': [self.target_temp_min, self.target_temp_max],
                'humidity': [self.target_humidity_min, self.target_humidity_max],
                'co2': self.target_co2
            },
            'created_at': self.created_at.isoformat()
        }

class SensorNode(db.Model):
    __tablename__ = 'sensor_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('climate_zones.id'), nullable=False)
    uid = db.Column(db.String(50), unique=True, nullable=False) # IoT Unique ID
    
    node_type = db.Column(db.String(50)) # e.g., ESP32-Climate, LoRa-Soil
    firmware_version = db.Column(db.String(20))
    
    is_active = db.Column(db.Boolean, default=True)
    last_heartbeat = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    telemetry = db.relationship('TelemetryLog', backref='node', lazy='dynamic')

class TelemetryLog(db.Model):
    __tablename__ = 'telemetry_logs'
    
    id = db.Column(db.LongInteger if hasattr(db, 'LongInteger') else db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('sensor_nodes.id'), nullable=False)
    
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    co2_level = db.Column(db.Float)
    light_intensity = db.Column(db.Float) # Lux
    
    # Soil metrics (if multi-node)
    soil_moisture = db.Column(db.Float)
    soil_ph = db.Column(db.Float)
    
    battery_level = db.Column(db.Float) # Percentage
    signal_strength = db.Column(db.Float) # dBm
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'node_id': self.node_id,
            'temp': self.temperature,
            'humidity': self.humidity,
            'co2': self.co2_level,
            'light': self.light_intensity,
            'timestamp': self.timestamp.isoformat()
        }

class AutomationTrigger(db.Model):
    __tablename__ = 'automation_triggers'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('climate_zones.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    actor_type = db.Column(db.String(50)) # e.g., VENTILATION, IRRIGATION, LIGHTING
    
    # Clause logic: e.g., {"metric": "temp", "operator": ">", "value": 30}
    condition_json = db.Column(db.Text, nullable=False)
    action_json = db.Column(db.Text, nullable=False) # e.g., {"command": "ON", "duration": 300}
    
    is_enabled = db.Column(db.Boolean, default=True)
    last_triggered = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'actor': self.actor_type,
            'condition': json.loads(self.condition_json),
            'action': json.loads(self.action_json),
            'enabled': self.is_enabled,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }
