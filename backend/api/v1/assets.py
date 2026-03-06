"""
Farm Asset Management API Endpoints
Provides endpoints for asset registration, health monitoring, 
predictive maintenance, and telemetry tracking.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging

from backend.services.asset_service import AssetService
from backend.schemas.asset_schema import (
    AssetCreateSchema, AssetUpdateSchema, TelemetrySchema,
    MaintenanceLogSchema, AssetQuerySchema
)
from backend.services.audit_service import AuditService

logger = logging.getLogger(__name__)

assets_bp = Blueprint('assets', __name__, url_prefix='/api/v1/assets')


@assets_bp.route('/register', methods=['POST'])
@jwt_required()
def register_asset():
    """
    Register a new farm asset for tracking.
    
    Request Body:
        {
            "asset_type": "tractor",
            "asset_name": "John Deere 5075E",
            "manufacturer": "John Deere",
            "model": "5075E",
            "purchase_date": "2023-01-15T00:00:00",
            "purchase_price": 45000
        }
    
    Returns:
        201: Asset created successfully
        400: Invalid data
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        schema = AssetCreateSchema()
        validated_data = schema.load(data)
        
        # Create asset
        asset = AssetService.create_asset(current_user_id, validated_data)
        
        AuditService.log_action(
            action="ASSET_REGISTERED",
            user_id=current_user_id,
            resource_type="FARM_ASSET",
            resource_id=asset.asset_id,
            meta_data={"name": asset.asset_name, "type": asset.asset_type}
        )
        
        return jsonify({
            'success': True,
            'message': 'Asset registered successfully',
            'data': asset.to_dict()
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in register_asset: {e.messages}")
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    except Exception as e:
        logger.error(f"Error in register_asset: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/telemetry/<asset_id>', methods=['POST'])
@jwt_required()
def update_telemetry(asset_id):
    """
    Update asset telemetry data and recalculate health score.
    
    Path Parameters:
        asset_id: Asset identifier
    
    Request Body:
        {
            "runtime_hours": 5.5,
            "temperature_c": 78,
            "vibration_level": 45,
            "fuel_efficiency": 82,
            "error_codes": []
        }
    
    Returns:
        200: Telemetry updated
        400: Invalid data
        404: Asset not found
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate telemetry
        schema = TelemetrySchema()
        validated_data = schema.load(data)
        
        # Update telemetry
        asset, health_score = AssetService.update_telemetry(asset_id, validated_data)
        
        # Verify ownership
        if asset.user_id != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'message': 'Telemetry updated successfully',
            'data': {
                'asset_id': asset.asset_id,
                'health_score': health_score,
                'status': asset.status,
                'next_maintenance_due': asset.next_maintenance_due.isoformat() if asset.next_maintenance_due else None
            }
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error in update_telemetry: {e.messages}")
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    
    except Exception as e:
        logger.error(f"Error in update_telemetry: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/predict-failure/<asset_id>', methods=['POST'])
@jwt_required()
def predict_failure(asset_id):
    """
    Request AI-powered failure prediction for an asset.
    Uses Gemini AI to analyze asset history and telemetry.
    
    Path Parameters:
        asset_id: Asset identifier
    
    Returns:
        200: Prediction generated
        404: Asset not found
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Run AI prediction
        prediction = AssetService.predict_failure_ai(asset_id)
        
        AuditService.log_action(
            action="ASSET_FAILURE_PREDICTION",
            user_id=current_user_id,
            resource_type="FARM_ASSET",
            resource_id=asset_id,
            meta_data={"result": prediction.get('status')}
        )
        
        return jsonify({
            'success': True,
            'message': 'Failure prediction completed',
            'data': prediction
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    
    except Exception as e:
        logger.error(f"Error in predict_failure: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/maintenance-log/<asset_id>', methods=['POST'])
@jwt_required()
def log_maintenance(asset_id):
    """
    Record a maintenance activity for an asset.
    
    Path Parameters:
        asset_id: Asset identifier
    
    Request Body:
        {
            "maintenance_type": "ROUTINE",
            "description": "Oil change and filter replacement",
            "cost": 250.00,
            "parts_replaced": ["oil_filter", "air_filter"],
            "technician_name": "Mike Smith",
            "status": "COMPLETED"
        }
    
    Returns:
        201: Maintenance logged
        400: Invalid data
        404: Asset not found
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        schema = MaintenanceLogSchema()
        validated_data = schema.load(data)
        
        # Log maintenance
        log = AssetService.log_maintenance(asset_id, validated_data)
        
        return jsonify({
            'success': True,
            'message': 'Maintenance logged successfully',
            'data': log.to_dict()
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in log_maintenance: {e.messages}")
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    
    except Exception as e:
        logger.error(f"Error in log_maintenance: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/my-assets', methods=['GET'])
@jwt_required()
def get_my_assets():
    """
    Get all assets owned by the current user.
    
    Query Parameters:
        status: Filter by status (ACTIVE, MAINTENANCE, FAILED, RETIRED)
        asset_type: Filter by type (tractor, tiller, pump, etc.)
        health_min: Minimum health score
        health_max: Maximum health score
    
    Returns:
        200: List of assets
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Parse filters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('asset_type'):
            filters['asset_type'] = request.args.get('asset_type')
        if request.args.get('health_min'):
            filters['health_min'] = float(request.args.get('health_min'))
        if request.args.get('health_max'):
            filters['health_max'] = float(request.args.get('health_max'))
        
        # Get assets
        assets = AssetService.get_assets_by_user(current_user_id, filters)
        
        return jsonify({
            'success': True,
            'count': len(assets),
            'data': [asset.to_dict() for asset in assets]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_my_assets: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_asset_summary():
    """
    Get summary statistics for user's assets.
    
    Returns:
        200: Summary data
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        
        summary = AssetService.get_asset_summary(current_user_id)
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_asset_summary: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/critical', methods=['GET'])
@jwt_required()
def get_critical_assets():
    """
    Get all assets with critical health scores.
    Admin endpoint - returns critical assets across all users.
    
    Query Parameters:
        threshold: Health score threshold (default: 30)
    
    Returns:
        200: List of critical assets
        500: Server error
    """
    try:
        threshold = float(request.args.get('threshold', 30))
        
        assets = AssetService.get_critical_assets(threshold)
        
        return jsonify({
            'success': True,
            'count': len(assets),
            'threshold': threshold,
            'data': [asset.to_dict() for asset in assets]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_critical_assets: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/<asset_id>', methods=['GET'])
@jwt_required()
def get_asset_details(asset_id):
    """
    Get detailed information for a specific asset.
    
    Path Parameters:
        asset_id: Asset identifier
    
    Returns:
        200: Asset details
        404: Asset not found
        500: Server error
    """
    try:
        from backend.models import FarmAsset
        current_user_id = get_jwt_identity()
        
        asset = FarmAsset.query.filter_by(asset_id=asset_id).first()
        
        if not asset:
            return jsonify({'success': False, 'message': 'Asset not found'}), 404
        
        # Verify ownership
        if asset.user_id != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'data': asset.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_asset_details: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/<asset_id>', methods=['PUT'])
@jwt_required()
def update_asset(asset_id):
    """
    Update asset information.
    
    Path Parameters:
        asset_id: Asset identifier
    
    Request Body:
        {
            "asset_name": "Updated Name",
            "status": "MAINTENANCE",
            "alert_threshold_days": 5
        }
    
    Returns:
        200: Asset updated
        400: Invalid data
        404: Asset not found
        500: Server error
    """
    try:
        from backend.models import FarmAsset
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        asset = FarmAsset.query.filter_by(asset_id=asset_id).first()
        
        if not asset:
            return jsonify({'success': False, 'message': 'Asset not found'}), 404
        
        # Verify ownership
        if asset.user_id != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Update fields
        schema = AssetUpdateSchema()
        validated_data = schema.load(data)
        
        for key, value in validated_data.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        from backend.extensions import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Asset updated successfully',
            'data': asset.to_dict()
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error in update_asset: {e.messages}")
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    except Exception as e:
        logger.error(f"Error in update_asset: {str(e)}")
        from backend.extensions import db
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@assets_bp.route('/<asset_id>', methods=['DELETE'])
@jwt_required()
def delete_asset(asset_id):
    """
    Mark an asset as retired.
    
    Path Parameters:
        asset_id: Asset identifier
    
    Returns:
        200: Asset retired
        404: Asset not found
        500: Server error
    """
    try:
        from backend.models import FarmAsset
        from backend.extensions import db
        current_user_id = get_jwt_identity()
        
        asset = FarmAsset.query.filter_by(asset_id=asset_id).first()
        
        if not asset:
            return jsonify({'success': False, 'message': 'Asset not found'}), 404
        
        # Verify ownership
        if asset.user_id != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Mark as retired instead of deleting
        asset.status = 'RETIRED'
        db.session.commit()
        
        AuditService.log_action(
            action="ASSET_RETIRED",
            user_id=current_user_id,
            resource_type="FARM_ASSET",
            resource_id=asset_id,
            risk_level="MEDIUM"
        )
        
        return jsonify({
            'success': True,
            'message': 'Asset retired successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in delete_asset: {str(e)}")
        from backend.extensions import db
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
