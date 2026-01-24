"""Loan Request model"""
from datetime import datetime
from extensions import db
import json


class LoanRequest(db.Model):
    """Model for storing loan requests and eligibility assessments"""
    __tablename__ = 'loan_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Loan details
    loan_type = db.Column(db.String(100), nullable=False)
    amount_requested = db.Column(db.Float)
    purpose = db.Column(db.Text)
    
    # Applicant data
    applicant_data = db.Column(db.Text, nullable=False)  # JSON string of application data
    
    # Assessment results
    eligibility_status = db.Column(db.String(20))  # eligible, not_eligible, pending
    assessment_result = db.Column(db.Text)  # JSON string of full assessment
    recommended_amount = db.Column(db.Float)
    risk_score = db.Column(db.Float)  # 0-100
    
    # Status tracking
    status = db.Column(db.String(20), default='draft')  # draft, submitted, approved, rejected
    submitted_at = db.Column(db.DateTime)
    processed_at = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Report generation
    report_generated = db.Column(db.Boolean, default=False)
    report_path = db.Column(db.String(255))
    report_sent = db.Column(db.Boolean, default=False)
    
    def set_applicant_data(self, data):
        """Store applicant data as JSON"""
        self.applicant_data = json.dumps(data)
    
    def get_applicant_data(self):
        """Retrieve applicant data from JSON"""
        return json.loads(self.applicant_data) if self.applicant_data else None
    
    def set_assessment_result(self, result):
        """Store assessment result as JSON"""
        self.assessment_result = json.dumps(result)
    
    def get_assessment_result(self):
        """Retrieve assessment result from JSON"""
        return json.loads(self.assessment_result) if self.assessment_result else None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'loan_type': self.loan_type,
            'amount_requested': self.amount_requested,
            'purpose': self.purpose,
            'applicant_data': self.get_applicant_data(),
            'eligibility_status': self.eligibility_status,
            'assessment_result': self.get_assessment_result(),
            'recommended_amount': self.recommended_amount,
            'risk_score': self.risk_score,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'report_generated': self.report_generated,
            'report_sent': self.report_sent
        }
    
    def __repr__(self):
        return f'<LoanRequest {self.loan_type} - {self.id}>'
