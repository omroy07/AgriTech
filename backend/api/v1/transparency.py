from flask import Blueprint, jsonify, request
from backend.services.transparency_service import TransparencyService
from backend.models.warehouse import StockItem
from backend.auth_utils import token_required
from backend.extensions import db

transparency_bp = Blueprint('transparency', __name__)

@transparency_bp.route('/trace/<int:stock_item_id>', methods=['GET'])
def get_traceability(stock_item_id):
    """Publicly accessible traceability data for consumers."""
    genealogy = TransparencyService.get_seed_to_shelf_genealogy(stock_item_id)
    if not genealogy:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404
    return jsonify({
        'status': 'success',
        'data': genealogy
    })

@transparency_bp.route('/review', methods=['POST'])
@token_required
def submit_review(current_user):
    """Consumers submit quality feedback which impacts farmer reputation."""
    data = request.get_json()
    if not data or 'stock_item_id' not in data or 'rating' not in data:
        return jsonify({'status': 'error', 'message': 'Missing review data'}), 400
        
    review = TransparencyService.process_consumer_feedback(
        user_id=current_user.id,
        stock_item_id=data['stock_item_id'],
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    
    if not review:
        return jsonify({'status': 'error', 'message': 'Review failed'}), 500
        
    return jsonify({
        'status': 'success',
        'data': review.to_dict()
    }), 201

@transparency_bp.route('/pricing/audit/<int:stock_item_id>', methods=['GET'])
@token_required
def get_pricing_history(current_user, stock_item_id):
    """Audit trail for freshness-based price changes."""
    from backend.models.transparency import PriceAdjustmentLog
    logs = PriceAdjustmentLog.query.filter_by(stock_item_id=stock_item_id).order_by(PriceAdjustmentLog.timestamp.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [l.to_dict() for l in logs]
    })
