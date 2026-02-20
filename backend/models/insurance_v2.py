from datetime import datetime
from backend.extensions import db
from enum import Enum

class PolicyStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ClaimStatus(Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class CropPolicy(db.Model):
    __tablename__ = 'crop_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    crop_type = db.Column(db.String(50), nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    premium_paid = db.Column(db.Float, nullable=False)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    risk_score = db.Column(db.Float) # Calculated during underwriting
    status = db.Column(db.String(20), default=PolicyStatus.PENDING.value)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    claims = db.relationship('ClaimRequest', backref='policy', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'crop_type': self.crop_type,
            'coverage': self.coverage_amount,
            'premium': self.premium_paid,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status,
            'risk_score': self.risk_score
        }

class ClaimRequest(db.Model):
    __tablename__ = 'insurance_claims'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('crop_policies.id'), nullable=False)
    
    claim_amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text) # e.g., "Drought", "Excess Rainfall"
    
    evidence_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default=ClaimStatus.SUBMITTED.value)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    notes = db.relationship('AdjusterNote', backref='claim', lazy='dynamic')

class AdjusterNote(db.Model):
    __tablename__ = 'adjuster_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('insurance_claims.id'), nullable=False)
    adjuster_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    verification_score = db.Column(db.Float) # 0-1 based on satellite/weather data verification
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PayoutLedger(db.Model):
    __tablename__ = 'insurance_payouts'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('insurance_claims.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    transaction_ref = db.Column(db.String(100), unique=True)
    
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
