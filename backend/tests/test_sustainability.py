import pytest
from app import app
from backend.extensions import db
from backend.models import User, Farm, CarbonPractice, CreditLedger, AuditRequest, AuditStatus
from backend.services.carbon_service import CarbonService
from backend.services.audit_workflow import AuditWorkflow
from datetime import date, timedelta

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
def setup_data():
    with app.app_context():
        u = User(username='green_farmer', email='gf@test.com')
        f = Farm(name="EcoFarm", location="Hills", user_id=1) # Simplified for test
        db.session.add_all([u, f])
        db.session.commit()
        return u.id, f.id

def test_carbon_lifecycle(setup_data):
    u_id, f_id = setup_data
    
    with app.app_context():
        # 1. Log a practice (No-Till for 50 acres starting 100 days ago)
        start = date.today() - timedelta(days=100)
        practice, err = CarbonService.log_practice(u_id, f_id, "No-Till", 50.0, start)
        assert err is None
        
        # 2. Calculate offsets
        offset = CarbonService.calculate_and_update_offsets(practice.id)
        # Factor for No-Till is 0.52. Offset = 50 * (100/365) * 0.52 = ~7.12
        assert 7.1 <= offset <= 7.2
        
        # 3. Request Audit
        audit, err = AuditWorkflow.initiate_audit(practice.id)
        assert err is None
        assert audit.status == AuditStatus.SUBMITTED.value
        
        # 4. Finalize Audit (Certification)
        success = AuditWorkflow.finalize_audit(audit.id, AuditStatus.CERTIFIED.value, "Excellent evidence.")
        assert success is True
        assert practice.is_verified is True
        
        # 5. Issue Credits
        credit, err = CarbonService.issue_credits(practice.id)
        assert err is None
        assert credit.amount == offset
        assert credit.owner_id == u_id
        assert "AGRI-" in credit.serial_number

def test_impact_summary(setup_data):
    u_id, f_id = setup_data
    with app.app_context():
        start = date.today() - timedelta(days=365)
        # Add two practices
        CarbonService.log_practice(u_id, f_id, "Reforestation", 10.0, start)
        CarbonService.log_practice(u_id, f_id, "Organic Manure", 20.0, start)
        
        CarbonService.calculate_and_update_offsets(1)
        CarbonService.calculate_and_update_offsets(2)
        
        impact = CarbonService.get_user_impact(u_id)
        # Reforestation: 10 * 1 * 2.40 = 24.0
        # Organic Manure: 20 * 1 * 0.35 = 7.0
        # Total = 31.0
        assert impact['total_co2_offset'] == 31.0
        assert impact['practice_count'] == 2
