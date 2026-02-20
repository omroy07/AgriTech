from flask_socketio import emit, join_room, leave_room
from backend.extensions import socketio
from backend.utils.logger import logger

@socketio.on('subscribe_alerts')
def handle_subscribe_alerts(data):
    """
    Subscribes a user to their private alert room.
    """
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        logger.info(f"User {user_id} subscribed to alert room: {room}")
        emit('subscription_success', {'room': room})
    
    # All users subscribe to global alerts
    join_room('global_alerts')

@socketio.on('unsubscribe_alerts')
def handle_unsubscribe_alerts(data):
    """
    Unsubscribes a user from their private alert room.
    """
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        leave_room(room)
        logger.info(f"User {user_id} unsubscribed from alert room: {room}")

@socketio.on('acknowledge_alert')
def handle_acknowledge_alert(data):
    """
    Handles client-side acknowledgement of an alert.
    """
    alert_id = data.get('alert_id')
    user_id = data.get('user_id')
    
    if alert_id and user_id:
        # Here you could potentially call AlertRegistry.mark_as_read
        # but usually that's better done via a REST API call for reliability
        logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
        emit('alert_acknowledged', {'alert_id': alert_id}, room=f"user_{user_id}")
