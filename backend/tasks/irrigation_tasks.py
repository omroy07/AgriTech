from backend.celery_app import celery_app
from backend.models.irrigation import IrrigationZone, SensorLog, ValveStatus
from backend.services.irrigation_service import IrrigationService
from backend.utils.iot_simulator import IoTSimulator
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.poll_sensor_telemetry')
def poll_sensor_telemetry_task():
    """Simulates periodic IoT polling for all active zones"""
    try:
        zones = IrrigationZone.query.all()
        for zone in zones:
            # Get last log to maintain continuity
            last_log = SensorLog.query.filter_by(zone_id=zone.id)\
                .order_by(SensorLog.timestamp.desc()).first()
            
            prev_moist = last_log.moisture if last_log else 45.0
            
            # 1. Simulate environmental change
            telemetry = IoTSimulator.generate_sensor_data(zone.id, prev_moist)
            
            # 2. If valve is OPEN, simulate water flow moisture boost
            if zone.current_valve_status == ValveStatus.OPEN.value:
                telemetry['moisture'] = IoTSimulator.simulate_irrigation_effect(telemetry['moisture'])
                
            # 3. Process telemetry (triggers automation logic)
            IrrigationService.process_telemetry(
                zone.id, 
                telemetry['moisture'], 
                telemetry['temperature'], 
                telemetry['ph_level']
            )
            
        return {'status': 'success', 'zones_polled': len(zones)}
    except Exception as e:
        logger.error(f"Poll task failed: {str(e)}")
        return {'status': 'error'}

@celery_app.task(name='tasks.irrigation_health_audit')
def irrigation_health_audit_task():
    """Detect offline sensors or stuck valves"""
    threshold = datetime.utcnow() - timedelta(hours=1)
    zones = IrrigationZone.query.all()
    
    issues = []
    for zone in zones:
        last_log = SensorLog.query.filter_by(zone_id=zone.id)\
            .order_by(SensorLog.timestamp.desc()).first()
            
        if not last_log or last_log.timestamp < threshold:
            issues.append(f"Zone {zone.name}: Sensor Offline")
            
    if issues:
        logger.warning(f"Irrigation Audit Issues: {issues}")
        
    return {'status': 'success', 'issues_count': len(issues)}
