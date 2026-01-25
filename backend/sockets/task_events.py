from flask_socketio import emit, join_room, leave_room
from backend.extensions.socketio import socketio


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to AgriTech WebSocket server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    pass


@socketio.on('join_task')
def handle_join_task(data):
    """
    Client joins a room to receive updates for a specific task.
    Expected data: { 'task_id': 'abc123' }
    """
    task_id = data.get('task_id')
    if task_id:
        join_room(task_id)
        emit('joined_task', {
            'message': f'Joined room for task {task_id}',
            'task_id': task_id
        })


@socketio.on('leave_task')
def handle_leave_task(data):
    """
    Client leaves a task room.
    Expected data: { 'task_id': 'abc123' }
    """
    task_id = data.get('task_id')
    if task_id:
        leave_room(task_id)
        emit('left_task', {
            'message': f'Left room for task {task_id}',
            'task_id': task_id
        })


def emit_task_update(task_id, status, result=None, error=None):
    """
    Emit task update to all clients in the task room.
    Called from Celery tasks when they complete.
    """
    payload = {
        'task_id': task_id,
        'status': status
    }
    
    if result:
        payload['result'] = result
    if error:
        payload['error'] = error
    
    socketio.emit('task_update', payload, room=task_id)


def emit_task_started(task_id):
    """Emit when a task starts processing."""
    socketio.emit('task_started', {
        'task_id': task_id,
        'status': 'processing',
        'message': 'Task has started processing'
    }, room=task_id)


def emit_task_completed(task_id, result):
    """Emit when a task completes successfully."""
    socketio.emit('task_completed', {
        'task_id': task_id,
        'status': 'completed',
        'result': result
    }, room=task_id)


def emit_task_failed(task_id, error):
    """Emit when a task fails."""
    socketio.emit('task_failed', {
        'task_id': task_id,
        'status': 'failed',
        'error': str(error)
    }, room=task_id)
