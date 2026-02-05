from datetime import datetime
from backend.extensions import db
import json

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., Tractor, Harvester, Drone
    description = db.Column(db.Text)
    hourly_rate = db.Column(db.Float, nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255))
    
    # Specs as JSON
    specifications = db.Column(db.Text) # e.g., {"HP": 50, "Fuel": "Diesel"}
    
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('RentalBooking', backref='equipment', lazy='dynamic')
    availability = db.relationship('AvailabilityCalendar', backref='equipment', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'hourly_rate': self.hourly_rate,
            'daily_rate': self.daily_rate,
            'location': self.location,
            'image_url': self.image_url,
            'specifications': json.loads(self.specifications) if self.specifications else {},
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat()
        }

class RentalBooking(db.Model):
    __tablename__ = 'rental_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    total_price = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float, nullable=False)
    
    # State Machine: PENDING -> PAID -> PICKED_UP -> COMPLETED / CANCELLED / DISPUTED
    status = db.Column(db.String(20), default='PENDING')
    
    payment_intent_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    escrow = db.relationship('PaymentEscrow', backref='booking', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'renter_id': self.renter_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'total_price': self.total_price,
            'security_deposit': self.security_deposit,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class AvailabilityCalendar(db.Model):
    __tablename__ = 'availability_calendar'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(100)) # e.g., Maintenance, Personal Use

class PaymentEscrow(db.Model):
    __tablename__ = 'payment_escrows'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('rental_bookings.id'), nullable=False)
    
    total_amount = db.Column(db.Float, nullable=False)
    held_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # HELD -> RELEASED -> REFUNDED
    status = db.Column(db.String(20), default='HELD')
    released_at = db.Column(db.DateTime)
    
    dispute_reason = db.Column(db.Text)
    transaction_ref = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'held_at': self.held_at.isoformat(),
            'released_at': self.released_at.isoformat() if self.released_at else None
        }
