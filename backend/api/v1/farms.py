from flask import Blueprint, request, jsonify
from backend.services.farm_service import FarmService
from backend.services.farm_analytics import FarmAnalytics
from auth_utils import token_required
import logging

farms_bp = Blueprint('farms', __name__)

@farms_bp.route('/', methods=['GET'])
@token_required
def get_my_farms(current_user):
    """List all farms the user is associated with"""
    farms = FarmService.get_user_farms(current_user.id)
    return jsonify({
        'status': 'success',
        'data': [f.to_dict() for f in farms]
    }), 200

@farms_bp.route('/', methods=['POST'])
@token_required
def create_farm(current_user):
    """Register a new farm under the current user"""
    data = request.get_json()
    if not data or 'name' not in data or 'location' not in data:
        return jsonify({'status': 'error', 'message': 'Name and location required'}), 400
        
    farm, error = FarmService.create_farm(
        user_id=current_user.id,
        name=data['name'],
        location=data['location'],
        acreage=data.get('acreage', 0),
        description=data.get('description'),
        soil_details=data.get('soil_details')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': farm.to_dict()
    }), 201

@farms_bp.route('/<int:farm_id>/analytics', methods=['GET'])
@token_required
def get_farm_analytics(current_user, farm_id):
    """Retrieve performance KPIs for a specific farm"""
    # Permission check: must be a member
    from backend.models.farm import FarmMember
    membership = FarmMember.query.filter_by(farm_id=farm_id, user_id=current_user.id).first()
    if not membership:
        return jsonify({'status': 'error', 'message': 'Unauthorized access to farm data'}), 403
        
    stats = FarmAnalytics.get_farm_kpis(farm_id)
    return jsonify({
        'status': 'success',
        'data': stats
    }), 200

@farms_bp.route('/<int:farm_id>/assets', methods=['POST'])
@token_required
def add_asset(current_user, farm_id):
    """Add equipment/assets to a farm's inventory"""
    data = request.get_json()
    asset, error = FarmService.add_asset(
        farm_id=farm_id,
        name=data['name'],
        category=data['category'],
        purchase_value=data.get('purchase_value', 0)
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': asset.to_dict()
    }), 201
