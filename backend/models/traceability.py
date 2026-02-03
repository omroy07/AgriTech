from datetime import datetime
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


class ProduceBatch(db.Model):
    __tablename__ = 'produce_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(50), unique=True, nullable=False)
    qr_code = db.Column(db.Text)
    produce_name = db.Column(db.String(100), nullable=False)
    produce_type = db.Column(db.String(50), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    origin_location = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default=BatchStatus.HARVESTED)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_handler_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shopkeeper_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    harvest_date = db.Column(db.DateTime, default=datetime.utcnow)
    quality_check_date = db.Column(db.DateTime, nullable=True)
    logistics_date = db.Column(db.DateTime, nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)
    certification = db.Column(db.String(100))
    quality_grade = db.Column(db.String(20))
    quality_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit_logs = db.relationship('AuditTrail', backref='batch', lazy='dynamic', cascade='all, delete-orphan')

    def can_transition_to(self, new_status, user_role):
        # Simplified transition logic
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'produce_name': self.produce_name,
            'produce_type': self.produce_type,
            'quantity_kg': self.quantity_kg,
            'origin_location': self.origin_location,
            'status': self.status,
            'farmer_id': self.farmer_id,
            'current_handler_id': self.current_handler_id,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditTrail(db.Model):
    __tablename__ = 'audit_trails'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('produce_batches.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_role = db.Column(db.String(20))
    user_email = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    location = db.Column(db.String(200))
    notes = db.Column(db.Text)
    event_metadata = db.Column(db.Text)
    signature = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'notes': self.notes
        }
