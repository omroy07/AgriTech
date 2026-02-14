import pytest
from app import app
from backend.extensions import db
from backend.models import User, Farm, WorkerProfile, WorkShift, HarvestLog
from backend.services.payroll_service import PayrollService
from backend.utils.payroll_formulas import PayrollFormulas
from datetime import datetime, timedelta

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
def setup_worker():
    with app.app_context():
        u = User(username='farmer_hr', email='hr@test.com')
        db.session.add(u)
        db.session.commit()
        
        f = Farm(name="Legacy Farms", user_id=u.id)
        db.session.add(f)
        db.session.commit()
        
        worker = WorkerProfile(
            farm_id=f.id,
            name="John Doe",
            base_hourly_rate=20.0,
            piece_rate_kg=2.0
        )
        db.session.add(worker)
        db.session.commit()
        return worker.id

def test_overtime_calculation():
    # 45 hours @ 20/hr, threshold 40, 1.5x multi
    regular, ot = PayrollFormulas.calculate_hourly_pay(45, 20)
    assert regular == 800.0  # 40 * 20
    assert ot == 150.0       # 5 * 20 * 1.5
    
def test_piece_rate_and_tax():
    # 500kg @ 2/kg = 1000
    piece_pay = PayrollFormulas.calculate_piece_pay(500, 2)
    assert piece_pay == 1000.0
    
    # Tax on 6000: slab 5% on full if > 5000 in this simplified model
    tax = PayrollFormulas.calculate_tax(6000)
    assert tax == 300.0 # 5% of 6000

def test_shift_lifecycle(setup_worker):
    worker_id = setup_worker
    with app.app_context():
        # Start shift
        shift, err = PayrollService.clock_in(worker_id)
        assert err is None
        assert shift.shift_status == 'ACTIVE'
        
        # End shift (simulate 8 hours later)
        shift.start_time = datetime.utcnow() - timedelta(hours=8)
        db.session.commit()
        
        completed, err = PayrollService.clock_out(worker_id, break_mins=30)
        assert err is None
        assert completed.total_hours == 7.5

def test_payroll_generation(setup_worker):
    worker_id = setup_worker
    with app.app_context():
        # 1. Add shift
        shift = WorkShift(
            worker_id=worker_id,
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow() - timedelta(days=1) + timedelta(hours=10),
            total_hours=10.0,
            shift_status='COMPLETED'
        )
        db.session.add(shift)
        
        # 2. Add harvest
        log = HarvestLog(worker_id=worker_id, crop_type="Apples", quantity_kg=100.0)
        db.session.add(log)
        db.session.commit()
        
        # 3. Generate
        start = datetime.utcnow() - timedelta(days=2)
        end = datetime.utcnow() + timedelta(days=1)
        payroll, err = PayrollService.generate_worker_payroll(worker_id, start, end)
        
        assert err is None
        # Pay: (10hr * 20) + (100kg * 2) = 200 + 200 = 400
        assert payroll.gross_hourly_pay == 200.0
        assert payroll.gross_piece_pay == 200.0
        assert payroll.net_payable == 400.0 # < 5000 tax free
