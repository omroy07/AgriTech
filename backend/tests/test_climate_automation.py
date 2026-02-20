import pytest
from app import app
from backend.extensions import db
from backend.models import User, Farm, ClimateZone, SensorNode, TelemetryLog, AutomationTrigger
from backend.services.climate_service import ClimateService
from backend.utils.climate_formulas import ClimateFormulas
import json

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def setup_greenhouse():
    with app.app_context():
        u = User(username='iot_admin', email='iot@test.com')
        db.session.add(u)
        db.session.commit()
        
        f = Farm(name="Smart Acres", user_id=u.id)
        db.session.add(f)
        db.session.commit()
        
        zone = ClimateService.setup_zone(f.id, "Main Greenhouse", {
            'temp_min': 20.0, 'temp_max': 30.0,
            'hum_min': 50.0, 'hum_max': 70.0,
            'co2': 800.0
        })
        
        node = SensorNode(zone_id=zone.id, uid="NODE-001-CLIMATE", node_type="ESP32")
        db.session.add(node)
        
        # Add a trigger for high temp
        trigger = AutomationTrigger(
            zone_id=zone.id,
            name="Heat Safety",
            actor_type="VENTILATION",
            condition_json=json.dumps({"metric": "temp", "operator": ">", "value": 30}),
            action_json=json.dumps({"command": "ON", "speed": "HIGH"})
        )
        db.session.add(trigger)
        db.session.commit()
        
        return zone.id, node.uid

def test_vpd_calculation():
    # 25C, 60% Humidity
    vpd = ClimateFormulas.calculate_vpd(25, 60)
    # SVP @ 25C ≈ 3.167 kPa
    # AVP = 3.167 * 0.6 = 1.9 kPa
    # VPD = 3.167 - 1.9 = 1.267 kPa
    assert 1.25 < vpd < 1.30
    assert ClimateFormulas.get_vpd_status(vpd) == "VEGETATIVE"

def test_telemetry_and_trigger_cascade(setup_greenhouse):
    zone_id, node_uid = setup_greenhouse
    with app.app_context():
        # 1. Post telemetry that breaches threshold (32C > 30C)
        data = {
            'temp': 32.5,
            'humidity': 55.0,
            'co2': 450.0,
            'light': 12000.0,
            'battery': 85.0,
            'rssi': -65.0
        }
        log, err = ClimateService.process_telemetry(node_uid, data)
        assert err is None
        assert log.temperature == 32.5
        
        # 2. Check if trigger was hit
        trigger = AutomationTrigger.query.filter_by(zone_id=zone_id).first()
        assert trigger.last_triggered is not None
        
        # 3. Verify analytics
        analytics = ClimateService.get_zone_analytics(zone_id)
        assert analytics['vpd'] > 0
        assert analytics['latest']['temp'] == 32.5

def test_sensor_offline_detection(setup_greenhouse):
    zone_id, node_uid = setup_greenhouse
    from backend.tasks.climate_tasks import check_sensor_health_task
    from datetime import datetime, timedelta
    
    with app.app_context():
        node = SensorNode.query.filter_by(uid=node_uid).first()
        # Set heartbeat to 1 hour ago
        node.last_heartbeat = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        
        result = check_sensor_health_task()
        assert result['stale_nodes'] == 1
