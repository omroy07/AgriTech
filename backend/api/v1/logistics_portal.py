from flask import Blueprint, request, jsonify
from backend.services.logistics_service import LogisticsService
from backend.models.logistics_v2 import TransportRoute, DriverProfile, DeliveryVehicle
from auth_utils import token_required

logistics_portal_bp = Blueprint('logistics_portal', __name__)

@logistics_portal_bp.route('/dispatch', methods=['POST'])
@token_required
def create_dispatch(current_user):
    """Creates a new transport dispatch."""
    data = request.get_json()
    route, error = LogisticsService.create_dispatch(
        driver_id=data['driver_id'],
        vehicle_id=data['vehicle_id'],
        origin=data['origin'],
        destination=data['destination'],
        cargo_weight=float(data['weight']),
        coords=data.get('coords') # {'origin': [lat,lng], 'dest': [lat,lng]}
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'data': route.to_dict()
    }), 201

@logistics_portal_bp.route('/routes/active', methods=['GET'])
@token_required
def get_active_routes(current_user):
    """Lists all in-transit routes."""
    routes = TransportRoute.query.filter(TransportRoute.status.in_(['PENDING', 'IN_TRANSIT'])).all()
    return jsonify({
        'status': 'success',
        'data': [r.to_dict() for r in routes]
    }), 200

@logistics_portal_bp.route('/route/<int:route_id>/start', methods=['POST'])
@token_required
def start_route(current_user, route_id):
    success, error = LogisticsService.start_route(route_id)
    if not success:
        return jsonify({'status': 'error', 'message': error}), 400
    return jsonify({'status': 'success', 'message': 'Route started'}), 200

@logistics_portal_bp.route('/route/<int:route_id>/complete', methods=['POST'])
@token_required
def complete_route(current_user, route_id):
    data = request.get_json()
    success, error = LogisticsService.complete_route(route_id, float(data['actual_distance']))
    if not success:
        return jsonify({'status': 'error', 'message': error}), 400
    return jsonify({'status': 'success', 'message': 'Route completed'}), 200

@logistics_portal_bp.route('/fleet/stats', methods=['GET'])
@token_required
def get_fleet_stats(current_user):
    stats = LogisticsService.get_fleet_status()
    return jsonify({
        'status': 'success',
        'data': stats
    }), 200

@logistics_portal_bp.route('/drivers/available', methods=['GET'])
@token_required
def get_available_drivers(current_user):
    drivers = DriverProfile.query.filter_by(status='AVAILABLE').all()
    return jsonify({
        'status': 'success',
        'data': [{'id': d.id, 'name': f"Driver #{d.id}"} for d in drivers]
    }), 200

@logistics_portal_bp.route('/vehicles/idle', methods=['GET'])
@token_required
def get_idle_vehicles(current_user):
    vehicles = DeliveryVehicle.query.filter_by(status='IDLE').all()
    return jsonify({
        'status': 'success',
        'data': [{'id': v.id, 'plate': v.plate_number, 'type': v.vehicle_type} for v in vehicles]
    }), 200
