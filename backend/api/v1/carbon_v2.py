from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.carbon_escrow import CarbonTradeEscrow, CarbonCreditWallet
from backend.services.carbon_escrow_service import CarbonEscrowManager
from backend.extensions import db

carbon_v2_bp = Blueprint('carbon_v2', __name__)

@carbon_v2_bp.route('/escrow/listings', methods=['GET'])
@token_required
def get_escrow_listings(current_user):
    """View all available carbon credit listings in the L3 escrow pool."""
    listings = CarbonTradeEscrow.query.filter_by(status='LISTED').all()
    return jsonify({
        'status': 'success',
        'data': [{
            'id': l.id,
            'volume': l.credits_volume,
            'price': l.price_per_credit_usd,
            'seller_id': l.seller_id
        } for l in listings]
    }), 200

@carbon_v2_bp.route('/wallet/balance', methods=['GET'])
@token_required
def get_carbon_balance(current_user):
    """Get the tokenized carbon credit balance for the logarithmic vault."""
    wallet = CarbonCreditWallet.query.filter_by(user_id=current_user.id).first()
    if not wallet:
        return jsonify({'balance': 0.0, 'frozen': 0.0}), 200
        
    return jsonify({
        'status': 'success',
        'data': {
            'total_minted': wallet.total_credits_minted,
            'available': wallet.available_credits_for_sale,
            'frozen': wallet.frozen_credits_in_escrow
        }
    }), 200

@carbon_v2_bp.route('/escrow/fund', methods=['POST'])
@token_required
def fund_carbon_trade(current_user):
    """Commit buyer funds to the carbon trade escrow account."""
    data = request.json
    escrow_id = data.get('escrow_id')
    
    try:
        escrow = CarbonEscrowManager.fund_escrow(escrow_id, current_user.id)
        return jsonify({
            'status': 'success',
            'message': 'Escrow funded and credits frozen',
            'escrow_id': escrow.id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
