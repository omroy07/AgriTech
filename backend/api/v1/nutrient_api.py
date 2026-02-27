from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.fertigation_v2 import FieldMicronutrients, NutrientInjectionLog
from backend.services.nutrient_advisor import NutrientAdvisor
from backend.extensions import db

nutrient_api_bp = Blueprint('nutrient_api', __name__)

@nutrient_api_bp.route('/nutrients/strategy', methods=['POST'])
@token_required
def generate_strategy(current_user):
    """Triggers an autonomous nutrient optimization cycle for a zone."""
    data = request.json
    zone_id = data.get('zone_id')
    
    log = NutrientAdvisor.calculate_injection_strategy(zone_id)
    if not log:
        return jsonify({'error': 'Insufficient soil data or invalid zone'}), 400
        
    return jsonify({
        'status': 'success',
        'data': log.to_dict(),
        'message': 'AI Nutrient strategy deployed'
    }), 201

@nutrient_api_bp.route('/nutrients/micronutrients', methods=['GET'])
@token_required
def get_micronutrients(current_user):
    """Retrieve heavy-metal and micronutrient profiles for a specific farm zone."""
    zone_id = request.args.get('zone_id')
    profile = FieldMicronutrients.query.filter_by(zone_id=zone_id).order_by(FieldMicronutrients.recorded_at.desc()).first()
    
    if not profile:
        return jsonify({'status': 'pending', 'message': 'No profile recorded'}), 200
        
    return jsonify({
        'status': 'success',
        'data': {
            'zinc': profile.zinc,
            'boron': profile.boron,
            'iron': profile.iron,
            'biological_index': profile.microbial_activity_index
        }
    }), 200

@nutrient_api_bp.route('/nutrients/history', methods=['GET'])
@token_required
def get_injection_history(current_user):
    """View historical N-P-K-S injection logs."""
    zone_id = request.args.get('zone_id')
    logs = NutrientInjectionLog.query.filter_by(zone_id=zone_id).order_by(NutrientInjectionLog.recorded_at.desc()).limit(20).all()
    return jsonify({
        'status': 'success',
        'data': [l.to_dict() for l in logs]
    }), 200
