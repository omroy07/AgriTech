from backend.celery_app import celery_app
from backend.models.climate import SensorNode, TelemetryLog, ClimateZone
from backend.extensions import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.check_sensor_health')
def check_sensor_health_task():
    """
    Scans all sensor nodes for heartbeat timeouts (stale sensors).
    """
    timeout = datetime.utcnow() - timedelta(minutes=30)
    stale_nodes = SensorNode.query.filter(
        SensorNode.is_active == True,
        (SensorNode.last_heartbeat < timeout) | (SensorNode.last_heartbeat.is_(None))
    ).all()
    
    for node in stale_nodes:
        logger.warning(f"Sensor Node Offline: UID {node.uid} (Zone #{node.zone_id})")
        # In real app: send notification to farmer
        
    return {'status': 'success', 'stale_nodes': len(stale_nodes)}

@celery_app.task(name='tasks.generate_env_report')
def generate_env_report_task():
    """
    Aggregates daily environmental trends (Avg Temp, Humidity) for each zone.
    """
    yesterday = datetime.utcnow() - timedelta(days=1)
    zones = ClimateZone.query.all()
    
    reports_generated = 0
    for zone in zones:
        # Simple aggregation for demonstration
        node_ids = [n.id for n in zone.nodes]
        avg_data = db.session.query(
            db.func.avg(TelemetryLog.temperature),
            db.func.avg(TelemetryLog.humidity)
        ).filter(
            TelemetryLog.node_id.in_(node_ids),
            TelemetryLog.timestamp >= yesterday
        ).first()
        
        if avg_data and avg_data[0]:
            logger.info(f"Daily Report [Zone {zone.name}]: Avg Temp {avg_data[0]:.2f}C, Avg Hum {avg_data[1]:.2f}%")
            reports_generated += 1
            
    return {'status': 'success', 'reports': reports_generated}

@celery_app.task(name='tasks.purge_old_telemetry')
def purge_old_telemetry_task():
    """
    Cleans up telemetry logs older than 30 days to save space.
    """
    retention_period = datetime.utcnow() - timedelta(days=30)
    deleted = TelemetryLog.query.filter(TelemetryLog.timestamp < retention_period).delete()
    db.session.commit()
    
    return {'status': 'success', 'records_purged': deleted}
