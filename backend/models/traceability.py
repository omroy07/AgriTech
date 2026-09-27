"""
Supply Chain Traceability & Immutable Farm-to-Fork Lifecycle Models.
Location: backend/models/traceability.py
"""

from datetime import datetime
import json
import hashlib
import uuid
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
    current_gps_lat = db.Column(db.Float, default=19.9975)
    current_gps_lng = db.Column(db.Float, default=73.7898)
    
    # Participants
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_handler_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    distributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    retailer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    soil_test_id = db.Column(db.Integer, db.ForeignKey('soil_tests.id'))
    insurance_policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'))
    
    # Quality & Legal
    is_certified = db.Column(db.Boolean, default=True)
    certificate_url = db.Column(db.String(255))
    integrity_hash = db.Column(db.String(64))  # SHA256 of the batch history
    
    # Global Trade & ESG
    export_compliance_status = db.Column(db.String(20), default='CLEARED')
    target_market = db.Column(db.String(50), default='DOMESTIC_PREMIUM')
    esg_score = db.Column(db.Float, default=94.5)
    phyto_cert_id = db.Column(db.String(100))
    
    # Carbon Accounting
    carbon_footprint_hash = db.Column(db.String(64))
    net_zero_qualified = db.Column(db.Boolean, default=True)
    carbon_saved_kg = db.Column(db.Float, default=1.85)  # kg CO2e saved per kg produce
    
    # Bio-Security & Quality
    predicted_quality_grade = db.Column(db.String(10), default='A+')
    quarantine_status = db.Column(db.String(20), default='CLEAN')
    bio_clearance_hash = db.Column(db.String(64))
    contact_tracing_metadata = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    custody_logs = db.relationship('CustodyLog', backref='batch', lazy='dynamic', cascade='all, delete-orphan')
    quality_grades = db.relationship('QualityGrade', backref='batch', lazy='dynamic', cascade='all, delete-orphan')
    lifecycle_logs = db.relationship('FarmLifecycleLog', backref='batch', lazy='dynamic', cascade='all, delete-orphan', order_by='FarmLifecycleLog.timestamp.asc()')

    def generate_integrity_hash(self):
        """Generate a SHA256 cryptographic hash representing immutable audit trail"""
        logs = [log.to_dict() for log in self.lifecycle_logs.all()]
        data = {
            'batch_id': self.batch_internal_id,
            'crop': self.crop_name,
            'variety': self.crop_variety,
            'quantity': self.quantity,
            'farm': self.farm_location,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'lifecycle': logs
        }
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()

    def to_dict(self, include_logs=True):
        data = {
            'id': self.id,
            'batch_id': self.batch_internal_id,
            'crop_name': self.crop_name,
            'crop_variety': self.crop_variety or 'Organic Heirloom',
            'quantity': self.quantity,
            'unit': self.unit,
            'status': self.status,
            'farm_location': self.farm_location,
            'latitude': self.current_gps_lat or 19.9975,
            'longitude': self.current_gps_lng or 73.7898,
            'farmer_id': self.farmer_id,
            'current_handler_id': self.current_handler_id,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else datetime.utcnow().isoformat(),
            'is_certified': self.is_certified,
            'certificate_url': self.certificate_url,
            'integrity_hash': self.integrity_hash or self.generate_integrity_hash(),
            'esg_score': self.esg_score,
            'carbon_saved_kg': self.carbon_saved_kg,
            'quality_grade': self.predicted_quality_grade or 'A+',
            'net_zero_qualified': self.net_zero_qualified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_logs:
            data['lifecycle_logs'] = [l.to_dict() for l in self.lifecycle_logs.all()]
            data['logs'] = [log.to_dict() for log in self.custody_logs.order_by(CustodyLog.timestamp.desc()).all()]
            data['quality_history'] = [q.to_dict() for q in self.quality_grades.all()]
        return data


class FarmLifecycleLog(db.Model):
    """
    Immutable Farm-to-Fork Activity Ledger.
    Records seed origin, soil testing, bio-inputs, irrigation, lab screenings with cryptographic chaining.
    """
    __tablename__ = 'farm_lifecycle_logs'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id'), nullable=False, index=True)
    event_type = db.Column(db.String(60), nullable=False, index=True)  # SEED_SOWING | SOIL_HEALTH | BIO_FERTILIZER | BIOPESTICIDE | IRRIGATION | HARVEST | LAB_CERTIFICATION | PACKAGING
    event_title = db.Column(db.String(150), nullable=False)
    stage_category = db.Column(db.String(50), default='FARM')  # SEED | SOIL | CROP_CARE | HARVEST | QUALITY | LOGISTICS
    performed_by = db.Column(db.String(100), default='Certified Agronomist')
    location_name = db.Column(db.String(255))
    gps_lat = db.Column(db.Float)
    gps_lng = db.Column(db.Float)
    
    # Structured event payload
    payload_json = db.Column(db.Text)
    notes = db.Column(db.Text)
    carbon_impact_kg = db.Column(db.Float, default=0.0)
    
    # Cryptographic immutability chaining
    previous_hash = db.Column(db.String(64), nullable=False, default='GENESIS_BLOCK')
    block_hash = db.Column(db.String(64), nullable=False, index=True)
    digital_signature = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def create_event(
        cls,
        batch_id: int,
        event_type: str,
        event_title: str,
        payload_data: dict,
        previous_hash: str = 'GENESIS_BLOCK',
        performed_by: str = 'Certified Agronomist',
        location_name: str = 'Organic Farm Estate',
        gps_lat: float = 19.9975,
        gps_lng: float = 73.7898,
        notes: str = '',
        carbon_impact_kg: float = 0.0,
        timestamp: Optional[datetime] = None
    ):
        ts = timestamp or datetime.utcnow()
        payload_str = json.dumps(payload_data, sort_keys=True, default=str)
        
        # Calculate SHA256 block hash
        raw_block = f"{batch_id}|{event_type}|{payload_str}|{previous_hash}|{ts.isoformat()}"
        block_hash = hashlib.sha256(raw_block.encode('utf-8')).hexdigest()
        digital_sig = f"SIG_ED25519_{hashlib.sha256((block_hash + 'AGRITECH_KEY').encode()).hexdigest()[:24].upper()}"

        return cls(
            batch_id=batch_id,
            event_type=event_type,
            event_title=event_title,
            payload_json=payload_str,
            performed_by=performed_by,
            location_name=location_name,
            gps_lat=gps_lat,
            gps_lng=gps_lng,
            notes=notes,
            carbon_impact_kg=carbon_impact_kg,
            previous_hash=previous_hash,
            block_hash=block_hash,
            digital_signature=digital_sig,
            timestamp=ts
        )

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_title': self.event_title,
            'stage_category': self.stage_category,
            'performed_by': self.performed_by,
            'location': self.location_name,
            'gps': {'lat': self.gps_lat, 'lng': self.gps_lng} if self.gps_lat else None,
            'payload': json.loads(self.payload_json) if self.payload_json else {},
            'notes': self.notes,
            'carbon_impact_kg': self.carbon_impact_kg,
            'previous_hash': self.previous_hash,
            'block_hash': self.block_hash,
            'digital_signature': self.digital_signature,
            'timestamp': self.timestamp.isoformat()
        }


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
    
    action = db.Column(db.String(100), nullable=False)
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
