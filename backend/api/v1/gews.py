from flask import Blueprint, jsonify, request
from backend.models.gews import OutbreakZone, DiseaseIncident
from backend.services.pathogen_service import PathogenPropagationService
from backend.auth_utils import token_required
from backend.extensions import db

gews_bp = Blueprint('gews', __name__)

@gews_bp.route('/heatmap', methods=['GET'])
@token_required
def get_heatmap(current_user):
    """Returns aggregated heatmap data for spatial visualization."""
    data = PathogenPropagationService.get_risk_heatmap_data()
    return jsonify({
        'status': 'success',
        'data': data
    })

@gews_bp.route('/zone/<int:zone_id>/simulate', methods=['POST'])
@token_required
def manual_simulate(current_user, zone_id):
    """Manually triggers propagation simulation for a zone."""
    # TODO: Add admin/expert check
    zone = PathogenPropagationService.simulate_propagation(zone_id)
    if not zone:
        return jsonify({'status': 'error', 'message': 'Zone not found'}), 404
        
    return jsonify({
        'status': 'success',
        'data': zone.to_dict()
    })

@gews_bp.route('/zones/containment', methods=['GET'])
@token_required
def list_active_containments(current_user):
    """Lists all zones under autonomous containment."""
    zones = OutbreakZone.query.filter(OutbreakZone.containment_status != 'NONE').all()
    return jsonify({
        'status': 'success',
        'data': [z.to_dict() for z in zones]
    })
