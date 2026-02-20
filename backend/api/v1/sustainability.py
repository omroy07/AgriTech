from flask import Blueprint, jsonify, request
from backend.services.carbon_calculator import CarbonCalculator
from backend.models.sustainability import CarbonLedger, SustainabilityScore
from backend.auth_utils import token_required
from backend.extensions import db

sustainability_bp = Blueprint('sustainability', __name__)

@sustainability_bp.route('/report/farm/<int:farm_id>', methods=['GET'])
@token_required
def get_farm_sustainability_report(current_user, farm_id):
    """
    Returns detailed carbon breakdown and rating for a farm.
    """
    ledger = CarbonLedger.query.filter_by(farm_id=farm_id).order_by(CarbonLedger.recorded_at.desc()).first()
    score = SustainabilityScore.query.filter_by(farm_id=farm_id).first()
    
    if not ledger:
        return jsonify({'status': 'pending', 'message': 'No audit records found'}), 200
        
    return jsonify({
        'status': 'success',
        'data': {
            'carbon_footprint': ledger.to_dict(),
            'rating': score.overall_rating if score else None,
            'credits_available': score.offset_credits_available if score else 0.0
        }
    })

@sustainability_bp.route('/report/batch/<int:batch_id>', methods=['GET'])
@token_required
def get_batch_certification(current_user, batch_id):
    """
    Returns a 'Net-Zero' certification hash for a specific supply batch.
    """
    ledger = CarbonLedger.query.filter_by(batch_id=batch_id).first()
    if not ledger:
        return jsonify({'error': 'Certification not yet calculated'}), 404
        
    return jsonify({
        'status': 'success',
        'certification_id': f"NZ-{ledger.id:06d}",
        'net_carbon': ledger.net_carbon_balance,
        'is_net_zero': ledger.certification_status == 'NET_ZERO'
    })

@sustainability_bp.route('/audit', methods=['POST'])
@token_required
def trigger_manual_audit(current_user):
    """Manually triggers a fresh carbon audit for the user's farm."""
    data = request.get_json()
    farm_id = data.get('farm_id')
    
    ledger = CarbonCalculator.run_full_audit(farm_id)
    return jsonify({
        'status': 'success',
        'footprint': ledger.total_footprint,
        'certification': ledger.certification_status
    })
