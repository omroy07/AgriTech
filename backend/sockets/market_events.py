from flask_socketio import emit, join_room, leave_room
from backend.extensions.socketio import socketio
from backend.utils.logger import logger

@socketio.on('join_market', namespace='/market')
def handle_join_market(data):
    district = data.get('district', 'all')
    join_room(district)
    logger.info(f"User joined market room: {district}")
    emit('market_status', {'message': f'Joined market updates for {district}'})

@socketio.on('leave_market', namespace='/market')
def handle_leave_market(data):
    district = data.get('district', 'all')
    leave_room(district)
    logger.info(f"User left market room: {district}")

def broadcast_market_update(prices, district='all'):
    """Utility to broadcast price updates to specific rooms."""
    socketio.emit('market_update', {'prices': prices}, namespace='/market', room=district)
