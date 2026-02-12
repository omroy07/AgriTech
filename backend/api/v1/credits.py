from flask import Blueprint, request, jsonify
from backend.services.carbon_service import CarbonService
from backend.models.sustainability import CreditLedger
from auth_utils import token_required

credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/my-ledger', methods=['GET'])
@token_required
def get_ledger(current_user):
    credits = CreditLedger.query.filter_by(owner_id=current_user.id).all()
    return jsonify({
        'status': 'success',
        'data': [c.to_dict() for c in credits]
    }), 200

@credits_bp.route('/issue/<int:practice_id>', methods=['POST'])
@token_required
def issue_credits(current_user, practice_id):
    # Only allow owner to trigger issuance
    from backend.models.sustainability import CarbonPractice
    practice = CarbonPractice.query.get_or_404(practice_id)
    if practice.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    # Recalculate offsets before issuance to ensure latest data
    CarbonService.calculate_and_update_offsets(practice_id)
    
    credit, error = CarbonService.issue_credits(practice_id)
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'data': credit.to_dict()
    }), 201

@credits_bp.route('/marketplace', methods=['GET'])
def list_available_credits():
    """List credits available for purchase by corporations/other users"""
    credits = CreditLedger.query.filter_by(status='Active').limit(50).all()
    return jsonify({
        'status': 'success',
        'data': [c.to_dict() for c in credits]
    }), 200
