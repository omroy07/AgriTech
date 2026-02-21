from datetime import datetime
# L3-1560: Predictive Harvest Velocity & Autonomous Futures Hedging
import json
import hashlib
from backend.extensions import db


class BatchStatus:
    HARVESTED = 'HARVESTED'
    QUALITY_CHECK = 'QUALITY_CHECK'
    PACKAGED = 'PACKAGED'
    LOGISTICS = 'LOGISTICS'
    IN_SHOP = 'IN_SHOP'
    SOLD = 'SOLD'
    REJECTED = 'REJECTED'

    @classmethod
    def is_valid(cls, status):
        return status in [cls.HARVESTED, cls.QUALITY_CHECK, cls.PACKAGED, cls.LOGISTICS, cls.IN_SHOP, cls.SOLD, cls.REJECTED]


class SupplyBatch(db.Model):
    __tablename__ = 'supply_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_internal_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    qr_code_data = db.Column(db.Text)
    
    # Crop Details
    crop_name = db.Column(db.String(100), nullable=False)
    crop_variety = db.Column(db.String(100))
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='KG')
    
    # State & Timeline
    status = db.Column(db.String(20), default=BatchStatus.HARVESTED)
    harvest_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    
    # Locations
    farm_location = db.Column(db.String(255), nullable=False)
    current_gps_lat = db.Column(db.Float)
    current_gps_lng = db.Column(db.Float)
    
    # Participants
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_handler_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    distributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    retailer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    soil_test_id = db.Column(db.Integer, db.ForeignKey('soil_tests.id'))
    insurance_policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'))
    
    # Quality & Legal
    is_certified = db.Column(db.Boolean, default=False)
    certificate_url = db.Column(db.String(255))
    integrity_hash = db.Column(db.String(64))  # SHA256 of the batch history
    
    # Global Trade & ESG (L3-1546)
    export_compliance_status = db.Column(db.String(20), default='PENDING') # PENDING, CLEARED, REJECTED
    target_market = db.Column(db.String(50)) # EU, USA, ASIA
    esg_score = db.Column(db.Float) # Calculated sustainability score
    phyto_cert_id = db.Column(db.String(100))
    
    # Carbon Accounting (L3-1558)
    carbon_footprint_hash = db.Column(db.String(64)) # Linked to CarbonLedger
    net_zero_qualified = db.Column(db.Boolean, default=False)
    
    # Predictive Velocity (L3-1560)
    predicted_quality_grade = db.Column(db.String(10)) # A, B, C based on pre-harvest flux
    # Bio-Security (L3-1596)
    # Status: CLEAN, SUSPECTED, QUARANTINED, REJECTED
    quarantine_status = db.Column(db.String(20), default='CLEAN')
    bio_clearance_hash = db.Column(db.String(64)) # Required for logistics manifest
    contact_tracing_metadata = db.Column(db.Text) # JSON of previous exposures
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    custody_logs = db.relationship('CustodyLog', backref='batch', lazy='dynamic', cascade='all, delete-orphan')
    quality_grades = db.relationship('QualityGrade', backref='batch', lazy='dynamic', cascade='all, delete-orphan')

    def generate_integrity_hash(self):
        """Generate a SHA256 hash representing the current state and audit trail of the batch"""
        logs = [log.to_dict() for log in self.custody_logs.all()]
        data = {
            'id': self.batch_internal_id,
            'crop': self.crop_name,
            'quantity': self.quantity,
            'logs': logs
        }
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()

    def to_dict(self, include_logs=False):
        data = {
            'id': self.id,
            'batch_id': self.batch_internal_id,
            'crop_name': self.crop_name,
            'crop_variety': self.crop_variety,
            'quantity': self.quantity,
            'unit': self.unit,
            'status': self.status,
            'farm_location': self.farm_location,
            'farmer_id': self.farmer_id,
            'current_handler_id': self.current_handler_id,
            'harvest_date': self.harvest_date.isoformat(),
            'is_certified': self.is_certified,
            'certificate_url': self.certificate_url,
            'integrity_hash': self.integrity_hash,
            'updated_at': self.updated_at.isoformat()
        }
        if include_logs:
            data['logs'] = [log.to_dict() for log in self.custody_logs.order_by(CustodyLog.timestamp.desc()).all()]
            data['quality_history'] = [q.to_dict() for q in self.quality_grades.all()]
        return data


class QualityGrade(db.Model):
    __tablename__ = 'quality_grades'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    grade = db.Column(db.String(10), nullable=False)  # A, B, C, Premium, etc.
    parameters = db.Column(db.Text)  # JSON string of moisture, size, etc.
    notes = db.Column(db.Text)
    
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'grade': self.grade,
            'parameters': json.loads(self.parameters) if self.parameters else {},
            'notes': self.notes,
            'inspection_date': self.inspection_date.isoformat()
        }


class CustodyLog(db.Model):
    __tablename__ = 'custody_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id'), nullable=False)
    handler_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    action = db.Column(db.String(100), nullable=False)  # HARVESTED, TRANSFERRED, RECEIVED, etc.
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20))
    
    location = db.Column(db.String(255))
    gps_lat = db.Column(db.Float)
    gps_lng = db.Column(db.Float)
    
    notes = db.Column(db.Text)
    digital_signature = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'handler_id': self.handler_id,
            'action': self.action,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'location': self.location,
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes
        }
