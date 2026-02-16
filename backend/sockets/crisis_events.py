from flask_socketio import emit, join_room, leave_room
from backend.extensions import socketio
from backend.services.pathogen_service import PathogenPropagationService
import logging

logger = logging.getLogger(__name__)

@socketio.on('connect', namespace='/crisis')
def handle_connect():
    """Client connected to the crisis monitoring namespace."""
    logger.info("Admin/Viewer joined Crisis Monitoring Namespace")
    # Send initial heatmap data
    heatmap = PathogenPropagationService.get_risk_heatmap_data()
    emit('heatmap_init', {'zones': heatmap})

@socketio.on('subscribe_zone', namespace='/crisis')
def handle_zone_subscription(data):
    """Client wants to monitor a specific outbreak zone."""
    zone_id = data.get('zone_id')
    if zone_id:
        join_room(f'zone_{zone_id}')
        logger.info(f"Client monitoring zone: {zone_id}")

@socketio.on('unsubscribe_zone', namespace='/crisis')
def handle_zone_unsubscription(data):
    """Client stops monitoring a specific zone."""
    zone_id = data.get('zone_id')
    if zone_id:
        leave_room(f'zone_{zone_id}')

@socketio.on('trigger_manual_simulation', namespace='/crisis')
def handle_manual_sim(data):
    """Admin manually re-runs propagation simulation."""
    zone_id = data.get('zone_id')
    if zone_id:
        # This will update DB and emit 'pathogen_update'
        PathogenPropagationService.simulate_propagation(zone_id)
        emit('sim_complete', {'status': 'success', 'zone_id': zone_id})
