from flask_socketio import join_room, leave_room
from backend.extensions.socketio import socketio
from backend.utils.logger import logger

@socketio.on('join_notifications')
def handle_join_notifications(data):
    """
    User joins their private notification room.
    Expected data: { 'user_id': 123 }
    """
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        logger.info("User %s joined notification room", user_id)


@socketio.on('leave_notifications')
def handle_leave_notifications(data):
    """
    User leaves their private notification room.
    """
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        leave_room(room)
        logger.info("User %s left notification room", user_id)
