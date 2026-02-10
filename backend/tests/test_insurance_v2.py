import pytest
from app import app
from backend.extensions import db
from backend.models import User, Farm, CropPolicy, ClaimRequest, AdjusterNote, PolicyStatus, ClaimStatus
from backend.services.insurance_service import InsuranceService
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
def setup_insurance():
    with app.app_context():
        u = User(username='farmer1', email='f1@test.com')
        adj = User(username='adj1', email='a1@test.com')
        f = Farm(name="Legacy Farm", user_id=1)
        db.session.add_all([u, adj, f])
        db.session.commit()
        return u.id, adj.id, f.id

def test_full_insurance_lifecycle(setup_insurance):
    user_id, adj_id, farm_id = setup_insurance
    
    with app.app_context():
        # 1. Test Underwriting
        start = date.today()
        end = start + timedelta(days=90)
        policy, err = InsuranceService.issue_policy(user_id, farm_id, "Rice", 10000.0, start, end)
        
        assert err is None
        assert policy.status == PolicyStatus.ACTIVE.value
        assert policy.premium_paid > 0
        
        # 2. Test Claim Submission
        # Rice sensitivity is 60. Expected yield for 10k coverage = 1000kg.
        # Loss of 400kg is 40% loss ratio.
        claim, err = InsuranceService.file_claim(policy.id, 400.0, "Extended Drought Season")
        assert err is None
        assert claim.status == ClaimStatus.SUBMITTED.value
        assert claim.claim_amount > 0
        
        # 3. Test Adjudication (Approval)
        success, err = InsuranceService.process_claim(claim.id, adj_id, "approve", "Verified via Satellite IR data.", 0.9)
        assert success is True
        assert claim.status == ClaimStatus.PAID.value
        
        # Check Payout Ledger
        from backend.models.insurance_v2 import PayoutLedger
        payout = PayoutLedger.query.filter_by(claim_id=claim.id).first()
        assert payout is not None
        assert payout.amount == claim.claim_amount

def test_claim_reversal_logic(setup_insurance):
    user_id, adj_id, farm_id = setup_insurance
    with app.app_context():
        start = date.today()
        end = start + timedelta(days=30)
        policy, _ = InsuranceService.issue_policy(user_id, farm_id, "Wheat", 5000.0, start, end)
        claim, _ = InsuranceService.file_claim(policy.id, 100.0, "Pest Damage")
        
        # Adjuster Rejects
        InsuranceService.process_claim(claim.id, adj_id, "reject", "Insufficient evidence of pests.", 0.2)
        assert claim.status == ClaimStatus.REJECTED.value
