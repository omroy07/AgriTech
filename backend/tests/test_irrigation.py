import pytest
from app import app
from backend.extensions import db
from backend.models import User, Farm, IrrigationZone, SensorLog, ValveStatus
from backend.services.irrigation_service import IrrigationService
from datetime import datetime

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
def setup_zone():
    with app.app_context():
        # Setup boilerplate
        u = User(username='testirr', email='ti@test.com')
        f = Farm(name="IoT Farm", location="Cloud", user_id=1)
        db.session.add_all([u, f])
        db.session.commit()
        
        zone = IrrigationZone(
            farm_id=f.id,
            name="Alpha Block",
            moisture_threshold_min=35.0,
            moisture_threshold_max=75.0,
            auto_mode=True
        )
        db.session.add(zone)
        db.session.commit()
        return zone.id

def test_irrigation_automation_on(setup_zone):
    zone_id = setup_zone
    with app.app_context():
        # 1. Simulate Moisture drop (below 35.0)
        log, err = IrrigationService.process_telemetry(zone_id, 30.0, 25.0, 6.8)
        assert err is None
        
        # 2. Check if valve opened automatically
        zone = IrrigationZone.query.get(zone_id)
        assert zone.current_valve_status == ValveStatus.OPEN.value
        assert zone.last_activation is not None

def test_irrigation_automation_off(setup_zone):
    zone_id = setup_zone
    with app.app_context():
        # Open valve first
        zone = IrrigationZone.query.get(zone_id)
        zone.current_valve_status = ValveStatus.OPEN.value
        db.session.commit()
        
        # 1. Simulate Moisture rise (above 75.0)
        IrrigationService.process_telemetry(zone_id, 80.0, 25.0, 6.8)
        
        # 2. Check if valve closed
        assert zone.current_valve_status == ValveStatus.CLOSED.value

def test_manual_override_logic(setup_zone):
    zone_id = setup_zone
    with app.app_context():
        # 1. Force Open
        IrrigationService.manual_override(zone_id, ValveStatus.OPEN.value)
        
        zone = IrrigationZone.query.get(zone_id)
        assert zone.current_valve_status == ValveStatus.OPEN.value
        assert zone.auto_mode is False # Manual override should kill auto
        
        # 2. Telemetry should NOT close it anymore because auto is false
        IrrigationService.process_telemetry(zone_id, 90.0, 25.0, 6.8)
        assert zone.current_valve_status == ValveStatus.OPEN.value # Remains open
