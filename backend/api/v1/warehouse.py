from flask import Blueprint, request, jsonify
from backend.services.inventory_service import InventoryService
from backend.models.warehouse import StockItem, StockMovement, WarehouseLocation
from auth_utils import token_required

warehouse_bp = Blueprint('warehouse', __name__)

@warehouse_bp.route('/stock', methods=['GET'])
@token_required
def list_stock(current_user):
    """Lists all stock items in a warehouse."""
    warehouse_id = request.args.get('warehouse_id', type=int)
    if not warehouse_id:
        return jsonify({'status': 'error', 'message': 'Warehouse ID required'}), 400
    
    items = StockItem.query.filter_by(warehouse_id=warehouse_id).all()
    return jsonify({
        'status': 'success',
        'data': [i.to_dict() for i in items]
    }), 200

@warehouse_bp.route('/stock/in', methods='POST'])
@token_required
def stock_in(current_user):
    """Records incoming stock."""
    data = request.get_json()
    movement, error = InventoryService.record_stock_in(
        stock_item_id=data['stock_item_id'],
        quantity=float(data['quantity']),
        reference_doc=data.get('reference'),
        user_id=current_user.id
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
    
    return jsonify({'status': 'success', 'message': 'Stock received'}), 201

@warehouse_bp.route('/stock/out', methods=['POST'])
@token_required
def stock_out(current_user):
    """Records outgoing stock."""
    data = request.get_json()
    movement, error = InventoryService.record_stock_out(
        stock_item_id=data['stock_item_id'],
        quantity=float(data['quantity']),
        reference_doc=data.get('reference'),
        user_id=current_user.id
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
    
    return jsonify({'status': 'success', 'message': 'Stock issued'}), 201

@warehouse_bp.route('/reconcile', methods=['POST'])
@token_required
def reconcile(current_user):
    """Performs stock reconciliation audit."""
    data = request.get_json()
    log, error = InventoryService.perform_reconciliation(
        warehouse_id=data['warehouse_id'],
        user_id=current_user.id,
        physical_counts=data['physical_counts']
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
    
    return jsonify({
        'status': 'success',
        'data': {
            'discrepancies': log.discrepancies_found,
            'shrinkage': log.shrinkage_value
        }
    }), 201

@warehouse_bp.route('/expiring', methods=['GET'])
@token_required
def get_expiring(current_user):
    """Returns stock items nearing expiry."""
    warehouse_id = request.args.get('warehouse_id', type=int)
    days = request.args.get('days', 30, type=int)
    
    expiring = InventoryService.get_expiring_stock(warehouse_id, days)
    return jsonify({
        'status': 'success',
        'data': expiring
    }), 200
