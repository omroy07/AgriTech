from datetime import datetime, timedelta
from backend.extensions import db
from backend.models import IoTSensor, SensorReading, SensorAlert, User
from backend.services.alert_registry import AlertRegistry
import logging

logger = logging.getLogger(__name__)


class IoTSensorService:
    @staticmethod
    def register_sensor(user_id, farm_id, sensor_id, sensor_type, location):
        sensor = IoTSensor(
            sensor_id=sensor_id,
            farm_id=farm_id,
            user_id=user_id,
            sensor_type=sensor_type,
            location=location,
        )
        db.session.add(sensor)
        db.session.commit()
        return sensor

    @staticmethod
    def get_user_sensors(user_id):
        return IoTSensor.query.filter_by(user_id=user_id, is_active=True).all()

    @staticmethod
    def get_sensor_by_id(sensor_id):
        return IoTSensor.query.filter_by(id=sensor_id).first()

    @staticmethod
    def update_sensor_status(sensor_id, is_active):
        sensor = IoTSensor.query.filter_by(id=sensor_id).first()
        if sensor:
            sensor.is_active = is_active
            sensor.last_seen = datetime.utcnow()
            db.session.commit()
        return sensor

    @staticmethod
    def receive_reading(sensor_id, reading_data):
        sensor = IoTSensor.query.filter_by(id=sensor_id).first()
        if not sensor:
            return None

        reading = SensorReading(
            sensor_id=sensor_id,
            soil_moisture=reading_data.get("soil_moisture"),
            temperature=reading_data.get("temperature"),
            humidity=reading_data.get("humidity"),
            ph_level=reading_data.get("ph_level"),
            nitrogen_level=reading_data.get("nitrogen_level"),
            phosphorus_level=reading_data.get("phosphorus_level"),
            potassium_level=reading_data.get("potassium_level"),
            light_intensity=reading_data.get("light_intensity"),
            rainfall=reading_data.get("rainfall"),
            battery_level=reading_data.get("battery_level"),
            signal_strength=reading_data.get("signal_strength"),
        )

        reading, is_abnormal, alert_message = IoTSensorService._check_abnormal_readings(
            reading
        )

        sensor.last_seen = datetime.utcnow()
        db.session.add(reading)
        db.session.commit()

        if is_abnormal:
            IoTSensorService._create_alert(sensor, alert_message)

        return reading

    @staticmethod
    def _check_abnormal_readings(reading):
        is_abnormal = False
        alert_message = ""

        if reading.soil_moisture and reading.soil_moisture < 20:
            is_abnormal = True
            reading.is_abnormal = True
            alert_message = "Low soil moisture detected. Consider irrigation."
        elif reading.soil_moisture and reading.soil_moisture > 80:
            is_abnormal = True
            reading.is_abnormal = True
            alert_message = "High soil moisture detected. Risk of waterlogging."

        if reading.temperature and reading.temperature > 40:
            is_abnormal = True
            reading.is_abnormal = True
            alert_message = (
                f"Extreme temperature ({reading.temperature}C) detected. Protect crops."
            )
        elif reading.temperature and reading.temperature < 5:
            is_abnormal = True
            reading.is_abnormal = True
            alert_message = f"Freezing temperature ({reading.temperature}C) detected. Take protective measures."

        if reading.ph_level and (reading.ph_level < 5.0 or reading.ph_level > 8.0):
            is_abnormal = True
            reading.is_abnormal = True
            alert_message = (
                f"Abnormal pH level ({reading.ph_level}). Soil treatment needed."
            )

        if reading.battery_level and reading.battery_level < 20:
            is_abnormal = True
            reading.is_abnormal = True
            alert_message = "Low sensor battery. Replace soon."

        if is_abnormal:
            reading.alert_message = alert_message

        return reading, is_abnormal, alert_message

    @staticmethod
    def _create_alert(sensor, message):
        alert = SensorAlert(
            sensor_id=sensor.id,
            user_id=sensor.user_id,
            alert_type="ENVIRONMENTAL",
            severity="HIGH",
            message=message,
        )
        db.session.add(alert)

        AlertRegistry.register_alert(
            user_id=sensor.user_id,
            title="IoT Sensor Alert",
            message=message,
            category="IOT",
            priority="HIGH",
            group_key=f"sensor_{sensor.id}",
        )

        db.session.commit()

    @staticmethod
    def get_sensor_readings(sensor_id, hours=24):
        threshold = datetime.utcnow() - timedelta(hours=hours)
        return (
            SensorReading.query.filter(
                SensorReading.sensor_id == sensor_id,
                SensorReading.timestamp >= threshold,
            )
            .order_by(SensorReading.timestamp.desc())
            .all()
        )

    @staticmethod
    def get_user_alerts(user_id):
        return (
            SensorAlert.query.filter_by(user_id=user_id, is_resolved=False)
            .order_by(SensorAlert.created_at.desc())
            .all()
        )

    @staticmethod
    def resolve_alert(alert_id):
        alert = SensorAlert.query.filter_by(id=alert_id).first()
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            db.session.commit()
        return alert

    @staticmethod
    def get_historical_data(sensor_id, days=7):
        threshold = datetime.utcnow() - timedelta(days=days)
        readings = (
            SensorReading.query.filter(
                SensorReading.sensor_id == sensor_id,
                SensorReading.timestamp >= threshold,
            )
            .order_by(SensorReading.timestamp.asc())
            .all()
        )

        return {
            "readings": [r.to_dict() for r in readings],
            "stats": IoTSensorService._calculate_stats(readings),
        }

    @staticmethod
    def _calculate_stats(readings):
        if not readings:
            return {}

        stats = {}
        metrics = ["soil_moisture", "temperature", "humidity", "ph_level"]

        for metric in metrics:
            values = [
                getattr(r, metric) for r in readings if getattr(r, metric) is not None
            ]
            if values:
                stats[f"{metric}_avg"] = sum(values) / len(values)
                stats[f"{metric}_min"] = min(values)
                stats[f"{metric}_max"] = max(values)

        return stats

    @staticmethod
    def delete_sensor(sensor_id):
        sensor = IoTSensor.query.filter_by(id=sensor_id).first()
        if sensor:
            sensor.is_active = False
            db.session.commit()
        return sensor
