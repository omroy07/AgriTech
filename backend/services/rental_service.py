from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.equipment import Equipment, RentalBooking, AvailabilityCalendar, PaymentEscrow
import logging

logger = logging.getLogger(__name__)

class RentalService:
    @staticmethod
    def list_equipment(category=None, location=None, max_rate=None):
        """Search and filter equipment listings"""
        query = Equipment.query.filter_by(is_available=True)
        
        if category:
            query = query.filter(Equipment.category == category)
        if location:
            query = query.filter(Equipment.location.ilike(f"%{location}%"))
        if max_rate:
            query = query.filter(Equipment.daily_rate <= float(max_rate))
            
        return query.all()

    @staticmethod
    def create_booking(equipment_id, renter_id, start_time, end_time):
        """Create a new rental booking with conflict checks"""
        try:
            equipment = Equipment.query.get(equipment_id)
            if not equipment:
                return None, "Equipment not found"
            
            # Check availability
            if not RentalService.is_available(equipment_id, start_time, end_time):
                return None, "Equipment is already booked for these dates."
            
            # Calculate price
            duration = end_time - start_time
            days = max(1, duration.days)
            total_price = days * equipment.daily_rate
            security_deposit = total_price * 0.2 # 20% deposit
            
            booking = RentalBooking(
                equipment_id=equipment_id,
                renter_id=renter_id,
                start_time=start_time,
                end_time=end_time,
                total_price=total_price,
                security_deposit=security_deposit,
                status='PENDING'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            return booking, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def is_available(equipment_id, start_time, end_time):
        """Check if equipment is available for a given range (no overlap)"""
        # Check existing bookings that are not CANCELLED
        overlaps = RentalBooking.query.filter(
            RentalBooking.equipment_id == equipment_id,
            RentalBooking.status != 'CANCELLED',
            RentalBooking.start_time < end_time,
            RentalBooking.end_time > start_time
        ).count()
        
        if overlaps > 0:
            return False
            
        # Check blocked dates in calendar
        blocked = AvailabilityCalendar.query.filter(
            AvailabilityCalendar.equipment_id == equipment_id,
            AvailabilityCalendar.is_blocked == True,
            AvailabilityCalendar.date >= start_time.date(),
            AvailabilityCalendar.date <= end_time.date()
        ).count()
        
        return blocked == 0

    @staticmethod
    def update_booking_status(booking_id, new_status, user_id):
        """Manage the booking lifecycle state machine"""
        booking = RentalBooking.query.get(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Simple state machine validation
        allowed = {
            'PENDING': ['PAID', 'CANCELLED'],
            'PAID': ['PICKED_UP', 'CANCELLED'],
            'PICKED_UP': ['COMPLETED', 'DISPUTED'],
            'COMPLETED': [],
            'CANCELLED': [],
            'DISPUTED': ['COMPLETED']
        }
        
        if new_status not in allowed.get(booking.status, []):
            return None, f"Cannot transition from {booking.status} to {new_status}"
            
        # Permission checks
        equipment = Equipment.query.get(booking.equipment_id)
        if new_status == 'PICKED_UP' and user_id != equipment.owner_id:
            return None, "Only owner can confirm pick-up"
            
        booking.status = new_status
        db.session.commit()
        
        # Trigger escrow actions
        if new_status == 'PAID':
            from backend.services.escrow_service import EscrowService
            EscrowService.hold_funds(booking)
        elif new_status == 'COMPLETED':
            from backend.services.escrow_service import EscrowService
            EscrowService.release_funds(booking)
            
        return booking, None
