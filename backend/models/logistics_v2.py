from datetime import datetime
from backend.extensions import db

class DriverProfile(db.Model):
    __tablename__ = 'driver_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    contact_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='AVAILABLE') # AVAILABLE, ON_TRIP, OFF_DUTY
    
    rating = db.Column(db.Float, default=5.0)
    total_trips = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    routes = db.relationship('TransportRoute', backref='driver', lazy='dynamic')

class DeliveryVehicle(db.Model):
    __tablename__ = 'delivery_vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50)) # e.g., Refrigerator Truck, Small Pickup
    
    capacity_kg = db.Column(db.Float, nullable=False)
    fuel_type = db.Column(db.String(20)) # Diesel, Petrol, Electric
    avg_fuel_consumption = db.Column(db.Float) # liters per 100km
    
    status = db.Column(db.String(20), default='IDLE') # IDLE, ACTIVE, MAINTENANCE
    last_maintenance_date = db.Column(db.DateTime)
    mileage = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    routes = db.relationship('TransportRoute', backref='vehicle', lazy='dynamic')
    fuel_logs = db.relationship('FuelLog', backref='vehicle', lazy='dynamic')

class TransportRoute(db.Model):
    __tablename__ = 'transport_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver_profiles.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('delivery_vehicles.id'))
    
    origin = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    
    origin_coords = db.Column(db.String(100)) # "lat,lng"
    destination_coords = db.Column(db.String(100)) # "lat,lng"
    
    estimated_distance = db.Column(db.Float) # km
    actual_distance = db.Column(db.Float)
    
    status = db.Column(db.String(20), default='PENDING') # PENDING, IN_TRANSIT, COMPLETED, CANCELLED
    
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    
    cargo_weight = db.Column(db.Float)
    cargo_description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'origin': self.origin,
            'destination': self.destination,
            'status': self.status,
            'distance': self.estimated_distance,
            'weight': self.cargo_weight,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }

class FuelLog(db.Model):
    __tablename__ = 'fuel_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('delivery_vehicles.id'), nullable=False)
    
    fuel_quantity = db.Column(db.Float, nullable=False) # Liters
    cost = db.Column(db.Float)
    mileage_at_refill = db.Column(db.Float)
    
    # Sustainability (L3-1558)
    carbon_footprint_kg = db.Column(db.Float, default=0.0)
    
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class PhytoSanitaryCertificate(db.Model):
    """
    Autonomously generated Phyto-Sanitary Certificate for cross-border shipments (L3-1631).
    The JSON payload is SHA-256 signed for regulatory verification.
    """
    __tablename__ = 'phyto_sanitary_certificates'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('supply_batches.id'), nullable=False)

    # Certificate metadata
    certificate_number = db.Column(db.String(64), unique=True, nullable=False)
    issuing_authority = db.Column(db.String(150), default='AgriTech Digital Authority')
    origin_country = db.Column(db.String(80), nullable=False)
    destination_country = db.Column(db.String(80), nullable=False)
    commodity = db.Column(db.String(100))
    declared_quantity_kg = db.Column(db.Float)

    # Signed JSON payload
    certificate_payload_json = db.Column(db.Text)   # Full JSON cert body
    signature_hash = db.Column(db.String(64), nullable=False)  # SHA-256 sign

    # Status: DRAFT, ISSUED, ACCEPTED, REJECTED, EXPIRED
    status = db.Column(db.String(20), default='DRAFT')

    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'certificate_number': self.certificate_number,
            'route_id': self.route_id,
            'batch_id': self.batch_id,
            'origin_country': self.origin_country,
            'destination_country': self.destination_country,
            'commodity': self.commodity,
            'quantity_kg': self.declared_quantity_kg,
            'signature_hash': self.signature_hash,
            'status': self.status,
            'issued_at': self.issued_at.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None
        }

class FreightEscrow(db.Model):
    """
    Smart-Contract Freight Release: funds held in escrow and released ONLY
    when GPS geo-fencing confirms delivery at warehouse coordinates (L3-1631).
    """
    __tablename__ = 'freight_escrows'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver_profiles.id'), nullable=False)

    # Financial value
    total_freight_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')

    # Geo-fence parameters for smart release
    destination_lat = db.Column(db.Float, nullable=False)
    destination_lng = db.Column(db.Float, nullable=False)
    geo_fence_radius_meters = db.Column(db.Float, default=200.0)

    # Delivery confirmation
    confirmed_delivery_lat = db.Column(db.Float)
    confirmed_delivery_lng = db.Column(db.Float)
    geo_fence_passed = db.Column(db.Boolean, default=False)
    delivery_proof_hash = db.Column(db.String(64))

    # Escrow state: HELD, RELEASED, DISPUTED, REFUNDED
    status = db.Column(db.String(20), default='HELD')

    # Ledger reference for the release transaction
    release_ledger_txn_id = db.Column(db.Integer, db.ForeignKey('ledger_transactions.id'))

    # Dynamic price adjustment
    base_price = db.Column(db.Float)
    fuel_surcharge = db.Column(db.Float, default=0.0)
    customs_delay_penalty = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'driver_id': self.driver_id,
            'total_freight_amount': self.total_freight_amount,
            'final_amount': self.final_amount,
            'fuel_surcharge': self.fuel_surcharge,
            'customs_delay_penalty': self.customs_delay_penalty,
            'geo_fence_passed': self.geo_fence_passed,
            'status': self.status,
            'released_at': self.released_at.isoformat() if self.released_at else None
        }

class CustomsCheckpoint(db.Model):
    """
    Tracks customs wait times at border crossings to drive dynamic freight repricing (L3-1631).
    """
    __tablename__ = 'customs_checkpoints'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'), nullable=False)

    checkpoint_name = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(80))
    arrived_at = db.Column(db.DateTime, default=datetime.utcnow)
    cleared_at = db.Column(db.DateTime)

    # Wait time in hours (calculated on clearance)
    wait_hours = db.Column(db.Float, default=0.0)
    # Status: PENDING, CLEARED, REJECTED, HELD_FOR_INSPECTION
    status = db.Column(db.String(30), default='PENDING')

    # Phyto cert verified at this checkpoint
    phyto_cert_id = db.Column(db.Integer, db.ForeignKey('phyto_sanitary_certificates.id'))
    inspector_notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'checkpoint_name': self.checkpoint_name,
            'country': self.country,
            'wait_hours': self.wait_hours,
            'status': self.status,
            'arrived_at': self.arrived_at.isoformat(),
            'cleared_at': self.cleared_at.isoformat() if self.cleared_at else None
        }

class GPSTelemetry(db.Model):
    """
    Real-time GPS position stream from vehicles (L3-1631).
    Powers the geo-fence evaluation in FreightEscrow smart-contract release.
    """
    __tablename__ = 'gps_telemetry'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('delivery_vehicles.id'), nullable=False)

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed_kmh = db.Column(db.Float, default=0.0)
    heading_degrees = db.Column(db.Float)

    # Fuel volatility snapshot at this ping
    fuel_price_per_liter = db.Column(db.Float)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
