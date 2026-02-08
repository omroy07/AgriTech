from flask_socketio import emit, join_room, leave_room
from backend.extensions import socketio
from flask import request
import logging

logger = logging.getLogger(__name__)

@socketio.on('join_thread', namespace='/forum')
def on_join(data):
    """Join a WebSocket room for a specific forum thread"""
    thread_id = data.get('thread_id')
    if thread_id:
        room = f"thread_{thread_id}"
        join_room(room)
        logger.info(f"User {request.sid} joined room: {room}")
        emit('status', {'msg': f'Joined thread {thread_id}'}, room=room)

@socketio.on('leave_thread', namespace='/forum')
def on_leave(data):
    """Leave a forum thread WebSocket room"""
    thread_id = data.get('thread_id')
    if thread_id:
        room = f"thread_{thread_id}"
        leave_room(room)
        logger.info(f"User {request.sid} left room: {room}")

@socketio.on('typing', namespace='/forum')
def on_typing(data):
    """Broadcast typing indicator to other users in the thread"""
    thread_id = data.get('thread_id')
    user_name = data.get('username', 'Someone')
    is_typing = data.get('is_typing', False)
    
    if thread_id:
        room = f"thread_{thread_id}"
        emit('user_typing', {
            'username': user_name,
            'is_typing': is_typing
        }, room=room, include_self=False)

def broadcast_new_comment(thread_id, comment_data):
    """
    Utility function to broadcast a new comment to all users in a thread room.
    Called from the service layer after a comment is saved.
    """
    room = f"thread_{thread_id}"
    socketio.emit('new_post_comment', comment_data, room=room, namespace='/forum')

def broadcast_thread_update(thread_id, update_data):
    """Broadcast thread edits/status changes (like locking)"""
    room = f"thread_{thread_id}"
    socketio.emit('thread_updated', update_data, room=room, namespace='/forum')
