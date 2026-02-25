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
    
    # Parametric Auto-Settlement (L3-1630)
    parametric_enabled = db.Column(db.Boolean, default=False) # Opts into climate-trigger payouts
    yield_at_risk_pct = db.Column(db.Float, default=0.0)      # Engine-computed exposure %
    last_climate_check = db.Column(db.DateTime)
    
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

class ParametricAutoSettlement(db.Model):
    """
    Immutable record of every autonomous parametric insurance payout (L3-1630).
    Created when ForceMajeureAlert triggers an eligible CropPolicy.
    Bypasses manual claim adjudication entirely.
    """
    __tablename__ = 'parametric_auto_settlements'

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('crop_policies.id'), nullable=False)
    alert_id = db.Column(db.Integer, db.ForeignKey('force_majeure_alerts.id'), nullable=False)

    # Settlement financials
    coverage_amount = db.Column(db.Float, nullable=False)
    payout_percentage = db.Column(db.Float, nullable=False)
    payout_amount = db.Column(db.Float, nullable=False)

    # Evidence snapshot (immutable for audit)
    trigger_type = db.Column(db.String(50))
    consecutive_days_observed = db.Column(db.Integer)
    peak_temperature_c = db.Column(db.Float)
    evidence_hash = db.Column(db.String(64), unique=True, nullable=False)

    # Double-entry ledger reference
    ledger_transaction_id = db.Column(db.Integer, db.ForeignKey('ledger_transactions.id'))
    
    settled_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'alert_id': self.alert_id,
            'payout_amount': self.payout_amount,
            'payout_percentage': self.payout_percentage,
            'trigger_type': self.trigger_type,
            'consecutive_days': self.consecutive_days_observed,
            'evidence_hash': self.evidence_hash,
            'settled_at': self.settled_at.isoformat()
        }
