from datetime import datetime, date
from backend.extensions import db

class RepaymentSchedule(db.Model):
    __tablename__ = 'repayment_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_request_id = db.Column(db.Integer, db.ForeignKey('loan_requests.id'), nullable=False)
    
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    
    principal_amount = db.Column(db.Float, nullable=False)
    interest_amount = db.Column(db.Float, nullable=False)
    total_emi = db.Column(db.Float, nullable=False)
    
    outstanding_balance = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'installment': self.installment_number,
            'due_date': self.due_date.isoformat(),
            'principal': self.principal_amount,
            'interest': self.interest_amount,
            'emi': self.total_emi,
            'balance': self.outstanding_balance,
            'paid': self.is_paid
        }

class PaymentHistory(db.Model):
    __tablename__ = 'payment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_request_id = db.Column(db.Integer, db.ForeignKey('loan_requests.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('repayment_schedules.id'))
    
    amount_paid = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    
    payment_method = db.Column(db.String(50)) # e.g., UPI, Bank Transfer
    transaction_ref = db.Column(db.String(100), unique=True)
    
    late_fee = db.Column(db.Float, default=0.0)
    penalty_interest = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount_paid,
            'date': self.payment_date.isoformat(),
            'method': self.payment_method,
            'late_fee': self.late_fee,
            'penalty': self.penalty_interest,
            'ref': self.transaction_ref
        }

class DefaultRiskScore(db.Model):
    __tablename__ = 'default_risk_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_request_id = db.Column(db.Integer, db.ForeignKey('loan_requests.id'), nullable=False)
    
    risk_score = db.Column(db.Float, nullable=False) # 0-100 scale
    probability_default = db.Column(db.Float) # 0-1 probability
    
    days_overdue = db.Column(db.Integer, default=0)
    payment_consistency = db.Column(db.Float) # 0-1 where 1 is perfect
    
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'risk_score': self.risk_score,
            'default_prob': self.probability_default,
            'days_overdue': self.days_overdue,
            'consistency': self.payment_consistency,
            'calculated_at': self.calculated_at.isoformat()
        }

class CollectionNote(db.Model):
    __tablename__ = 'collection_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_request_id = db.Column(db.Integer, db.ForeignKey('loan_requests.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    note_type = db.Column(db.String(50)) # REMINDER, WARNING, LEGAL_NOTICE
    content = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
