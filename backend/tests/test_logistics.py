import pytest
from app import app
from backend.extensions import db
from backend.models import User, DriverProfile, DeliveryVehicle, TransportRoute
from backend.services.logistics_service import LogisticsService
from backend.utils.route_formulas import RouteFormulas
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
def setup_logistics():
    with app.app_context():
        u = User(username='fleet_mgr', email='fleet@test.com')
        db.session.add(u)
        db.session.commit()
        
        driver = DriverProfile(user_id=u.id, license_number="DL-123456", status='AVAILABLE')
        db.session.add(driver)
        
        vehicle = DeliveryVehicle(
            plate_number="TRUCK-001",
            vehicle_type="Refrigerator Truck",
            capacity_kg=5000.0,
            avg_fuel_consumption=15.0, # L/100km
            status='IDLE'
        )
        db.session.add(vehicle)
        db.session.commit()
        
        return driver.id, vehicle.id

def test_haversine_distance():
    # Distance between Taj Mahal (27.1751, 78.0421) and Red Fort (28.6562, 77.2410)
    # Approx 178km
    dist = RouteFormulas.calculate_haversine_distance(27.1751, 78.0421, 28.6562, 77.2410)
    assert 170 < dist < 190

def test_fuel_consumption_with_load():
    # distance 200km, avg 10L/100km, load 5000kg, max 5000kg
    # base = (200/100) * 10 = 20L
    # factor = 1 + (5000/5000)*0.15 = 1.15
    # total = 20 * 1.15 = 23.0L
    fuel = RouteFormulas.estimate_fuel_consumption(200, 10, 5000, 5000)
    assert fuel == 23.0

def test_dispatch_lifecycle(setup_logistics):
    driver_id, vehicle_id = setup_logistics
    with app.app_context():
        # 1. Create Dispatch
        route, err = LogisticsService.create_dispatch(
            driver_id, vehicle_id, "Warehouse A", "Organic Market", 2500.0,
            coords={'origin': [27.0, 78.0], 'dest': [28.0, 77.0]}
        )
        assert err is None
        assert route.status == 'PENDING'
        
        # Verify statuses changed
        d = DriverProfile.query.get(driver_id)
        v = DeliveryVehicle.query.get(vehicle_id)
        assert d.status == 'ON_TRIP'
        assert v.status == 'ACTIVE'
        
        # 2. Start Route
        success, err = LogisticsService.start_route(route.id)
        assert success
        assert route.status == 'IN_TRANSIT'
        
        # 3. Complete Route
        success, err = LogisticsService.complete_route(route.id, 180.0)
        assert success
        assert route.status == 'COMPLETED'
        assert d.status == 'AVAILABLE'
        assert v.status == 'IDLE'
        assert v.mileage == 180.0
