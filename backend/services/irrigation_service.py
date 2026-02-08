from datetime import datetime
from backend.extensions import db
from backend.models.irrigation import IrrigationZone, SensorLog, ValveStatus
from backend.utils.iot_simulator import IoTSimulator
import logging

logger = logging.getLogger(__name__)

class IrrigationService:
    @staticmethod
    def process_telemetry(zone_id, moisture, temperature, ph):
        """Store new sensor data and evaluate automation triggers"""
        try:
            zone = IrrigationZone.query.get(zone_id)
            if not zone:
                return None, "Zone not found"
            
            # 1. Log the data
            log = SensorLog(
                zone_id=zone_id,
                moisture=moisture,
                temperature=temperature,
                ph_level=ph
            )
            db.session.add(log)
            
            # 2. Evaluate Automation if Enabled
            if zone.auto_mode:
                IrrigationService._evaluate_automation(zone, moisture)
                
            db.session.commit()
            return log, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"Telemetry processing failed: {str(e)}")
            return None, str(e)

    @staticmethod
    def _evaluate_automation(zone, current_moisture):
        """Core logic for opening/closing valves based on thresholds"""
        # If moisture drops below min -> Open Valve
        if current_moisture < zone.moisture_threshold_min:
            if zone.current_valve_status != ValveStatus.OPEN.value:
                zone.current_valve_status = ValveStatus.OPEN.value
                zone.last_activation = datetime.utcnow()
                logger.info(f"Automation: Opening valve for Zone {zone.name} (Moisture: {current_moisture}%)")
        
        # If moisture exceeds max -> Close Valve
        elif current_moisture > zone.moisture_threshold_max:
            if zone.current_valve_status != ValveStatus.CLOSED.value:
                zone.current_valve_status = ValveStatus.CLOSED.value
                logger.info(f"Automation: Closing valve for Zone {zone.name} (Moisture: {current_moisture}%)")

    @staticmethod
    def manual_override(zone_id, status):
        """Force valve state regardless of automation"""
        zone = IrrigationZone.query.get(zone_id)
        if zone:
            zone.current_valve_status = status
            zone.auto_mode = False # Disable auto on manual intervention
            if status == ValveStatus.OPEN.value:
                zone.last_activation = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_zone_analytics(zone_id):
        """Get 24h history and average metrics"""
        from sqlalchemy import func
        logs = SensorLog.query.filter_by(zone_id=zone_id).order_by(SensorLog.timestamp.desc()).limit(24).all()
        
        avg_moisture = db.session.query(func.avg(SensorLog.moisture)).filter_by(zone_id=zone_id).scalar() or 0
        
        return {
            'history': [l.to_dict() for l in logs],
            'average_moisture': round(float(avg_moisture), 2)
        }
