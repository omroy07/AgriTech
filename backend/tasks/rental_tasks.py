from backend.celery_app import celery_app
from backend.extensions import db
from backend.models.equipment import RentalBooking, Equipment
from backend.services.escrow_service import EscrowService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='tasks.check_overdue_rentals')
def check_overdue_rentals_task():
    """Daily check for rentals that weren't returned on time"""
    try:
        now = datetime.utcnow()
        overdue_bookings = RentalBooking.query.filter(
            RentalBooking.status == 'PICKED_UP',
            RentalBooking.end_time < now
        ).all()
        
        for booking in overdue_bookings:
            # Here we would send notifications or escalate the dispute
            logger.warning(f"Booking {booking.id} is overdue! End time was {booking.end_time}")
            
            # Auto-dispute if overdue by > 24h
            if (now - booking.end_time) > timedelta(days=1):
                booking.status = 'DISPUTED'
                EscrowService.handle_dispute(booking.id, "Equipment not returned on time.")
                
        db.session.commit()
        return {'status': 'success', 'overdue_found': len(overdue_bookings)}
    except Exception as e:
        logger.error(f"Failed to check overdue rentals: {str(e)}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task(name='tasks.cleanup_expired_pending_bookings')
def cleanup_expired_pending_bookings_task():
    """Cleanup bookings that were never paid for within 2 hours"""
    threshold = datetime.utcnow() - timedelta(hours=2)
    expired = RentalBooking.query.filter(
        RentalBooking.status == 'PENDING',
        RentalBooking.created_at < threshold
    ).all()
    
    for b in expired:
        b.status = 'CANCELLED'
        
    db.session.commit()
    return {'status': 'success', 'cancelled_count': len(expired)}
