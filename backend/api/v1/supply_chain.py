from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.autonomous_supply import SmartContractOrder
from backend.services.sc_orchestrator import SupplyChainOrchestrator
from backend.extensions import db

supply_chain_bp = Blueprint('supply_chain', __name__)

@supply_chain_bp.route('/contract/init', methods=['POST'])
@token_required
def init_smart_contract(current_user):
    """Initializes an autonomous supply chain order."""
    data = request.json
    try:
        order = SupplyChainOrchestrator.initialize_contract(
            buyer_id=current_user.id,
            vendor_id=data.get('vendor_id'),
            commodity_info=data.get('commodity')
        )
        return jsonify({
            'status': 'success',
            'order_id': order.id,
            'message': 'Smart contract order initialized'
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@supply_chain_bp.route('/contract/<int:order_id>/telemetry', methods=['POST'])
@token_required
def update_order_telemetry(current_user, order_id):
    """Updates GPS telemetry and checks geofence for order completion."""
    data = request.json
    lat = data.get('lat')
    lng = data.get('lng')
    
    triggered = SupplyChainOrchestrator.update_gps_telemetry(order_id, lat, lng)
    
    return jsonify({
        'status': 'success',
        'geofence_triggered': triggered,
        'message': 'Telemetry processed'
    }), 200

@supply_chain_bp.route('/orders/active', methods=['GET'])
@token_required
def get_active_orders(current_user):
    """Retrieves active smart contract orders."""
    orders = SmartContractOrder.query.filter(SmartContractOrder.status != 'COMPLETED').all()
    return jsonify({
        'status': 'success',
        'data': [{
            'id': o.id,
            'commodity': o.commodity,
            'status': o.status,
            'quantity': o.quantity_kg
        } for o in orders]
    }), 200
