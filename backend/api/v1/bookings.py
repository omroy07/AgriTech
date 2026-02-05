from flask import Blueprint, request, jsonify
from backend.services.rental_service import RentalService
from auth_utils import token_required
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/', methods=['POST'])
@token_required
def create_booking(current_user):
    """Create a new equipment rental booking"""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
    try:
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
        equipment_id = data['equipment_id']
        
        booking, error = RentalService.create_booking(
            equipment_id, current_user.id, start_time, end_time
        )
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 400
            
        return jsonify({
            'status': 'success',
            'data': booking.to_dict()
        }), 210
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bookings_bp.route('/<int:booking_id>/status', methods=['PATCH'])
@token_required
def update_booking_status(current_user, booking_id):
    """Update booking status (e.g., PAYMENT, PICKED_UP, COMPLETED)"""
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'status': 'error', 'message': 'No status provided'}), 400
        
    booking, error = RentalService.update_booking_status(booking_id, new_status, current_user.id)
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    # Real-time notification would happen here
    from backend.sockets.rental_events import broadcast_booking_update
    broadcast_booking_update(booking, current_user.id)
    
    return jsonify({
        'status': 'success',
        'data': booking.to_dict()
    }), 200

@bookings_bp.route('/my-bookings', methods=['GET'])
@token_required
def get_my_bookings(current_user):
    """Get all bookings for the current user (renter or owner)"""
    from backend.models.equipment import RentalBooking, Equipment
    
    is_owner = request.args.get('as_owner') == 'true'
    
    if is_owner:
        bookings = RentalBooking.query.join(Equipment).filter(Equipment.owner_id == current_user.id).all()
    else:
        bookings = RentalBooking.query.filter_by(renter_id=current_user.id).all()
        
    return jsonify({
        'status': 'success',
        'data': [b.to_dict() for b in bookings]
    }), 200
