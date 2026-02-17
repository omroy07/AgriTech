from flask import Blueprint, request, jsonify
from backend.services.insurance_service import InsuranceService
from backend.models.insurance_v2 import CropPolicy, ClaimRequest
from auth_utils import token_required
from datetime import datetime

insurance_v2_bp = Blueprint('insurance_v2', __name__)

@insurance_v2_bp.route('/policies', methods=['POST'])
@token_required
def create_policy(current_user):
    data = request.get_json()
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    policy, error = InsuranceService.issue_policy(
        user_id=current_user.id,
        farm_id=data['farm_id'],
        crop_type=data['crop_type'],
        coverage=float(data['coverage']),
        start_date=start_date,
        end_date=end_date
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': policy.to_dict()
    }), 201

@insurance_v2_bp.route('/my-policies', methods=['GET'])
@token_required
def list_policies(current_user):
    policies = CropPolicy.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'status': 'success',
        'data': [p.to_dict() for p in policies]
    }), 200

@insurance_v2_bp.route('/claims', methods=['POST'])
@token_required
def submit_claim(current_user):
    data = request.get_json()
    claim, error = InsuranceService.file_claim(
        policy_id=data['policy_id'],
        loss_kg=float(data['loss_kg']),
        reason=data['reason']
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'data': {'claim_id': claim.id, 'suggested_payout': claim.claim_amount}
    }), 201

@insurance_v2_bp.route('/claims/<int:claim_id>/process', methods=['PATCH'])
@token_required
def adjudicate_claim(current_user, claim_id):
    # In real app, check for ADJUSTER role
    data = request.get_json()
    success, error = InsuranceService.process_claim(
        claim_id=claim_id,
        adjuster_id=current_user.id,
        decision=data['decision'], # 'approve' or 'reject'
        notes=data['notes'],
        verification_score=data.get('verification_score', 0.8)
    )
    
    if not success:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({'status': 'success'}), 200
