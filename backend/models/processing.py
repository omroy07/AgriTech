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

batch_supply_map = db.Table('batch_supply_map',
    db.Column('processing_batch_id', db.Integer, db.ForeignKey('processing_batches.id'), primary_key=True),
    db.Column('supply_batch_id', db.Integer, db.ForeignKey('supply_batches.id'), primary_key=True)
)

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
    supply_batches = db.relationship('SupplyBatch', secondary=batch_supply_map, backref='processing_batches')

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

class SpectralScanData(db.Model):
    """
    Simulated 'optical/spectral scans' for raw chemical analysis (L3-1604).
    """
    __tablename__ = 'spectral_scans'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('processing_batches.id'), nullable=False)
    
    # Nutritional parameters (Simulated)
    moisture_percentage = db.Column(db.Float)
    brix_level = db.Column(db.Float) # Sugar content
    protein_percentage = db.Column(db.Float)
    fiber_percentage = db.Column(db.Float)
    
    # Spectral metadata
    wavelength_range = db.Column(db.String(50)) # e.g., "700nm-2500nm"
    scan_integrity_score = db.Column(db.Float) # 0.0 - 1.0
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class DynamicGradeAdjustment(db.Model):
    """
    Tracks cascading financial recalculations after grading (L3-1604).
    """
    __tablename__ = 'dynamic_grade_adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('processing_batches.id'), nullable=False)
    
    old_grade = db.Column(db.String(10))
    new_grade = db.Column(db.String(10))
    
    price_penalty_factor = db.Column(db.Float) # e.g., -0.15 for 15% drop
    adjustment_reason = db.Column(db.String(255))
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
