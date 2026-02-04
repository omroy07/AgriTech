from flask_socketio import emit, join_room
from backend.extensions import socketio
import logging

logger = logging.getLogger(__name__)

@socketio.on('join_rental_notifications', namespace='/rentals')
def on_join_rentals(data):
    """Join a room for receiving rental-related notifications (user-specific)"""
    user_id = data.get('user_id')
    if user_id:
        join_room(f"user_rentals_{user_id}")
        logger.info(f"User {user_id} joined rental notifications room.")

def broadcast_booking_update(booking, actor_id):
    """Notify both renter and owner about a booking status change"""
    from backend.models.equipment import Equipment
    equipment = Equipment.query.get(booking.equipment_id)
    
    # Notify Owner
    socketio.emit(
        'booking_updated',
        {
            'booking_id': booking.id,
            'status': booking.status,
            'message': f"Booking for {equipment.name} is now {booking.status}",
            'actor_id': actor_id
        },
        room=f"user_rentals_{equipment.owner_id}",
        namespace='/rentals'
    )
    
    # Notify Renter
    if actor_id != booking.renter_id:
        socketio.emit(
            'booking_updated',
            {
                'booking_id': booking.id,
                'status': booking.status,
                'message': f"Your booking for {equipment.name} is now {booking.status}",
                'actor_id': actor_id
            },
            room=f"user_rentals_{booking.renter_id}",
            namespace='/rentals'
        )
