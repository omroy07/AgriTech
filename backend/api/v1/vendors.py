from flask import Blueprint, request, jsonify
from backend.services.procurement_service import ProcurementService
from backend.models.procurement import BulkOrder, VendorProfile, OrderStatus
from auth_utils import token_required
from backend.extensions import db

vendors_bp = Blueprint('vendors', __name__)

@vendors_bp.route('/orders', methods=['GET'])
@token_required
def get_vendor_orders(current_user):
    vendor = VendorProfile.query.filter_by(user_id=current_user.id).first()
    if not vendor:
        return jsonify({'status': 'error', 'message': 'Not a registered vendor'}), 404
        
    orders = BulkOrder.query.filter_by(vendor_id=vendor.id).all()
    return jsonify({
        'status': 'success',
        'data': [{'id': o.id, 'buyer_id': o.buyer_id, 'status': o.status} for o in orders]
    }), 200

@vendors_bp.route('/orders/<int:order_id>/update', methods=['PATCH'])
@token_required
def update_order_status(current_user, order_id):
    data = request.get_json()
    new_status = data.get('status')
    comment = data.get('comment')
    
    vendor = VendorProfile.query.filter_by(user_id=current_user.id).first()
    order = BulkOrder.query.get_or_404(order_id)
    
    if order.vendor_id != vendor.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
    success, error = ProcurementService.transition_order(order_id, new_status, comment)
    if not success:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({'status': 'success'}), 200

@vendors_bp.route('/profile', methods=['POST'])
@token_required
def setup_vendor(current_user):
    data = request.get_json()
    vendor = VendorProfile(
        user_id=current_user.id,
        company_name=data['company_name'],
        registration_id=data.get('reg_id')
    )
    db.session.add(vendor)
    db.session.commit()
    return jsonify({'status': 'success', 'vendor_id': vendor.id}), 201
