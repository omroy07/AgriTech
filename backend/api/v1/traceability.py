"""
Traceability API Endpoints
Provides REST API for supply chain traceability and QR code verification
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from auth_utils import token_required
from security_utils import roles_required, log_security_event, sanitize_input
from backend.services.batch_service import BatchService
from backend.models import BatchStatus, UserRole
from extensions import limiter

# Create blueprint
traceability_bp = Blueprint('traceability', __name__, url_prefix='/traceability')


# ==================== BATCH CREATION ====================

@traceability_bp.route('/batches', methods=['POST'])
@limiter.limit("20 per hour")
@token_required
@roles_required(UserRole.FARMER, UserRole.ADMIN)
def create_batch():
    """
    Create a new produce batch with QR code.
    
    Required fields:
        - produce_name: Name of the produce
        - produce_type: Type (vegetable, fruit, grain, etc.)
        - quantity_kg: Quantity in kilograms
        - origin_location: Farm/origin location
    
    Optional fields:
        - harvest_date: Date of harvest (ISO format)
        - certification: Certification type (organic, non-GMO, etc.)
        - quality_grade: Initial quality grade (A, B, C)
        - quality_notes: Quality notes
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['produce_name', 'produce_type', 'quantity_kg', 'origin_location']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Sanitize inputs
        produce_name = sanitize_input(data['produce_name'])
        produce_type = sanitize_input(data['produce_type'])
        origin_location = sanitize_input(data['origin_location'])
        
        # Parse quantity
        try:
            quantity_kg = float(data['quantity_kg'])
            if quantity_kg <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid quantity value'
            }), 400
        
        # Parse optional harvest date
        harvest_date = None
        if 'harvest_date' in data and data['harvest_date']:
            try:
                harvest_date = datetime.fromisoformat(data['harvest_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid harvest_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
        
        # Get user ID from token
        user_id = request.user.get('user_id') or request.user.get('id')
        
        # Create batch
        batch, error = BatchService.create_batch(
            user_id=user_id,
            produce_name=produce_name,
            produce_type=produce_type,
            quantity_kg=quantity_kg,
            origin_location=origin_location,
            harvest_date=harvest_date,
            certification=sanitize_input(data.get('certification', '')),
            quality_grade=sanitize_input(data.get('quality_grade', '')),
            quality_notes=sanitize_input(data.get('quality_notes', ''))
        )
        
        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Batch created successfully',
            'data': {
                'batch': batch.to_dict(),
                'qr_verification_url': f'/api/v1/traceability/verify/{batch.batch_id}'
            }
        }), 201
    
    except Exception as e:
        log_security_event('BATCH_CREATE_ERROR', str(e))
        return jsonify({
            'status': 'error',
            'message': f'Error creating batch: {str(e)}'
        }), 500


# ==================== BATCH STATUS TRANSITIONS ====================

@traceability_bp.route('/batches/<batch_id>/status', methods=['PUT'])
@limiter.limit("30 per hour")
@token_required
@roles_required(UserRole.FARMER, UserRole.SHOPKEEPER, UserRole.ADMIN)
def update_batch_status(batch_id):
    """
    Update batch status with role-based enforcement.
    
    Required fields:
        - status: New status (Harvested, Quality_Check, Logistics, In_Shop)
    
    Optional fields:
        - notes: Notes about the transition
        - location: Current location
        - quality_grade: Quality grade (A, B, C)
        - quality_notes: Quality assessment notes
    """
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: status'
            }), 400
        
        new_status = data['status']
        
        # Get user ID from token
        user_id = request.user.get('user_id') or request.user.get('id')
        
        # Perform transition
        success, message = BatchService.transition_batch_status(
            batch_id=batch_id,
            new_status=new_status,
            user_id=user_id,
            notes=sanitize_input(data.get('notes', '')),
            location=sanitize_input(data.get('location', '')),
            quality_grade=sanitize_input(data.get('quality_grade', '')),
            quality_notes=sanitize_input(data.get('quality_notes', ''))
        )
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
        # Get updated batch
        batch = BatchService.get_batch_by_id(batch_id)
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'batch': batch.to_dict() if batch else None
            }
        }), 200
    
    except Exception as e:
        log_security_event('BATCH_STATUS_UPDATE_ERROR', str(e))
        return jsonify({
            'status': 'error',
            'message': f'Error updating batch status: {str(e)}'
        }), 500


# ==================== BATCH QUALITY UPDATE ====================

@traceability_bp.route('/batches/<batch_id>/quality', methods=['PUT'])
@limiter.limit("30 per hour")
@token_required
@roles_required(UserRole.FARMER, UserRole.ADMIN)
def update_batch_quality(batch_id):
    """
    Update batch quality information.
    
    Required fields:
        - quality_grade: Quality grade (A, B, C)
        - quality_notes: Quality assessment notes
    """
    try:
        data = request.get_json()
        
        required_fields = ['quality_grade', 'quality_notes']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Get user ID from token
        user_id = request.user.get('user_id') or request.user.get('id')
        
        # Update quality
        success, message = BatchService.update_quality_info(
            batch_id=batch_id,
            quality_grade=sanitize_input(data['quality_grade']),
            quality_notes=sanitize_input(data['quality_notes']),
            user_id=user_id
        )
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
        # Get updated batch
        batch = BatchService.get_batch_by_id(batch_id)
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'batch': batch.to_dict() if batch else None
            }
        }), 200
    
    except Exception as e:
        log_security_event('BATCH_QUALITY_UPDATE_ERROR', str(e))
        return jsonify({
            'status': 'error',
            'message': f'Error updating batch quality: {str(e)}'
        }), 500


# ==================== BATCH RETRIEVAL ====================

@traceability_bp.route('/batches/<batch_id>', methods=['GET'])
@limiter.limit("60 per hour")
@token_required
def get_batch(batch_id):
    """
    Get batch details with audit trail.
    """
    try:
        include_audit = request.args.get('include_audit', 'true').lower() == 'true'
        
        batch = BatchService.get_batch_by_id(batch_id, include_audit=include_audit)
        
        if not batch:
            return jsonify({
                'status': 'error',
                'message': 'Batch not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'batch': batch.to_dict(include_audit=include_audit)
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving batch: {str(e)}'
        }), 500


@traceability_bp.route('/batches', methods=['GET'])
@limiter.limit("60 per hour")
@token_required
def list_batches():
    """
    List batches based on user role and query parameters.
    
    Query parameters:
        - status: Filter by status
        - farmer_id: Filter by farmer (admin only)
        - shopkeeper_id: Filter by shopkeeper (admin only)
    """
    try:
        user_role = request.user.get('role')
        user_id = request.user.get('user_id') or request.user.get('id')
        
        status = request.args.get('status')
        
        if user_role == UserRole.FARMER:
            # Farmers see their own batches
            batches = BatchService.get_batches_by_farmer(user_id, status=status)
        elif user_role == UserRole.SHOPKEEPER:
            # Shopkeepers see batches they've received
            batches = BatchService.get_batches_by_shopkeeper(user_id, status=status)
        elif user_role == UserRole.ADMIN:
            # Admins can filter by farmer or shopkeeper
            farmer_id = request.args.get('farmer_id')
            shopkeeper_id = request.args.get('shopkeeper_id')
            
            if farmer_id:
                batches = BatchService.get_batches_by_farmer(int(farmer_id), status=status)
            elif shopkeeper_id:
                batches = BatchService.get_batches_by_shopkeeper(int(shopkeeper_id), status=status)
            elif status:
                batches = BatchService.get_batches_by_status(status)
            else:
                # Get all batches (limit to recent 100)
                from backend.models import ProduceBatch
                batches = ProduceBatch.query.order_by(ProduceBatch.created_at.desc()).limit(100).all()
        else:
            return jsonify({
                'status': 'error',
                'message': 'Insufficient permissions'
            }), 403
        
        return jsonify({
            'status': 'success',
            'data': {
                'batches': [batch.to_dict() for batch in batches],
                'count': len(batches)
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error listing batches: {str(e)}'
        }), 500


# ==================== PUBLIC QR VERIFICATION ====================

@traceability_bp.route('/verify/<batch_id>', methods=['GET'])
@limiter.limit("100 per hour")
def verify_batch_public(batch_id):
    """
    Public endpoint for QR code verification.
    Returns traceability passport without authentication.
    """
    try:
        passport = BatchService.get_traceability_passport(batch_id)
        
        if not passport:
            return jsonify({
                'status': 'error',
                'message': 'Batch not found or invalid QR code'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'passport': passport
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error verifying batch: {str(e)}'
        }), 500


@traceability_bp.route('/verify-qr', methods=['POST'])
@limiter.limit("100 per hour")
def verify_qr_code():
    """
    Verify encrypted QR code data.
    
    Required fields:
        - qr_data: Encrypted QR code data string
    """
    try:
        data = request.get_json()
        
        if 'qr_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: qr_data'
            }), 400
        
        decoded_data, error = BatchService.verify_qr_code(data['qr_data'])
        
        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        # Get full batch details
        batch_id = decoded_data.get('batch_id')
        passport = BatchService.get_traceability_passport(batch_id)
        
        return jsonify({
            'status': 'success',
            'message': 'QR code verified successfully',
            'data': {
                'qr_data': decoded_data,
                'passport': passport
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error verifying QR code: {str(e)}'
        }), 500


# ==================== STATISTICS ====================

@traceability_bp.route('/stats', methods=['GET'])
@limiter.limit("30 per hour")
@token_required
def get_statistics():
    """
    Get traceability statistics for the authenticated user.
    """
    try:
        from backend.models import ProduceBatch
        from sqlalchemy import func
        
        user_role = request.user.get('role')
        user_id = request.user.get('user_id') or request.user.get('id')
        
        stats = {}
        
        if user_role == UserRole.FARMER:
            # Farmer statistics
            batches = ProduceBatch.query.filter_by(farmer_id=user_id).all()
            stats = {
                'total_batches': len(batches),
                'by_status': {
                    'harvested': len([b for b in batches if b.status == BatchStatus.HARVESTED]),
                    'quality_check': len([b for b in batches if b.status == BatchStatus.QUALITY_CHECK]),
                    'logistics': len([b for b in batches if b.status == BatchStatus.LOGISTICS]),
                    'in_shop': len([b for b in batches if b.status == BatchStatus.IN_SHOP])
                },
                'total_quantity_kg': sum(b.quantity_kg for b in batches)
            }
        
        elif user_role == UserRole.SHOPKEEPER:
            # Shopkeeper statistics
            batches = ProduceBatch.query.filter_by(shopkeeper_id=user_id).all()
            stats = {
                'total_received': len(batches),
                'total_quantity_kg': sum(b.quantity_kg for b in batches),
                'by_produce_type': {}
            }
            
            # Group by produce type
            for batch in batches:
                if batch.produce_type not in stats['by_produce_type']:
                    stats['by_produce_type'][batch.produce_type] = 0
                stats['by_produce_type'][batch.produce_type] += 1
        
        elif user_role == UserRole.ADMIN:
            # Admin statistics
            total_batches = ProduceBatch.query.count()
            stats = {
                'total_batches': total_batches,
                'by_status': {
                    'harvested': ProduceBatch.query.filter_by(status=BatchStatus.HARVESTED).count(),
                    'quality_check': ProduceBatch.query.filter_by(status=BatchStatus.QUALITY_CHECK).count(),
                    'logistics': ProduceBatch.query.filter_by(status=BatchStatus.LOGISTICS).count(),
                    'in_shop': ProduceBatch.query.filter_by(status=BatchStatus.IN_SHOP).count()
                },
                'total_quantity_kg': db.session.query(func.sum(ProduceBatch.quantity_kg)).scalar() or 0
            }
        
        return jsonify({
            'status': 'success',
            'data': {
                'stats': stats
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving statistics: {str(e)}'
        }), 500
