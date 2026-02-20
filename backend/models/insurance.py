from datetime import datetime
from backend.extensions import db


class InsurancePolicy(db.Model):
    __tablename__ = 'insurance_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    policy_number = db.Column(db.String(50), unique=True, nullable=False)
    coverage_amount = db.Column(db.Numeric(15, 2), nullable=False)
    premium_amount = db.Column(db.Numeric(15, 2), nullable=False)
    ars_score_at_issuance = db.Column(db.Float)
    risk_multiplier = db.Column(db.Float)
    crop_type = db.Column(db.String(100))
    farm_location = db.Column(db.String(200))
    farm_size_acres = db.Column(db.Float)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ACTIVE')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Live Risk Orchestration (L3-1557)
    current_risk_score = db.Column(db.Float, default=0.0)
    is_suspended = db.Column(db.Boolean, default=False)
    suspension_reason = db.Column(db.String(255))
    recursive_discount_applied = db.Column(db.Boolean, default=False)

    premium_logs = db.relationship('DynamicPremiumLog', backref='policy', lazy='dynamic')
    risk_snapshots = db.relationship('RiskFactorSnapshot', backref='policy', lazy='dynamic')

class DynamicPremiumLog(db.Model):
    __tablename__ = 'dynamic_premium_logs'

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'), nullable=False)

    old_premium = db.Column(db.Numeric(15, 2))
    new_premium = db.Column(db.Numeric(15, 2))
    change_reason = db.Column(db.String(255))

    triggered_by = db.Column(db.String(50)) # WEATHER, TELEMETRY, AUDIT
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class RiskFactorSnapshot(db.Model):
    __tablename__ = 'risk_factor_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'), nullable=False)

    weather_risk_index = db.Column(db.Float)
    telemetry_risk_index = db.Column(db.Float)
    sustainability_discount_factor = db.Column(db.Float)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'policy_number': self.policy_number,
            'coverage_amount': float(self.coverage_amount),
            'premium_amount': float(self.premium_amount),
            'crop_type': self.crop_type,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }


class ClaimRequest(db.Model):
    __tablename__ = 'claim_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    claim_number = db.Column(db.String(50), unique=True, nullable=False)
    claimed_amount = db.Column(db.Numeric(15, 2), nullable=False)
    approved_amount = db.Column(db.Numeric(15, 2))
    incident_date = db.Column(db.DateTime, nullable=False)
    incident_description = db.Column(db.Text)
    evidence_photos = db.Column(db.JSON)
    status = db.Column(db.String(20), default='SUBMITTED')
    ai_verification_status = db.Column(db.String(20), default='PENDING')
    rejection_reason = db.Column(db.Text)
    processed_at = db.Column(db.DateTime)
    payment_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'claim_number': self.claim_number,
            'policy_id': self.policy_id,
            'claimed_amount': float(self.claimed_amount),
            'approved_amount': float(self.approved_amount) if self.approved_amount else None,
            'status': self.status,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RiskScoreHistory(db.Model):
    __tablename__ = 'risk_score_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ars_score = db.Column(db.Float, nullable=False)
    risk_category = db.Column(db.String(20))
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
