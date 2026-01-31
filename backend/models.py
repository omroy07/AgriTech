from datetime import datetime
from backend.extensions import db
from geoalchemy2 import Geometry
from sqlalchemy import Index

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
    
    # Geospatial farm location
    farm_latitude = db.Column(db.Float, nullable=True)
    farm_longitude = db.Column(db.Float, nullable=True)
    farm_location = db.Column(Geometry('POINT', srid=4326), nullable=True)  # PostGIS Point
    farm_address = db.Column(db.String(500), nullable=True)
    
    notifications = db.relationship('Notification', backref='user', lazy=True)
    files = db.relationship('File', backref='user', lazy=True)
    disease_incidents = db.relationship('DiseaseIncident', backref='reporter', lazy=True)
    
    def set_farm_location(self, latitude, longitude):
        """Set farm location from lat/lon coordinates"""
        self.farm_latitude = latitude
        self.farm_longitude = longitude
        self.farm_location = f'POINT({longitude} {latitude})'
    
    def get_farm_coordinates(self):
        """Get farm coordinates as dict"""
        if self.farm_latitude and self.farm_longitude:
            return {
                'latitude': self.farm_latitude,
                'longitude': self.farm_longitude
            }
        return None

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


class DiseaseIncident(db.Model):
    """
    Model for geo-tagged pest/disease incidents reported by farmers.
    Supports spatial clustering and outbreak detection.
    """
    __tablename__ = 'disease_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Reporter information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reporter_name = db.Column(db.String(200), nullable=False)
    reporter_email = db.Column(db.String(120), nullable=False)
    
    # Disease/Pest information
    disease_name = db.Column(db.String(200), nullable=False, index=True)
    disease_type = db.Column(db.String(100), nullable=False)  # pest, fungal, bacterial, viral
    crop_affected = db.Column(db.String(200), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, critical
    
    # Geospatial data
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location = db.Column(Geometry('POINT', srid=4326), nullable=False, index=True)  # PostGIS indexable
    address = db.Column(db.String(500), nullable=True)
    
    # GeoJSON for API responses
    geojson = db.Column(db.Text, nullable=True)
    
    # Additional details
    description = db.Column(db.Text, nullable=True)
    affected_area_hectares = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    
    # Status tracking
    status = db.Column(db.String(50), nullable=False, default='reported')  # reported, verified, resolved
    verified_by_expert = db.Column(db.Boolean, default=False)
    expert_notes = db.Column(db.Text, nullable=True)
    
    # Outbreak association
    outbreak_zone_id = db.Column(db.Integer, db.ForeignKey('outbreak_zones.id'), nullable=True)
    
    # Timestamps
    reported_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_location(self, latitude, longitude):
        """Set location from lat/lon coordinates"""
        self.latitude = latitude
        self.longitude = longitude
        self.location = f'POINT({longitude} {latitude})'
        # Generate GeoJSON
        self.geojson = f'{{"type":"Point","coordinates":[{longitude},{latitude}]}}'
    
    def to_dict(self, include_geojson=True):
        """Convert incident to dictionary"""
        result = {
            'id': self.id,
            'incident_id': self.incident_id,
            'user_id': self.user_id,
            'reporter_name': self.reporter_name,
            'reporter_email': self.reporter_email,
            'disease_name': self.disease_name,
            'disease_type': self.disease_type,
            'crop_affected': self.crop_affected,
            'severity': self.severity,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'description': self.description,
            'affected_area_hectares': self.affected_area_hectares,
            'image_url': self.image_url,
            'status': self.status,
            'verified_by_expert': self.verified_by_expert,
            'expert_notes': self.expert_notes,
            'outbreak_zone_id': self.outbreak_zone_id,
            'reported_at': self.reported_at.isoformat(),
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_geojson and self.geojson:
            import json
            result['geojson'] = json.loads(self.geojson)
        
        return result
    
    def to_geojson_feature(self):
        """Convert to GeoJSON Feature for mapping"""
        import json
        return {
            'type': 'Feature',
            'geometry': json.loads(self.geojson) if self.geojson else None,
            'properties': {
                'incident_id': self.incident_id,
                'disease_name': self.disease_name,
                'disease_type': self.disease_type,
                'crop_affected': self.crop_affected,
                'severity': self.severity,
                'status': self.status,
                'reported_at': self.reported_at.isoformat(),
                'reporter_name': self.reporter_name
            }
        }


# Create spatial index for efficient geospatial queries
Index('idx_disease_incidents_location', DiseaseIncident.location, postgresql_using='gist')


class OutbreakZone(db.Model):
    """
    Model for identified outbreak zones based on spatial clustering.
    Represents areas with multiple disease incidents within proximity.
    """
    __tablename__ = 'outbreak_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Zone details
    disease_name = db.Column(db.String(200), nullable=False)
    crop_affected = db.Column(db.String(200), nullable=False)
    severity_level = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, critical
    
    # Geospatial data - center point of the cluster
    center_latitude = db.Column(db.Float, nullable=False)
    center_longitude = db.Column(db.Float, nullable=False)
    center_location = db.Column(Geometry('POINT', srid=4326), nullable=False, index=True)
    
    # Radius in kilometers
    radius_km = db.Column(db.Float, nullable=False, default=50.0)
    
    # Cluster information
    incident_count = db.Column(db.Integer, nullable=False, default=0)
    total_affected_area = db.Column(db.Float, nullable=True)  # Total hectares
    
    # Status
    status = db.Column(db.String(50), nullable=False, default='active')  # active, monitoring, resolved
    risk_level = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, extreme
    
    # AI-generated preventative measures
    preventative_measures = db.Column(db.Text, nullable=True)
    emergency_recommendations = db.Column(db.Text, nullable=True)
    
    # Timestamps
    detected_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    incidents = db.relationship('DiseaseIncident', backref='outbreak_zone', lazy='dynamic')
    alerts = db.relationship('OutbreakAlert', backref='zone', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_center_location(self, latitude, longitude):
        """Set center location from lat/lon coordinates"""
        self.center_latitude = latitude
        self.center_longitude = longitude
        self.center_location = f'POINT({longitude} {latitude})'
    
    def to_dict(self, include_incidents=False):
        """Convert outbreak zone to dictionary"""
        result = {
            'id': self.id,
            'zone_id': self.zone_id,
            'disease_name': self.disease_name,
            'crop_affected': self.crop_affected,
            'severity_level': self.severity_level,
            'center_latitude': self.center_latitude,
            'center_longitude': self.center_longitude,
            'radius_km': self.radius_km,
            'incident_count': self.incident_count,
            'total_affected_area': self.total_affected_area,
            'status': self.status,
            'risk_level': self.risk_level,
            'preventative_measures': self.preventative_measures,
            'emergency_recommendations': self.emergency_recommendations,
            'detected_at': self.detected_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
        
        if include_incidents:
            result['incidents'] = [inc.to_dict(include_geojson=False) for inc in self.incidents.all()]
        
        return result
    
    def to_geojson_feature(self):
        """Convert to GeoJSON Feature with circle radius"""
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [self.center_longitude, self.center_latitude]
            },
            'properties': {
                'zone_id': self.zone_id,
                'disease_name': self.disease_name,
                'crop_affected': self.crop_affected,
                'severity_level': self.severity_level,
                'radius_km': self.radius_km,
                'incident_count': self.incident_count,
                'status': self.status,
                'risk_level': self.risk_level,
                'detected_at': self.detected_at.isoformat()
            }
        }


Index('idx_outbreak_zones_location', OutbreakZone.center_location, postgresql_using='gist')


class OutbreakAlert(db.Model):
    """
    Model for tracking emergency alerts sent to farmers in outbreak zones.
    """
    __tablename__ = 'outbreak_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Alert target
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outbreak_zone_id = db.Column(db.Integer, db.ForeignKey('outbreak_zones.id'), nullable=False)
    
    # Alert details
    alert_type = db.Column(db.String(50), nullable=False)  # proximity_warning, outbreak_detected, preventive_action
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, urgent
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Distance of farmer from outbreak center
    distance_km = db.Column(db.Float, nullable=True)
    
    # PDF report if generated
    pdf_report_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    
    # Status tracking
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='outbreak_alerts')
    pdf_report = db.relationship('File', foreign_keys=[pdf_report_id])
    
    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'user_id': self.user_id,
            'outbreak_zone_id': self.outbreak_zone_id,
            'alert_type': self.alert_type,
            'priority': self.priority,
            'title': self.title,
            'message': self.message,
            'distance_km': self.distance_km,
            'pdf_report_id': self.pdf_report_id,
            'sent_at': self.sent_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }
