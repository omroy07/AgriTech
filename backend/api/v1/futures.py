from flask import Blueprint, jsonify, request
from backend.services.velocity_engine import VelocityEngine
from backend.models.market import ForwardContract, PriceHedgingLog
from backend.models.farm import Farm
from backend.auth_utils import token_required
from backend.extensions import db
from datetime import datetime, timedelta

futures_bp = Blueprint('futures', __name__)

@futures_bp.route('/liquidity/<int:farm_id>', methods=['GET'])
@token_required
def get_yield_liquidity(current_user, farm_id):
    """
    Returns the predicted yield, readiness, and current hedge ratio.
    """
    farm = Farm.query.get(farm_id)
    if not farm:
        return jsonify({'error': 'Farm not found'}), 404
        
    # Trigger fresh calculations
    VelocityEngine.calculate_harvest_readiness(farm_id)
    VelocityEngine.predict_yield_volume(farm_id)
    hedge_ratio = VelocityEngine.calculate_hedge_ratio(farm_id)
    
    return jsonify({
        'status': 'success',
        'data': {
            'predicted_yield_kg': farm.predicted_yield_volume,
            'harvest_readiness': farm.harvest_readiness_index,
            'recommended_hedge_ratio': hedge_ratio,
            'market_status': 'VOLATILE' if hedge_ratio > 0.6 else 'STABLE'
        }
    })

@futures_bp.route('/contract/lock', methods=['POST'])
@token_required
def lock_forward_contract(current_user):
    """
    Manually lock a portion of upcoming harvest into a forward contract.
    """
    data = request.get_json()
    farm_id = data.get('farm_id')
    quantity = data.get('quantity')
    target_price = data.get('price')
    
    # Calculate recommended hedge ratio (L3 logic)
    hedge_ratio = VelocityEngine.calculate_hedge_ratio(farm_id)
    
    contract = ForwardContract(
        farm_id=farm_id,
        crop_type="Grains", # Generic for example
        estimated_quantity=quantity,
        locked_price_per_unit=target_price,
        maturity_date=datetime.utcnow() + timedelta(days=45),
        status='SIGNED',
        hedge_ratio=hedge_ratio
    )
    
    db.session.add(contract)
    
    # Log the hedging action
    log = PriceHedgingLog(
        farm_id=farm_id,
        action="MANUAL_CONTRACT_LOCK",
        new_hedge_ratio=hedge_ratio,
        trigger_reason="User manual intervention"
    )
    db.session.add(log)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'contract_id': contract.id,
        'hedged_at': hedge_ratio
    })

@futures_bp.route('/hedging-history/<int:farm_id>', methods=['GET'])
@token_required
def get_hedging_history(current_user, farm_id):
    """Returns historical hedge ratio adjustments."""
    logs = PriceHedgingLog.query.filter_by(farm_id=farm_id).order_by(PriceHedgingLog.timestamp.desc()).all()
    return jsonify({
        'status': 'success',
        'logs': [
            {
                'action': l.action,
                'ratio': l.new_hedge_ratio,
                'reason': l.trigger_reason,
                'timestamp': l.timestamp.isoformat()
            } for l in logs
        ]
    })

@futures_bp.route('/yield-at-risk/<int:farm_id>', methods=['GET'])
@token_required
def get_yield_at_risk(current_user, farm_id):
    """
    Returns real-time climate risk exposure (YaR) for a farm.
    """
    from backend.services.yield_resilience_service import YieldResilienceEngine
    risk_profile = YieldResilienceEngine.compute_yield_at_risk(farm_id)
    return jsonify({
        'status': 'success',
        'data': risk_profile
    }), 200

@futures_bp.route('/contract/<int:contract_id>/climate-status', methods=['GET'])
@token_required
def get_contract_climate_status(current_user, contract_id):
    """Shows if a specific contract is suspended due to Force Majeure."""
    contract = ForwardContract.query.get(contract_id)
    if not contract:
        return jsonify({'error': 'Contract not found'}), 404
    
    return jsonify({
        'status': 'success',
        'data': {
            'contract_id': contract.id,
            'force_majeure_suspended': contract.force_majeure_suspended,
            'climate_risk_discount_pct': contract.climate_risk_discount,
            'yield_at_risk_pct': contract.yield_at_risk_pct
        }
    }), 200
