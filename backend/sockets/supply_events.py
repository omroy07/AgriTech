from flask_socketio import emit, join_room, leave_room
from backend.extensions import socketio
from flask import request
import logging

logger = logging.getLogger(__name__)

@socketio.on('join_batch_tracking', namespace='/traceability')
def on_join(data):
    """Join a room dedicated to tracking a specific batch's real-time updates"""
    batch_id = data.get('batch_id')
    if batch_id:
        join_room(batch_id)
        logger.info(f"User {request.sid} joined tracking room for batch {batch_id}")
        emit('tracking_status', {'msg': f'Successfully joined tracking for {batch_id}'})

@socketio.on('leave_batch_tracking', namespace='/traceability')
def on_leave(data):
    """Leave a batch tracking room"""
    batch_id = data.get('batch_id')
    if batch_id:
        leave_room(batch_id)
        logger.info(f"User {request.sid} left tracking room for batch {batch_id}")

def broadcast_batch_update(batch_id, update_data):
    """
    Utility function to broadcast status changes to all users 
    tracking a specific batch in real-time.
    """
    socketio.emit(
        'batch_update_received', 
        update_data, 
        room=batch_id, 
        namespace='/traceability'
    )
    logger.info(f"Broadcasted update for batch {batch_id}")
