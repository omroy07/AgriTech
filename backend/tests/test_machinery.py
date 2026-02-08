import pytest
from app import app
from backend.extensions import db
from backend.models import User, Equipment, EngineHourLog, MaintenanceCycle, MaintenanceStatus
from backend.services.machinery_service import MachineryService
from backend.utils.fleet_logic import FleetLogic

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
def setup_machinery():
    with app.app_context():
        u = User(username='owner1', email='o1@test.com')
        db.session.add(u)
        db.session.commit()
        
        eq = Equipment(
            name="JD 5050 Tractor",
            owner_id=u.id,
            category="Tractor",
            description="High power tractor",
            daily_rate=1500.0,
            security_deposit=5000.0
        )
        db.session.add(eq)
        db.session.commit()
        return eq.id

def test_usage_billing_logic():
    # Standard 8h usage
    cost = FleetLogic.calculate_usage_cost(100.0, 5)
    assert cost == 500.0
    
    # Overage (10h usage, 2h overage at 1.5x)
    # (8 * 100) + (2 * 100 * 1.5) = 800 + 300 = 1100
    cost = FleetLogic.calculate_usage_cost(100.0, 10)
    assert cost == 1100.0

def test_machinery_health_tracking(setup_machinery):
    eq_id = setup_machinery
    with app.app_context():
        # 1. Log some hours
        MachineryService.log_engine_hours(eq_id, 100.0, 150.0) # 50h used
        
        # 2. Schedule maintenance with 40h interval
        MachineryService.schedule_maintenance(eq_id, "Oil Change", 40.0)
        
        # 3. Check health: should be overdue since 50h > 40h
        health = MachineryService.get_fleet_health(eq_id)
        assert health['total_hours'] == 50.0
        assert health['maintenance'][0]['is_overdue'] is True
        assert health['maintenance'][0]['remaining_hours'] == -10.0

def test_damage_and_repair_cascade(setup_machinery):
    eq_id = setup_machinery
    with app.app_context():
        # Mock booking ID
        def mock_book():
            from backend.models.equipment import RentalBooking
            from datetime import date
            b = RentalBooking(equipment_id=eq_id, user_id=1, start_date=date.today(), end_date=date.today(), total_price=1000)
            db.session.add(b)
            db.session.commit()
            return b.id
            
        book_id = mock_book()
        
        # 1. Report Damage
        report, err = MachineryService.report_damage(book_id, eq_id, "Broken hydraulic pump during use.", 2500.0)
        assert err is None
        assert report.escrow_hold_amount == 2500.0
        
        # 2. Check auto-created repair order
        from backend.models.machinery import RepairOrder
        repair = RepairOrder.query.filter_by(damage_report_id=report.id).first()
        assert repair.status == "pending"
        
        # 3. Complete Repair
        success, _ = MachineryService.complete_repair(repair.id, 2400.0, "Farmer's Garage Inc")
        assert success is True
        assert repair.status == "fixed"
        assert repair.actual_cost == 2400.0
