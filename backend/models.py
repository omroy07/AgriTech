from datetime import datetime
from backend.extensions import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True) # Changed to nullable for now if needed
    phone = db.Column(db.String(20), unique=True, nullable=True)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Multilingual preference
    language_preference = db.Column(db.String(10), default='en')
    
    # Email verification fields
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Notification preferences
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    
    notifications = db.relationship('Notification', backref='user', lazy=True)
    files = db.relationship('File', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'sent_at': self.sent_at.isoformat()
        }

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=False)
    storage_type = db.Column(db.String(20), default='local')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'storage_type': self.storage_type,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<File {self.id} - {self.original_name}>'


class RiskScoreHistory(db.Model):
    """
    Tracks the historical Agri-Risk Score (ARS) for a farmer over time.
    """
    __tablename__ = 'risk_score_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Risk Score (0-100, lower is better)
    ars_score = db.Column(db.Float, nullable=False)
    
    # Contributing factors
    weather_risk_factor = db.Column(db.Float, default=0.0)  # 0-1
    crop_success_rate = db.Column(db.Float, default=0.0)  # 0-1
    location_risk_factor = db.Column(db.Float, default=0.0)  # 0-1
    activity_score = db.Column(db.Float, default=0.0)  # Platform activity
    
    # Metadata
    calculation_version = db.Column(db.String(10), default='1.0')
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='risk_scores')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ars_score': self.ars_score,
            'weather_risk_factor': self.weather_risk_factor,
            'crop_success_rate': self.crop_success_rate,
            'location_risk_factor': self.location_risk_factor,
            'activity_score': self.activity_score,
            'calculation_version': self.calculation_version,
            'calculated_at': self.calculated_at.isoformat(),
            'risk_category': self.get_risk_category()
        }
    
    def get_risk_category(self):
        """Categorize risk score."""
        if self.ars_score <= 20:
            return 'EXCELLENT'
        elif self.ars_score <= 40:
            return 'GOOD'
        elif self.ars_score <= 60:
            return 'MODERATE'
        elif self.ars_score <= 80:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def __repr__(self):
        return f'<RiskScore User:{self.user_id} ARS:{self.ars_score}>'


class InsurancePolicy(db.Model):
    """
    Represents an agricultural insurance policy for a farmer.
    """
    __tablename__ = 'insurance_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Policy details
    crop_type = db.Column(db.String(100), nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)
    
    # Risk-based pricing
    ars_score_at_issuance = db.Column(db.Float, nullable=False)
    base_premium_rate = db.Column(db.Float, nullable=False)  # Base rate percentage
    risk_multiplier = db.Column(db.Float, nullable=False)  # Applied multiplier
    
    # Coverage period
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Status: ACTIVE, EXPIRED, CANCELLED, CLAIMED
    status = db.Column(db.String(20), default='ACTIVE', nullable=False)
    
    # Farm details
    farm_location = db.Column(db.String(200), nullable=False)
    farm_size_acres = db.Column(db.Float, nullable=False)
    
    # Timestamps
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    renewed_from_policy_id = db.Column(db.Integer, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='insurance_policies')
    claims = db.relationship('ClaimRequest', backref='policy', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'policy_number': self.policy_number,
            'user_id': self.user_id,
            'crop_type': self.crop_type,
            'coverage_amount': self.coverage_amount,
            'premium_amount': self.premium_amount,
            'ars_score_at_issuance': self.ars_score_at_issuance,
            'base_premium_rate': self.base_premium_rate,
            'risk_multiplier': self.risk_multiplier,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status,
            'farm_location': self.farm_location,
            'farm_size_acres': self.farm_size_acres,
            'issued_at': self.issued_at.isoformat(),
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'days_remaining': (self.end_date - datetime.utcnow().date()).days if self.status == 'ACTIVE' else 0
        }
    
    def __repr__(self):
        return f'<InsurancePolicy {self.policy_number} - {self.status}>'


class ClaimRequest(db.Model):
    """
    Represents a crop failure insurance claim request.
    """
    __tablename__ = 'claim_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_number = db.Column(db.String(50), unique=True, nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Claim details
    claim_type = db.Column(db.String(50), nullable=False)  # CROP_FAILURE, WEATHER_DAMAGE, PEST_DAMAGE
    claimed_amount = db.Column(db.Float, nullable=False)
    approved_amount = db.Column(db.Float, nullable=True)
    
    # Evidence
    description = db.Column(db.Text, nullable=False)
    evidence_photo_ids = db.Column(db.Text, nullable=True)  # Comma-separated file IDs
    
    # AI Verification
    ai_verification_status = db.Column(db.String(20), default='PENDING')  # PENDING, VERIFIED, REJECTED, MANUAL_REVIEW
    ai_confidence_score = db.Column(db.Float, nullable=True)  # 0-1
    ai_verification_notes = db.Column(db.Text, nullable=True)
    
    # Status: SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, PAID
    status = db.Column(db.String(20), default='SUBMITTED', nullable=False)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Reviewer notes
    reviewer_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='insurance_claims')
    
    def to_dict(self):
        return {
            'id': self.id,
            'claim_number': self.claim_number,
            'policy_id': self.policy_id,
            'user_id': self.user_id,
            'claim_type': self.claim_type,
            'claimed_amount': self.claimed_amount,
            'approved_amount': self.approved_amount,
            'description': self.description,
            'evidence_photo_ids': self.evidence_photo_ids.split(',') if self.evidence_photo_ids else [],
            'ai_verification_status': self.ai_verification_status,
            'ai_confidence_score': self.ai_confidence_score,
            'ai_verification_notes': self.ai_verification_notes,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'reviewer_notes': self.reviewer_notes,
            'rejection_reason': self.rejection_reason
        }
    
    def __repr__(self):
        return f'<ClaimRequest {self.claim_number} - {self.status}>'
