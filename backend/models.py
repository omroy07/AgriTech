from datetime import datetime
from backend.extensions import db

class UserRole:
    FARMER = 'farmer'
    SHOPKEEPER = 'shopkeeper'
    ADMIN = 'admin'
    CONSULTANT = 'consultant'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default=UserRole.FARMER)
    
    notifications = db.relationship('Notification', backref='user', lazy=True)
    files = db.relationship('File', backref='user', lazy=True)

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


class BatchStatus:
    """Enum-like class for batch lifecycle stages"""
    HARVESTED = 'Harvested'
    QUALITY_CHECK = 'Quality_Check'
    LOGISTICS = 'Logistics'
    IN_SHOP = 'In_Shop'
    
    @classmethod
    def all_statuses(cls):
        return [cls.HARVESTED, cls.QUALITY_CHECK, cls.LOGISTICS, cls.IN_SHOP]
    
    @classmethod
    def is_valid(cls, status):
        return status in cls.all_statuses()


class ProduceBatch(db.Model):
    """
    Model representing a batch of produce in the supply chain.
    Implements state-machine based lifecycle tracking from farm to shop.
    """
    __tablename__ = 'produce_batches'
    
    # Primary identifiers
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    qr_code = db.Column(db.Text, nullable=False)  # Encrypted QR code data
    
    # Produce details
    produce_name = db.Column(db.String(200), nullable=False)
    produce_type = db.Column(db.String(100), nullable=False)  # e.g., vegetable, fruit, grain
    quantity_kg = db.Column(db.Float, nullable=False)
    origin_location = db.Column(db.String(255), nullable=False)
    
    # Lifecycle state
    status = db.Column(db.String(50), nullable=False, default=BatchStatus.HARVESTED, index=True)
    
    # Ownership tracking
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_handler_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    shopkeeper_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Quality metrics
    quality_grade = db.Column(db.String(10), nullable=True)  # A, B, C
    quality_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    harvest_date = db.Column(db.DateTime, nullable=False)
    quality_check_date = db.Column(db.DateTime, nullable=True)
    logistics_date = db.Column(db.DateTime, nullable=True)
    received_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    temperature_log = db.Column(db.Text, nullable=True)  # JSON string of temperature readings
    certification = db.Column(db.String(100), nullable=True)  # organic, non-GMO, etc.
    
    # Relationships
    farmer = db.relationship('User', foreign_keys=[farmer_id], backref='batches_created')
    current_handler = db.relationship('User', foreign_keys=[current_handler_id])
    shopkeeper = db.relationship('User', foreign_keys=[shopkeeper_id], backref='batches_received')
    audit_logs = db.relationship('AuditTrail', backref='batch', lazy='dynamic', cascade='all, delete-orphan')
    
    def can_transition_to(self, new_status, user_role):
        """
        Check if batch can transition to new status based on current state and user role.
        Implements state-machine logic.
        """
        # Define valid transitions
        transitions = {
            BatchStatus.HARVESTED: {
                BatchStatus.QUALITY_CHECK: [UserRole.FARMER, UserRole.ADMIN]
            },
            BatchStatus.QUALITY_CHECK: {
                BatchStatus.LOGISTICS: [UserRole.FARMER, UserRole.ADMIN],
                BatchStatus.HARVESTED: [UserRole.ADMIN]  # Allow rollback
            },
            BatchStatus.LOGISTICS: {
                BatchStatus.IN_SHOP: [UserRole.SHOPKEEPER, UserRole.ADMIN],
                BatchStatus.QUALITY_CHECK: [UserRole.ADMIN]  # Allow rollback
            },
            BatchStatus.IN_SHOP: {
                # Terminal state - only admin can modify
                BatchStatus.LOGISTICS: [UserRole.ADMIN]
            }
        }
        
        if self.status not in transitions:
            return False
        
        if new_status not in transitions[self.status]:
            return False
        
        allowed_roles = transitions[self.status][new_status]
        return user_role in allowed_roles
    
    def to_dict(self, include_audit=False):
        """Convert batch to dictionary for API responses"""
        result = {
            'id': self.id,
            'batch_id': self.batch_id,
            'produce_name': self.produce_name,
            'produce_type': self.produce_type,
            'quantity_kg': self.quantity_kg,
            'origin_location': self.origin_location,
            'status': self.status,
            'farmer_id': self.farmer_id,
            'current_handler_id': self.current_handler_id,
            'shopkeeper_id': self.shopkeeper_id,
            'quality_grade': self.quality_grade,
            'quality_notes': self.quality_notes,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'quality_check_date': self.quality_check_date.isoformat() if self.quality_check_date else None,
            'logistics_date': self.logistics_date.isoformat() if self.logistics_date else None,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'certification': self.certification
        }
        
        if include_audit:
            result['audit_trail'] = [log.to_dict() for log in self.audit_logs.order_by(AuditTrail.timestamp.asc()).all()]
        
        return result
    
    def to_public_dict(self):
        """Public-facing dictionary for QR code verification (limited info)"""
        return {
            'batch_id': self.batch_id,
            'produce_name': self.produce_name,
            'produce_type': self.produce_type,
            'quantity_kg': self.quantity_kg,
            'origin_location': self.origin_location,
            'status': self.status,
            'quality_grade': self.quality_grade,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'certification': self.certification,
            'last_updated': self.updated_at.isoformat()
        }


class AuditTrail(db.Model):
    """
    Immutable audit log for supply chain hand-offs.
    Records every state transition with full context.
    """
    __tablename__ = 'audit_trails'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('produce_batches.id'), nullable=False, index=True)
    
    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # STATUS_CHANGE, QUALITY_UPDATE, etc.
    from_status = db.Column(db.String(50), nullable=True)
    to_status = db.Column(db.String(50), nullable=True)
    
    # Actor information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_role = db.Column(db.String(20), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    
    # Context
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    metadata = db.Column(db.Text, nullable=True)  # JSON string for additional data
    
    # Integrity
    signature = db.Column(db.String(255), nullable=True)  # HMAC signature for tamper detection
    
    # Relationships
    user = db.relationship('User', backref='audit_actions')
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'event_type': self.event_type,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'user_id': self.user_id,
            'user_role': self.user_role,
            'user_email': self.user_email,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'location': self.location,
            'notes': self.notes
        }
