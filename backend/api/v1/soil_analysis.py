from flask import Blueprint, request, jsonify
from backend.services.soil_service import SoilService
from backend.models.soil_health import SoilTest, FertilizerRecommendation
from auth_utils import token_required

soil_bp = Blueprint('soil_analysis', __name__)

@soil_bp.route('/test', methods=['POST'])
@token_required
def submit_test(current_user):
    data = request.get_json()
    farm_id = data.get('farm_id')
    if not farm_id:
        return jsonify({'status': 'error', 'message': 'Farm ID is required'}), 400
        
    test, error = SoilService.log_soil_test(farm_id, data)
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success', 
        'data': test.to_dict()
    }), 201

@soil_bp.route('/history/<int:farm_id>', methods=['GET'])
@token_required
def get_history(current_user, farm_id):
    history = SoilService.get_farm_soil_history(farm_id)
    return jsonify({
        'status': 'success',
        'data': [t.to_dict() for t in history]
    }), 200

@soil_bp.route('/recommendations/<int:test_id>', methods=['GET'])
@token_required
def get_recommendations(current_user, test_id):
    recs = FertilizerRecommendation.query.filter_by(soil_test_id=test_id).all()
    return jsonify({
        'status': 'success',
        'data': [r.to_dict() for r in recs]
    }), 200

@soil_bp.route('/apply', methods=['POST'])
@token_required
def log_application(current_user):
    data = request.get_json()
    log = SoilService.log_application(data['test_id'], current_user.id, data)
    return jsonify({
        'status': 'success',
        'message': 'Application logged successfully'
    }), 201
