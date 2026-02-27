from datetime import datetime
from backend.extensions import db


class IoTSensor(db.Model):
    __tablename__ = "iot_sensors"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(100), unique=True, nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    sensor_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime)
    installed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "farm_id": self.farm_id,
            "user_id": self.user_id,
            "sensor_type": self.sensor_type,
            "location": self.location,
            "is_active": self.is_active,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "installed_at": self.installed_at.isoformat(),
        }


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("iot_sensors.id"), nullable=False)

    soil_moisture = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    nitrogen_level = db.Column(db.Float)
    phosphorus_level = db.Column(db.Float)
    potassium_level = db.Column(db.Float)
    light_intensity = db.Column(db.Float)
    rainfall = db.Column(db.Float)

    battery_level = db.Column(db.Float)
    signal_strength = db.Column(db.Float)

    is_abnormal = db.Column(db.Boolean, default=False)
    alert_message = db.Column(db.String(500))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "soil_moisture": self.soil_moisture,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "ph_level": self.ph_level,
            "nitrogen_level": self.nitrogen_level,
            "phosphorus_level": self.phosphorus_level,
            "potassium_level": self.potassium_level,
            "light_intensity": self.light_intensity,
            "rainfall": self.rainfall,
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
            "is_abnormal": self.is_abnormal,
            "alert_message": self.alert_message,
            "timestamp": self.timestamp.isoformat(),
        }


class SensorAlert(db.Model):
    __tablename__ = "sensor_alerts"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("iot_sensors.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(500), nullable=False)

    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat(),
        }
