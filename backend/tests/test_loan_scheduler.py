import pytest
from app import app
from backend.extensions import db
from backend.models import User, LoanRequest, RepaymentSchedule, PaymentHistory
from backend.services.loan_scheduler import LoanScheduler
from backend.utils.credit_scoring import CreditScoring
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
def setup_loan():
    with app.app_context():
        u = User(username='borrower1', email='b1@test.com')
        db.session.add(u)
        db.session.commit()
        
        loan = LoanRequest(
            user_id=u.id,
            loan_type='Crop Cultivation',
            amount=100000.0,
            status='APPROVED'
        )
        db.session.add(loan)
        db.session.commit()
        return loan.id

def test_emi_calculation_accuracy(setup_loan):
    loan_id = setup_loan
    with app.app_context():
        # Generate schedule: 100k principal, 12% annual, 12 months
        schedules, err = LoanScheduler.generate_emi_schedule(loan_id, 100000, 12.0, 12)
        assert err is None
        assert len(schedules) == 12
        
        # Verify EMI formula
        # For 100k @ 12% for 12 months, EMI should be ~8884.88
        first_emi = schedules[0].total_emi
        assert 8880 < first_emi < 8890
        
        # Verify amortization (balance should reduce to ~0)
        last_schedule = schedules[-1]
        assert last_schedule.outstanding_balance < 1.0

def test_payment_processing_and_penalties(setup_loan):
    loan_id = setup_loan
    with app.app_context():
        schedules, _ = LoanScheduler.generate_emi_schedule(loan_id, 50000, 10.0, 6)
        
        # Simulate late payment (10 days late)
        first_schedule = schedules[0]
        first_schedule.due_date = date.today() - timedelta(days=10)
        db.session.commit()
        
        payment, err = LoanScheduler.record_payment(loan_id, first_schedule.id, first_schedule.total_emi)
        assert err is None
        assert payment.late_fee > 0
        assert payment.penalty_interest > 0
        
        # Verify schedule marked as paid
        assert first_schedule.is_paid is True

def test_default_risk_calculation():
    # Test risk scoring formulas
    prob = CreditScoring.calculate_default_probability(
        days_overdue=30,
        payment_consistency=0.8,
        loan_age_months=6
    )
    assert 0 <= prob <= 1
    
    # High overdue should increase risk
    high_risk_prob = CreditScoring.calculate_default_probability(90, 0.5, 3)
    assert high_risk_prob > prob
    
    # Test penalty calculations
    penalty = CreditScoring.calculate_penalty_interest(10000, 15, 12.0)
    assert penalty > 0
    
    late_fee = CreditScoring.calculate_late_fee(5000, 10, grace_period=3)
    assert late_fee == 100.0  # 2% of 5000
