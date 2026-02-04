from datetime import datetime
from backend.extensions import db
from backend.models.equipment import RentalBooking, PaymentEscrow
import logging

logger = logging.getLogger(__name__)

class EscrowService:
    @staticmethod
    def hold_funds(booking):
        """Place funds in a virtual escrow hold"""
        try:
            total_hold = booking.total_price + booking.security_deposit
            
            escrow = PaymentEscrow(
                booking_id=booking.id,
                total_amount=total_hold,
                status='HELD',
                held_at=datetime.utcnow()
            )
            
            db.session.add(escrow)
            db.session.commit()
            logger.info(f"Funds held for booking {booking.id}: {total_hold}")
            return escrow
        except Exception as e:
            logger.error(f"Escrow hold failed: {str(e)}")
            return None

    @staticmethod
    def release_funds(booking):
        """Release held funds to the equipment owner after completion"""
        try:
            escrow = PaymentEscrow.query.filter_by(booking_id=booking.id, status='HELD').first()
            if not escrow:
                return False, "No funds held in escrow"
            
            # Logic: Release total_price to owner, refund security_deposit to renter
            escrow.status = 'RELEASED'
            escrow.released_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Funds released for booking {booking.id}")
            return True, None
        except Exception as e:
            logger.error(f"Escrow release failed: {str(e)}")
            return False, str(e)

    @staticmethod
    def refund_funds(booking):
        """Refund all funds to renter (e.g., if owner cancels)"""
        try:
            escrow = PaymentEscrow.query.filter_by(booking_id=booking.id, status='HELD').first()
            if not escrow:
                return False, "No funds held in escrow"
            
            escrow.status = 'REFUNDED'
            escrow.released_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Funds refunded for booking {booking.id}")
            return True, None
        except Exception as e:
            logger.error(f"Escrow refund failed: {str(e)}")
            return False, str(e)
            
    @staticmethod
    def handle_dispute(booking_id, reason):
        """Mark escrow as disputed for manual intervention"""
        escrow = PaymentEscrow.query.filter_by(booking_id=booking_id).first()
        if escrow:
            escrow.dispute_reason = reason
            db.session.commit()
            return True
        return False
