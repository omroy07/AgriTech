from datetime import datetime
from backend.extensions import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True) # Changed to nullable for now if needed
    phone = db.Column(db.String(20), unique=True, nullable=True)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Multilingual preference
    language_preference = db.Column(db.String(10), default='en')
    
    # Email verification fields
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Notification preferences
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    
    notifications = db.relationship('Notification', backref='user', lazy=True)
    files = db.relationship('File', backref='user', lazy=True)

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

    def __repr__(self):
        return f'<File {self.id} - {self.original_name}>'


class FarmAsset(db.Model):
    """
    Represents farm machinery and equipment for predictive maintenance tracking.
    """
    __tablename__ = 'farm_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Asset details
    asset_type = db.Column(db.String(100), nullable=False)  # tractor, tiller, pump, harvester
    asset_name = db.Column(db.String(200), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    purchase_date = db.Column(db.DateTime, nullable=True)
    purchase_price = db.Column(db.Float, nullable=True)
    
    # Health metrics
    health_score = db.Column(db.Float, default=100.0)  # 0-100
    predicted_days_to_failure = db.Column(db.Integer, nullable=True)
    last_maintenance_date = db.Column(db.DateTime, nullable=True)
    next_maintenance_due = db.Column(db.DateTime, nullable=True)
    total_runtime_hours = db.Column(db.Float, default=0.0)
    
    # Telemetry data (JSON stored as Text)
    last_telemetry = db.Column(db.Text, nullable=True)  # Store recent telemetry as JSON string
    
    # Status
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, MAINTENANCE, FAILED, RETIRED
    alert_threshold_days = db.Column(db.Integer, default=7)  # Alert when failure prediction < this
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    maintenance_logs = db.relationship('MaintenanceLog', backref='asset', lazy=True, cascade='all, delete-orphan')
    owner = db.relationship('User', backref='farm_assets')
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'user_id': self.user_id,
            'asset_type': self.asset_type,
            'asset_name': self.asset_name,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'health_score': self.health_score,
            'predicted_days_to_failure': self.predicted_days_to_failure,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'next_maintenance_due': self.next_maintenance_due.isoformat() if self.next_maintenance_due else None,
            'total_runtime_hours': self.total_runtime_hours,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<FarmAsset {self.asset_id} - {self.asset_name}>'


class MaintenanceLog(db.Model):
    """
    Tracks maintenance history and issues for farm assets.
    """
    __tablename__ = 'maintenance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.String(50), unique=True, nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('farm_assets.id'), nullable=False)
    
    # Maintenance details
    maintenance_type = db.Column(db.String(50), nullable=False)  # ROUTINE, REPAIR, EMERGENCY, INSPECTION
    description = db.Column(db.Text, nullable=False)
    parts_replaced = db.Column(db.Text, nullable=True)  # JSON string of parts
    cost = db.Column(db.Float, default=0.0)
    
    # Condition assessment
    pre_maintenance_health = db.Column(db.Float, nullable=True)
    post_maintenance_health = db.Column(db.Float, nullable=True)
    issues_found = db.Column(db.Text, nullable=True)
    
    # Technician info
    technician_name = db.Column(db.String(200), nullable=True)
    technician_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    scheduled_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status
    status = db.Column(db.String(20), default='SCHEDULED')  # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    
    def to_dict(self):
        return {
            'id': self.id,
            'log_id': self.log_id,
            'asset_id': self.asset_id,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'cost': self.cost,
            'pre_maintenance_health': self.pre_maintenance_health,
            'post_maintenance_health': self.post_maintenance_health,
            'technician_name': self.technician_name,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<MaintenanceLog {self.log_id} - {self.maintenance_type}>'


class LogisticsOrder(db.Model):
    """
    Manages harvest pickup and transportation logistics coordination.
    """
    __tablename__ = 'logistics_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Pickup details
    crop_type = db.Column(db.String(100), nullable=False)
    quantity_tons = db.Column(db.Float, nullable=False)
    pickup_location = db.Column(db.String(300), nullable=False)
    pickup_latitude = db.Column(db.Float, nullable=True)
    pickup_longitude = db.Column(db.Float, nullable=True)
    
    # Destination
    destination_location = db.Column(db.String(300), nullable=False)
    destination_latitude = db.Column(db.Float, nullable=True)
    destination_longitude = db.Column(db.Float, nullable=True)
    
    # Scheduling
    requested_pickup_date = db.Column(db.DateTime, nullable=False)
    scheduled_pickup_date = db.Column(db.DateTime, nullable=True)
    actual_pickup_date = db.Column(db.DateTime, nullable=True)
    estimated_delivery_date = db.Column(db.DateTime, nullable=True)
    actual_delivery_date = db.Column(db.DateTime, nullable=True)
    
    # Logistics coordination
    route_group_id = db.Column(db.String(50), nullable=True)  # Groups nearby pickups
    transport_vehicle_id = db.Column(db.String(50), nullable=True)
    driver_name = db.Column(db.String(200), nullable=True)
    driver_phone = db.Column(db.String(20), nullable=True)
    
    # Cost calculation
    base_cost = db.Column(db.Float, nullable=True)
    shared_cost_discount = db.Column(db.Float, default=0.0)  # Discount from route grouping
    final_cost = db.Column(db.Float, nullable=True)
    distance_km = db.Column(db.Float, nullable=True)
    
    # Status tracking
    status = db.Column(db.String(30), default='PENDING')  # PENDING, SCHEDULED, IN_TRANSIT, DELIVERED, CANCELLED
    priority = db.Column(db.String(20), default='NORMAL')  # URGENT, HIGH, NORMAL, LOW
    
    # Special instructions
    special_instructions = db.Column(db.Text, nullable=True)
    requires_refrigeration = db.Column(db.Boolean, default=False)
    requires_covered_transport = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship('User', backref='logistics_orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'crop_type': self.crop_type,
            'quantity_tons': self.quantity_tons,
            'pickup_location': self.pickup_location,
            'destination_location': self.destination_location,
            'requested_pickup_date': self.requested_pickup_date.isoformat(),
            'scheduled_pickup_date': self.scheduled_pickup_date.isoformat() if self.scheduled_pickup_date else None,
            'actual_pickup_date': self.actual_pickup_date.isoformat() if self.actual_pickup_date else None,
            'route_group_id': self.route_group_id,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'base_cost': self.base_cost,
            'shared_cost_discount': self.shared_cost_discount,
            'final_cost': self.final_cost,
            'distance_km': self.distance_km,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<LogisticsOrder {self.order_id} - {self.status}>'
