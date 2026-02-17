from datetime import datetime
from backend.extensions import db
from enum import Enum

class AuditStatus(Enum):
    SUBMITTED = "submitted"
    PENDING_PROOF = "pending_proof"
    AUDITING = "auditing"
    CERTIFIED = "certified"
    REJECTED = "rejected"

class CarbonPractice(db.Model):
    __tablename__ = 'carbon_practices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    
    practice_type = db.Column(db.String(50), nullable=False) # e.g., 'No-Till', 'Cover Cropping'
    area_covered = db.Column(db.Float, nullable=False) # in acres
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    
    # Evidence for auditing
    evidence_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Calculated values
    estimated_offset = db.Column(db.Float, default=0.0) # Tonnes of CO2

    def to_dict(self):
        return {
            'id': self.id,
            'practice_type': self.practice_type,
            'area_covered': self.area_covered,
            'is_verified': self.is_verified,
            'estimated_offset': self.estimated_offset,
            'created_at': self.created_at.isoformat()
        }

class AuditRequest(db.Model):
    __tablename__ = 'audit_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    practice_id = db.Column(db.Integer, db.ForeignKey('carbon_practices.id'), nullable=False)
    auditor_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Assigned auditor
    
    status = db.Column(db.String(20), default=AuditStatus.SUBMITTED.value)
    auditor_comments = db.Column(db.Text)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

class CreditLedger(db.Model):
    __tablename__ = 'carbon_credit_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    practice_id = db.Column(db.Integer, db.ForeignKey('carbon_practices.id')) # Source of credit
    
    amount = db.Column(db.Float, nullable=False) # Number of credits (1 credit = 1 tonne CO2)
    status = db.Column(db.String(20), default='Active') # 'Active', 'Sold', 'Retired'
    serial_number = db.Column(db.String(100), unique=True)
    
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_id = db.Column(db.String(100)) # Cross-ref with marketplace transactions

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'status': self.status,
            'serial_number': self.serial_number,
            'issued_at': self.issued_at.isoformat()
        }
