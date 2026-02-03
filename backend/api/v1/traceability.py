from flask import Blueprint, request, jsonify, current_app
from backend.services.traceability_service import TraceabilityService
from backend.tasks.traceability_tasks import generate_batch_certificate_task
from auth_utils import token_required, roles_required
import logging

logger = logging.getLogger(__name__)
traceability_bp = Blueprint('traceability', __name__)

@traceability_bp.route('/batches', methods=['POST'])
@token_required
@roles_required(['farmer', 'admin'])
def create_batch(current_user):
    """Create a new produce batch"""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    required = ['crop_name', 'quantity', 'farm_location']
    if not all(k in data for k in required):
        return jsonify({'status': 'error', 'message': f'Missing required fields: {required}'}), 400
    
    batch, error = TraceabilityService.create_batch(
        farmer_id=current_user.id,
        crop_name=data['crop_name'],
        quantity=data['quantity'],
        farm_location=data['farm_location'],
        crop_variety=data.get('crop_variety'),
        unit=data.get('unit', 'KG')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
    
    return jsonify({
        'status': 'success',
        'data': batch.to_dict(),
        'message': 'Batch created successfully'
    }), 201

@traceability_bp.route('/batches/<batch_id>', methods=['GET'])
def get_batch(batch_id):
    """Public endpoint to fetch batch history for traceability scanning"""
    batch_data, error = TraceabilityService.get_batch_history(batch_id)
    if error:
        return jsonify({'status': 'error', 'message': error}), 404
    
    return jsonify({
        'status': 'success',
        'data': batch_data
    }), 200

@traceability_bp.route('/batches/<batch_id>/quality', methods=['POST'])
@token_required
@roles_required(['consultant', 'admin'])
def add_quality_check(current_user, batch_id):
    """Add quality inspection to a batch"""
    data = request.get_json()
    if not data or 'grade' not in data or 'parameters' not in data:
        return jsonify({'status': 'error', 'message': 'Missing grade or parameters'}), 400
    
    batch, error = TraceabilityService.add_quality_check(
        batch_id=batch_id,
        inspector_id=current_user.id,
        grade=data['grade'],
        parameters=data['parameters'],
        notes=data.get('notes')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
    
    # Trigger certificate generation if status moved to QUALITY_CHECK
    if batch.status == 'QUALITY_CHECK':
        generate_batch_certificate_task.delay(batch.batch_internal_id, user_id=batch.farmer_id)
    
    return jsonify({
        'status': 'success',
        'data': batch.to_dict(),
        'message': 'Quality check recorded'
    }), 200

@traceability_bp.route('/batches/<batch_id>/transfer', methods=['POST'])
@token_required
def transfer_custody(current_user, batch_id):
    """Transfer batch custody to another handler"""
    data = request.get_json()
    required = ['new_handler_id', 'new_status', 'location']
    if not all(k in data for k in required):
        return jsonify({'status': 'error', 'message': f'Missing fields: {required}'}), 400
    
    batch, error = TraceabilityService.transfer_custody(
        batch_id=batch_id,
        current_handler_id=current_user.id,
        new_handler_id=data['new_handler_id'],
        new_status=data['new_status'],
        location=data['location'],
        notes=data.get('notes')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
    
    # Real-time update via socket would be triggered here in a production app
    # (e.g., call broadcast_batch_update)
    from backend.sockets.supply_events import broadcast_batch_update
    broadcast_batch_update(batch_id, {
        'status': batch.status,
        'handler_id': batch.current_handler_id,
        'timestamp': batch.updated_at.isoformat()
    })
    
    return jsonify({
        'status': 'success',
        'data': batch.to_dict(),
        'message': 'Custody transferred successfully'
    }), 200

@traceability_bp.route('/batches/<batch_id>/certificate', methods=['POST'])
@token_required
def request_certificate(current_user, batch_id):
    """Manually trigger certificate generation task"""
    # Verify ownership or admin
    batch_data, error = TraceabilityService.get_batch_history(batch_id)
    if error:
        return jsonify({'status': 'error', 'message': error}), 404
        
    if batch_data['farmer_id'] != current_user.id and current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403
        
    generate_batch_certificate_task.delay(batch_id, user_id=current_user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'Certificate generation queued'
    }), 202
