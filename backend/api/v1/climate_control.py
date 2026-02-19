from flask import Blueprint, request, jsonify
from backend.services.climate_service import ClimateService
from backend.models.climate import SensorNode, ClimateZone, AutomationTrigger
from auth_utils import token_required

climate_bp = Blueprint('climate_control', __name__)

@climate_bp.route('/telemetry/<string:node_uid>', methods=['POST'])
def post_telemetry(node_uid):
    """IoT endpoint for sensor nodes to post data."""
    data = request.get_json()
    log, error = ClimateService.process_telemetry(node_uid, data)
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 404
        
    return jsonify({
        'status': 'success',
        'timestamp': log.timestamp.isoformat()
    }), 201

@climate_bp.route('/zones/<int:farm_id>', methods=['GET'])
@token_required
def get_farm_zones(current_user, farm_id):
    zones = ClimateZone.query.filter_by(farm_id=farm_id).all()
    return jsonify({
        'status': 'success',
        'data': [z.to_dict() for z in zones]
    }), 200

@climate_bp.route('/analytics/<int:zone_id>', methods=['GET'])
@token_required
def get_analytics(current_user, zone_id):
    analytics = ClimateService.get_zone_analytics(zone_id)
    if not analytics:
        return jsonify({'status': 'error', 'message': 'No data for this zone'}), 404
        
    return jsonify({
        'status': 'success',
        'data': analytics
    }), 200

@climate_bp.route('/triggers', methods=['POST'])
@token_required
def create_trigger(current_user):
    data = request.get_json()
    import json
    trigger = AutomationTrigger(
        zone_id=data['zone_id'],
        name=data['name'],
        actor_type=data['actor'],
        condition_json=json.dumps(data['condition']),
        action_json=json.dumps(data['action'])
    )
    db.session.add(trigger)
    db.session.commit()
    return jsonify({'status': 'success', 'id': trigger.id}), 201

@climate_bp.route('/nodes/register', methods=['POST'])
@token_required
def register_node(current_user):
    data = request.get_json()
    from backend.extensions import db
    node = SensorNode(
        zone_id=data['zone_id'],
        uid=data['uid'],
        node_type=data.get('type', 'GENERIC'),
        firmware_version=data.get('firmware', '1.0.0')
    )
    db.session.add(node)
    db.session.commit()
    return jsonify({'status': 'success', 'id': node.id}), 201
