from flask import Blueprint, request, jsonify
from backend.models.weather import CropAdvisory
from backend.services.advisory_engine import AdvisoryEngine
from backend.extensions import db
from auth_utils import token_required

advisories_bp = Blueprint('advisories', __name__)

@advisories_bp.route('/', methods=['GET'])
@token_required
def get_advisories(current_user):
    advisories = CropAdvisory.query.filter_by(user_id=current_user.id)\
        .order_by(CropAdvisory.created_at.desc()).limit(20).all()
        
    return jsonify({
        'status': 'success',
        'data': [a.to_dict() for a in advisories]
    }), 200

@advisories_bp.route('/generate', methods=['POST'])
@token_required
def manual_generate(current_user):
    data = request.get_json()
    if not data or 'crop_name' not in data or 'location' not in data:
        return jsonify({'status': 'error', 'message': 'Crop and location required'}), 400
        
    advisory = AdvisoryEngine.generate_advisory(
        user_id=current_user.id,
        crop_name=data['crop_name'],
        location=data['location'],
        soil_type=data.get('soil_type'),
        growth_stage=data.get('growth_stage')
    )
    
    if not advisory:
        return jsonify({'status': 'error', 'message': 'IA Engine busy or error'}), 500
        
    return jsonify({
        'status': 'success',
        'data': advisory.to_dict()
    }), 201

@advisories_bp.route('/<int:advisory_id>/read', methods=['PATCH'])
@token_required
def mark_read(current_user, advisory_id):
    advisory = CropAdvisory.query.get_or_404(advisory_id)
    if advisory.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    advisory.is_read = True
    db.session.commit()
    return jsonify({'status': 'success'}), 200

@advisories_bp.route('/<int:advisory_id>/feedback', methods=['POST'])
@token_required
def submit_feedback(current_user, advisory_id):
    data = request.get_json()
    rating = data.get('rating')
    
    if not rating or not (1 <= rating <= 5):
        return jsonify({'status': 'error', 'message': 'Invalid rating'}), 400
        
    advisory = CropAdvisory.query.get_or_404(advisory_id)
    if advisory.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    advisory.feedback_rating = rating
    db.session.commit()
    return jsonify({'status': 'success'}), 200
