from flask import Blueprint, jsonify, request
# L3-1560: Predictive Harvest Velocity & Autonomous Futures Hedging
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
