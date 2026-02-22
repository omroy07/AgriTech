from flask import Blueprint, request, jsonify
from backend.services.processing_service import ProcessingService
from backend.models.processing import ProcessingBatch, ProcessingStage
from auth_utils import token_required
import logging

processing_bp = Blueprint('processing', __name__)

@processing_bp.route('/batches', methods=['GET'])
@token_required
def list_batches(current_user):
    """Retrieve all active industrial processing batches"""
    batches = ProcessingBatch.query.order_by(ProcessingBatch.created_at.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [b.to_dict() for b in batches]
    }), 200

@processing_bp.route('/batches', methods=['POST'])
@token_required
def create_batch(current_user):
    """Initiate a new raw material batch for processing"""
    data = request.get_json()
    if not data or 'product_type' not in data or 'weight' not in data:
        return jsonify({'status': 'error', 'message': 'Missing product_type or weight'}), 400
        
    batch, error = ProcessingService.create_batch(
        product_type=data['product_type'],
        weight=data['weight'],
        origin_farms=data.get('origin_farms', '[]')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': batch.to_dict()
    }), 201

@processing_bp.route('/batches/<int:batch_id>/audit', methods=['POST'])
@token_required
def submit_audit(current_user, batch_id):
    """Perform a quality audit at the current stage"""
    data = request.get_json()
    audit, error = ProcessingService.perform_audit(
        batch_id=batch_id,
        auditor_id=current_user.id,
        moisture=data.get('moisture'),
        purity=data.get('purity'),
        weight=data.get('weight')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': audit.to_dict()
    }), 201

@processing_bp.route('/batches/<int:batch_id>/advance', methods=['PATCH'])
@token_required
def advance_batch(current_user, batch_id):
    """Transition batch to next stage if QA passed"""
    data = request.get_json()
    next_stage = data.get('next_stage')
    
    success, error = ProcessingService.advance_stage(
        batch_id=batch_id,
        operator_id=current_user.id,
        next_stage=next_stage
    )
    
    if not success:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({'status': 'success', 'message': f'Batch moved to {next_stage}'}), 200

@processing_bp.route('/batches/<int:batch_id>/genealogy', methods=['GET'])
@token_required
def get_genealogy(current_user, batch_id):
    """Trace all lifecycle events and audits for a batch"""
    history = ProcessingService.get_batch_genealogy(batch_id)
    if not history:
        return jsonify({'status': 'error', 'message': 'Batch not found'}), 404
        
    return jsonify({
        'status': 'success',
        'data': history
    }), 200

@processing_bp.route('/batches/<int:batch_id>/spectral-scan', methods=['POST'])
@token_required
def submit_spectral_scan(current_user, batch_id):
    """
    Ingest raw chemical scan data and trigger autonomous financial updates.
    """
    from backend.services.grading_engine import GradingEngine
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No scan data provided'}), 400
        
    grade, penalty = GradingEngine.process_spectral_scan(batch_id, data)
    
    return jsonify({
        'status': 'success',
        'data': {
            'final_grade': grade,
            'pricing_penalty': penalty,
            'cascading_status': 'COMPLETED'
        }
    }), 201

@processing_bp.route('/batches/<int:batch_id>/valuation', methods=['GET'])
@token_required
def get_batch_valuation(current_user, batch_id):
    """
    Fetch the current real-time valuation of a batch after quality adjustments.
    """
    from backend.models.procurement import BulkOrder
    # Simplified: Get the latest order for the supply batch linked to this processing batch
    # In reality, this would involve complex relationship traversals
    batch = ProcessingBatch.query.get(batch_id)
    if not batch:
        return jsonify({'status': 'error', 'message': 'Batch not found'}), 404
        
    # Mocking valuation response for demonstration of API structure
    return jsonify({
        'status': 'success',
        'data': {
            'batch_id': batch_id,
            'market_valuation': 12500.00, # Simulated
            'quality_modifier': 0.85, # 15% penalty applied
            'currency': 'USD'
        }
    }), 200
