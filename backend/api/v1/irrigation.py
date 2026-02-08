from flask import Blueprint, request, jsonify
from backend.services.irrigation_service import IrrigationService
from backend.models.irrigation import IrrigationZone, ValveStatus
from auth_utils import token_required
from backend.extensions import db

irrigation_bp = Blueprint('irrigation', __name__)

@irrigation_bp.route('/zones', methods=['GET'])
@token_required
def list_zones(current_user):
    farm_id = request.args.get('farm_id')
    query = IrrigationZone.query
    if farm_id:
        query = query.filter_by(farm_id=farm_id)
    
    zones = query.all()
    return jsonify({
        'status': 'success',
        'data': [z.to_dict() for z in zones]
    }), 200

@irrigation_bp.route('/telemetry', methods=['POST'])
def receive_telemetry():
    """Endpoint for IoT gateway to push sensor data"""
    data = request.get_json()
    if not data or 'zone_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400
        
    log, error = IrrigationService.process_telemetry(
        zone_id=data['zone_id'],
        moisture=data['moisture'],
        temperature=data['temperature'],
        ph=data['ph_level']
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({'status': 'success', 'data': log.to_dict()}), 201

@irrigation_bp.route('/control/<int:zone_id>', methods=['PATCH'])
@token_required
def control_valve(current_user, zone_id):
    """Manual override for valve status"""
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in [v.value for v in ValveStatus]:
        return jsonify({'status': 'error', 'message': 'Invalid status'}), 400
        
    success = IrrigationService.manual_override(zone_id, new_status)
    if success:
        return jsonify({'status': 'success', 'message': f'Valve set to {new_status}'}), 200
        
    return jsonify({'status': 'error', 'message': 'Zone not found'}), 404

@irrigation_bp.route('/analytics/<int:zone_id>', methods=['GET'])
@token_required
def get_analytics(current_user, zone_id):
    stats = IrrigationService.get_zone_analytics(zone_id)
    return jsonify({'status': 'success', 'data': stats}), 200
