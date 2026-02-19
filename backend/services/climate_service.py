from datetime import datetime
import json
from backend.extensions import db
from backend.models.climate import ClimateZone, SensorNode, TelemetryLog, AutomationTrigger
from backend.utils.climate_formulas import ClimateFormulas

class ClimateService:
    @staticmethod
    def process_telemetry(node_uid, data):
        """
        Ingests IoT telemetry, logs it, and evaluates automation triggers.
        """
        node = SensorNode.query.filter_by(uid=node_uid).first()
        if not node:
            return None, "Node not registered"
        
        # 1. Log Telemetry
        log = TelemetryLog(
            node_id=node.id,
            temperature=data.get('temp'),
            humidity=data.get('humidity'),
            co2_level=data.get('co2'),
            light_intensity=data.get('light'),
            battery_level=data.get('battery'),
            signal_strength=data.get('rssi')
        )
        node.last_heartbeat = datetime.utcnow()
        db.session.add(log)
        
        # 2. Evaluate Triggers
        triggered_actions = ClimateService.evaluate_triggers(node.zone_id, data)
        
        db.session.commit()
        return log, None

    @staticmethod
    def evaluate_triggers(zone_id, current_data):
        """
        Checks current telemetry against zone triggers.
        """
        triggers = AutomationTrigger.query.filter_by(zone_id=zone_id, is_enabled=True).all()
        fired = []
        
        for trigger in triggers:
            condition = json.loads(trigger.condition_json)
            metric = condition.get('metric')
            value = current_data.get(metric)
            
            if value is None: continue
            
            # Simple threshold check
            op = condition.get('operator')
            threshold = condition.get('value')
            
            is_fired = False
            if op == '>' and value > threshold: is_fired = True
            elif op == '<' and value < threshold: is_fired = True
            elif op == '==' and value == threshold: is_fired = True
            
            if is_fired:
                trigger.last_triggered = datetime.utcnow()
                fired.append({
                    'id': trigger.id,
                    'actor': trigger.actor_type,
                    'action': json.loads(trigger.action_json)
                })
        
        return fired

    @staticmethod
    def get_zone_analytics(zone_id, hours=24):
        """
        Aggregates telemetry and calculates scientific metrics for a zone.
        """
        # Get all nodes in zone
        node_ids = [n.id for n in SensorNode.query.filter_by(zone_id=zone_id).all()]
        
        # Fetch logs
        logs = TelemetryLog.query.filter(
            TelemetryLog.node_id.in_(node_ids)
        ).order_by(TelemetryLog.timestamp.desc()).limit(100).all()
        
        if not logs:
            return None
            
        latest = logs[0]
        vpd = ClimateFormulas.calculate_vpd(latest.temperature, latest.humidity)
        hi = ClimateFormulas.calculate_heat_index(latest.temperature, latest.humidity)
        
        return {
            'latest': latest.to_dict(),
            'vpd': vpd,
            'vpd_status': ClimateFormulas.get_vpd_status(vpd),
            'heat_index': hi,
            'history': [l.to_dict() for l in logs]
        }

    @staticmethod
    def setup_zone(farm_id, name, targets):
        """Initializes a new climate zone with target thresholds."""
        zone = ClimateZone(
            farm_id=farm_id,
            name=name,
            target_temp_min=targets.get('temp_min'),
            target_temp_max=targets.get('temp_max'),
            target_humidity_min=targets.get('hum_min'),
            target_humidity_max=targets.get('hum_max'),
            target_co2=targets.get('co2')
        )
        db.session.add(zone)
        db.session.commit()
        return zone
