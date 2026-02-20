from flask import Blueprint, jsonify, request
from backend.services.barter_service import BarterService, ValueOrchestrator
from backend.auth_utils import token_required
from backend.extensions import db
from backend.models.barter import BarterTransaction

barter_bp = Blueprint('barter', __name__)

@barter_bp.route('/quote', methods=['POST'])
@token_required
def get_quote(current_user):
    """Calculates the Value-Index for a potential resource swap."""
    data = request.get_json()
    category = data.get('category')
    ref_id = data.get('id')
    qty = data.get('qty', 1.0)
    
    val, details = ValueOrchestrator.get_resource_value(category, ref_id, qty)
    return jsonify({
        'status': 'success',
        'value_index': val,
        'breakdown': details
    })

@barter_bp.route('/propose', methods=['POST'])
@token_required
def propose_trade(current_user):
    """Initiates a new barter transaction proposal."""
    data = request.get_json()
    responder_id = data.get('responder_id')
    offered = data.get('offered', []) # List of {category, id, qty}
    requested = data.get('requested', [])
    
    if not responder_id or not offered or not requested:
        return jsonify({'status': 'error', 'message': 'Missing trade parameters'}), 400
        
    tx = BarterService.propose_barter(current_user.id, responder_id, offered, requested)
    return jsonify({
        'status': 'success',
        'transaction': tx.to_dict()
    }), 201

@barter_bp.route('/<int:tx_id>/commit', methods=['POST'])
@token_required
def lock_side(current_user, tx_id):
    """One party locks their commitment in escrow."""
    tx = BarterService.lock_escrow(tx_id, current_user.id)
    if not tx:
        return jsonify({'status': 'error', 'message': 'Transaction not found'}), 404
    return jsonify({
        'status': 'success',
        'transaction': tx.to_dict()
    })

@barter_bp.route('/<int:tx_id>/confirm-fulfillment', methods=['POST'])
@token_required
def confirm_delivery(current_user, tx_id):
    """Confirms physical exchange or service completion."""
    tx = BarterService.confirm_fulfillment(tx_id, current_user.id)
    return jsonify({
        'status': 'success',
        'transaction': tx.to_dict()
    })

@barter_bp.route('/history', methods=['GET'])
@token_required
def list_barters(current_user):
    """Lists all barter transactions for the current user."""
    txs = BarterTransaction.query.filter(
        (BarterTransaction.initiator_id == current_user.id) | 
        (BarterTransaction.responder_id == current_user.id)
    ).order_by(BarterTransaction.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'transactions': [t.to_dict() for t in txs]
    })
