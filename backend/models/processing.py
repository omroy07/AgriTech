from datetime import datetime
from backend.extensions import db
from enum import Enum

class ProcessingStage(Enum):
    COLLECTION = "collection"
    CLEANING = "cleaning"
    PROCESSING = "processing"
    GRADING = "grading"
    PACKAGING = "packaging"
    COMPLETED = "completed"

class ProcessingBatch(db.Model):
    __tablename__ = 'processing_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(50), unique=True, nullable=False)
    product_type = db.Column(db.String(100), nullable=False) # e.g., Wheat, Rice, Coffee
    
    total_weight = db.Column(db.Float, nullable=False) # in kg
    current_weight = db.Column(db.Float) # after processing losses
    
    current_stage = db.Column(db.String(20), default=ProcessingStage.COLLECTION.value)
    origin_farms = db.Column(db.Text) # JSON list of farm IDs or names
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    stages = db.relationship('StageLog', backref='batch', lazy='dynamic', cascade='all, delete-orphan')
    quality_checks = db.relationship('QualityCheck', backref='batch', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'batch_number': self.batch_number,
            'product_type': self.product_type,
            'total_weight': self.total_weight,
            'current_weight': self.current_weight,
            'current_stage': self.current_stage,
            'origin_farms': self.origin_farms,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class StageLog(db.Model):
    __tablename__ = 'processing_stage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('processing_batches.id'), nullable=False)
    
    stage_name = db.Column(db.String(20), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    notes = db.Column(db.Text)

class QualityCheck(db.Model):
    __tablename__ = 'quality_audits'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('processing_batches.id'), nullable=False)
    stage_name = db.Column(db.String(20), nullable=False)
    
    # Audit metrics
    moisture_content = db.Column(db.Float) # %
    purity_level = db.Column(db.Float) # %
    weight_recorded = db.Column(db.Float) # kg
    
    is_passed = db.Column(db.Boolean, default=False)
    auditor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'stage_name': self.stage_name,
            'moisture': self.moisture_content,
            'purity': self.purity_level,
            'weight': self.weight_recorded,
            'is_passed': self.is_passed,
            'timestamp': self.timestamp.isoformat()
        }
