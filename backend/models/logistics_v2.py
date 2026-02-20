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
