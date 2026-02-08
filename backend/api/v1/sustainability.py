from flask import Blueprint, request, jsonify
from backend.services.carbon_service import CarbonService
from backend.services.audit_workflow import AuditWorkflow
from backend.models.sustainability import CarbonPractice
from auth_utils import token_required
import logging

sustainability_bp = Blueprint('sustainability', __name__)

@sustainability_bp.route('/practices', methods=['POST'])
@token_required
def log_practice(current_user):
    data = request.get_json()
    if not data or 'practice_type' not in data or 'area' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
    practice, error = CarbonService.log_practice(
        user_id=current_user.id,
        farm_id=data.get('farm_id'),
        practice_type=data['practice_type'],
        area=data['area'],
        start_date=data.get('start_date'),
        description=data.get('description')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': practice.to_dict()
    }), 201

@sustainability_bp.route('/impact', methods=['GET'])
@token_required
def get_impact(current_user):
    impact = CarbonService.get_user_impact(current_user.id)
    return jsonify({
        'status': 'success',
        'data': impact
    }), 200

@sustainability_bp.route('/audit/<int:practice_id>', methods=['POST'])
@token_required
def request_audit(current_user, practice_id):
    # Verify ownership
    practice = CarbonPractice.query.get_or_404(practice_id)
    if practice.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    audit, error = AuditWorkflow.initiate_audit(practice_id)
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'message': 'Audit request submitted'
    }), 200
