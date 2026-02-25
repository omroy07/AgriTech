"""
AI Crop Diagnostic Models — L3-1643
==================================
Models for computer vision based disease detection and severity scoring.
"""

from datetime import datetime
from backend.extensions import db

class CropDiagnosticReport(db.Model):
    __tablename__ = 'crop_diagnostic_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    image_url = db.Column(db.String(512), nullable=False)
    
    # AI Detection Results
    identified_pathogen = db.Column(db.String(100)) # e.g., "Blast disease", "Leaf folder"
    confidence_score = db.Column(db.Float)
    severity_index = db.Column(db.Float) # 0.0 to 1.0
    
    # Recommended Action
    recommended_treatment = db.Column(db.Text)
    estimated_yield_loss_pct = db.Column(db.Float)
    
    status = db.Column(db.String(20), default='PENDING') # PENDING, VERIFIED, RESOLVED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DiagnosticVerification(db.Model):
    """
    Expert verification of AI diagnostics.
    """
    __tablename__ = 'diagnostic_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('crop_diagnostic_reports.id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    ai_was_correct = db.Column(db.Boolean)
    expert_notes = db.Column(db.Text)
    
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)

class PathogenKnowledgeBase(db.Model):
    __tablename__ = 'pathogen_knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    pathogen_name = db.Column(db.String(100), unique=True, nullable=False)
    
    typical_symptoms = db.Column(db.Text)
    suggested_chemical_treatment = db.Column(db.Text)
    organic_alternative = db.Column(db.Text)
    
    mortality_rate_potential = db.Column(db.Float)

