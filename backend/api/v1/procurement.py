from flask import Blueprint, request, jsonify
from backend.services.procurement_service import ProcurementService
from backend.models.procurement import ProcurementItem, BulkOrder
from auth_utils import token_required

procurement_bp = Blueprint('procurement', __name__)

@procurement_bp.route('/items', methods=['GET'])
def list_items():
    category = request.args.get('category')
    query = ProcurementItem.query
    if category:
        query = query.filter_by(category=category)
    
    items = query.all()
    return jsonify({
        'status': 'success',
        'data': [
            {
                'id': i.id,
                'name': i.name,
                'category': i.category,
                'base_price': i.base_price,
                'vendor_name': i.vendor.company_name
            } for i in items
        ]
    }), 200

@procurement_bp.route('/orders', methods=['POST'])
@token_required
def place_order(current_user):
    data = request.get_json()
    if not data or 'item_id' not in data or 'quantity' not in data:
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400
        
    order, error = ProcurementService.create_order(
        buyer_id=current_user.id,
        item_id=data['item_id'],
        quantity=data['quantity'],
        address=data.get('address', 'Primary Farm Location')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': {'order_id': order.id, 'total_amount': order.total_amount}
    }), 201

@procurement_bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    order = BulkOrder.query.get_or_404(order_id)
    if order.buyer_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    history = ProcurementService.get_order_history(order_id)
    return jsonify({
        'status': 'success',
        'data': {
            'id': order.id,
            'status': order.status,
            'history': [{'to': h.to_status, 'at': h.timestamp.isoformat()} for h in history]
        }
    }), 200
