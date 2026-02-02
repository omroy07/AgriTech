"""
Farm Logistics & Route Optimization API Endpoints
Provides endpoints for harvest pickup coordination, route optimization,
and cost-sharing logistics.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
import logging

from services.logistics_service import LogisticsService
from schemas.asset_schema import LogisticsOrderSchema, VehicleAssignmentSchema

logger = logging.getLogger(__name__)

logistics_bp = Blueprint('logistics', __name__, url_prefix='/api/v1/logistics')


@logistics_bp.route('/orders/create', methods=['POST'])
@jwt_required()
def create_order():
    """
    Create a new logistics pickup order.
    
    Request Body:
        {
            "crop_type": "wheat",
            "quantity_tons": 5.5,
            "pickup_location": "Farm Site A, GPS: lat,lon",
            "pickup_latitude": 28.6139,
            "pickup_longitude": 77.2090,
            "destination_location": "Market Hub Delhi",
            "destination_latitude": 28.7041,
            "destination_longitude": 77.1025,
            "requested_pickup_date": "2024-06-15T08:00:00",
            "priority": "NORMAL",
            "requires_refrigeration": false
        }
    
    Returns:
        201: Order created successfully
        400: Invalid data
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        schema = LogisticsOrderSchema()
        validated_data = schema.load(data)
        
        # Create order
        order = LogisticsService.create_order(current_user_id, validated_data)
        
        return jsonify({
            'success': True,
            'message': 'Logistics order created successfully',
            'data': order.to_dict()
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in create_order: {e.messages}")
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    except Exception as e:
        logger.error(f"Error in create_order: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/routes/optimize', methods=['POST'])
@jwt_required()
def optimize_routes():
    """
    Optimize pickup routes for a specific date.
    Groups nearby farmers to minimize costs and maximize efficiency.
    
    Request Body:
        {
            "date": "2024-06-15",
            "region": "north-delhi"
        }
    
    Returns:
        200: Routes optimized
        400: Invalid data
        500: Server error
    """
    try:
        data = request.get_json()
        
        if not data.get('date'):
            return jsonify({'success': False, 'message': 'Date is required'}), 400
        
        target_date = datetime.fromisoformat(data['date'])
        region = data.get('region')
        
        # Optimize routes
        routes = LogisticsService.optimize_routes(target_date, region)
        
        return jsonify({
            'success': True,
            'message': f'Route optimization completed: {len(routes)} routes created',
            'count': len(routes),
            'data': routes
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Invalid date format: {str(e)}'}), 400
    
    except Exception as e:
        logger.error(f"Error in optimize_routes: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/routes/<route_group_id>/assign-vehicle', methods=['POST'])
@jwt_required()
def assign_vehicle(route_group_id):
    """
    Assign a vehicle and driver to a route group.
    
    Path Parameters:
        route_group_id: Route identifier
    
    Request Body:
        {
            "vehicle_id": "TRUCK-101",
            "driver_name": "Rajesh Kumar",
            "driver_phone": "+91-9876543210",
            "scheduled_pickup_date": "2024-06-15T07:00:00"
        }
    
    Returns:
        200: Vehicle assigned
        400: Invalid data
        404: Route not found
        500: Server error
    """
    try:
        data = request.get_json()
        
        # Validate input
        schema = VehicleAssignmentSchema()
        validated_data = schema.load(data)
        
        # Assign vehicle
        orders = LogisticsService.assign_vehicle(route_group_id, validated_data)
        
        return jsonify({
            'success': True,
            'message': f'Vehicle assigned to {len(orders)} orders',
            'data': {
                'route_group_id': route_group_id,
                'orders_updated': len(orders),
                'vehicle_id': validated_data['vehicle_id'],
                'driver': validated_data['driver_name']
            }
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error in assign_vehicle: {e.messages}")
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    
    except Exception as e:
        logger.error(f"Error in assign_vehicle: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/orders/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """
    Update logistics order status.
    
    Path Parameters:
        order_id: Order identifier
    
    Request Body:
        {
            "status": "IN_TRANSIT",
            "actual_pickup_date": "2024-06-15T07:30:00"
        }
    
    Returns:
        200: Status updated
        400: Invalid data
        404: Order not found
        500: Server error
    """
    try:
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        status = data['status']
        update_data = {}
        
        if 'actual_pickup_date' in data:
            update_data['actual_pickup_date'] = data['actual_pickup_date']
        
        if 'actual_delivery_date' in data:
            update_data['actual_delivery_date'] = data['actual_delivery_date']
        
        # Update order
        order = LogisticsService.update_order_status(order_id, status, update_data)
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'data': order.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    
    except Exception as e:
        logger.error(f"Error in update_order_status: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/orders/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """
    Get logistics orders for the current user.
    
    Query Parameters:
        status: Filter by status (PENDING, SCHEDULED, IN_TRANSIT, DELIVERED)
        from_date: Start date (ISO format)
        to_date: End date (ISO format)
    
    Returns:
        200: List of orders
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Parse filters
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('from_date'):
            filters['from_date'] = request.args.get('from_date')
        if request.args.get('to_date'):
            filters['to_date'] = request.args.get('to_date')
        
        # Get orders
        orders = LogisticsService.get_orders_by_user(current_user_id, filters)
        
        return jsonify({
            'success': True,
            'count': len(orders),
            'data': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_my_orders: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/routes/<route_group_id>/summary', methods=['GET'])
@jwt_required()
def get_route_summary(route_group_id):
    """
    Get summary details for a route group.
    
    Path Parameters:
        route_group_id: Route identifier
    
    Returns:
        200: Route summary
        404: Route not found
        500: Server error
    """
    try:
        summary = LogisticsService.get_route_summary(route_group_id)
        
        if not summary:
            return jsonify({'success': False, 'message': 'Route not found'}), 404
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_route_summary: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """
    Get logistics performance analytics.
    
    Query Parameters:
        days: Number of days to analyze (default: 30)
        user_id: Filter by user (optional, admin only)
    
    Returns:
        200: Analytics data
        500: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        
        days = int(request.args.get('days', 30))
        user_filter = request.args.get('user_id')
        
        # Use current user unless admin requests different user
        analytics_user_id = current_user_id
        if user_filter:
            # TODO: Add admin role check here
            analytics_user_id = int(user_filter)
        
        # Get analytics
        analytics = LogisticsService.get_logistics_analytics(analytics_user_id, days)
        
        return jsonify({
            'success': True,
            'data': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/orders/<order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """
    Get detailed information for a specific order.
    
    Path Parameters:
        order_id: Order identifier
    
    Returns:
        200: Order details
        404: Order not found
        500: Server error
    """
    try:
        from models import LogisticsOrder
        current_user_id = get_jwt_identity()
        
        order = LogisticsOrder.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Verify ownership
        if order.user_id != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'data': order.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_order_details: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/orders/<order_id>', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    """
    Cancel a logistics order.
    
    Path Parameters:
        order_id: Order identifier
    
    Returns:
        200: Order cancelled
        404: Order not found
        400: Cannot cancel order in current status
        500: Server error
    """
    try:
        from models import LogisticsOrder
        from extensions import db
        current_user_id = get_jwt_identity()
        
        order = LogisticsOrder.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Verify ownership
        if order.user_id != current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Check if cancellable
        if order.status in ['DELIVERED', 'CANCELLED']:
            return jsonify({'success': False, 'message': f'Cannot cancel order with status: {order.status}'}), 400
        
        # Cancel order
        order.status = 'CANCELLED'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in cancel_order: {str(e)}")
        from extensions import db
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@logistics_bp.route('/routes/active', methods=['GET'])
@jwt_required()
def get_active_routes():
    """
    Get all active routes (scheduled or in-transit).
    
    Query Parameters:
        date: Filter by date (ISO format)
    
    Returns:
        200: List of active routes
        500: Server error
    """
    try:
        from models import LogisticsOrder
        from sqlalchemy import distinct
        
        # Get unique route groups with active orders
        query = LogisticsOrder.query.filter(
            LogisticsOrder.status.in_(['SCHEDULED', 'IN_TRANSIT'])
        )
        
        if request.args.get('date'):
            target_date = datetime.fromisoformat(request.args.get('date'))
            query = query.filter(
                LogisticsOrder.scheduled_pickup_date.cast(db.Date) == target_date.date()
            )
        
        # Get distinct route group IDs
        route_ids = [r.route_group_id for r in query.distinct(LogisticsOrder.route_group_id).all() if r.route_group_id]
        
        # Get summary for each route
        routes = [LogisticsService.get_route_summary(rid) for rid in route_ids]
        
        return jsonify({
            'success': True,
            'count': len(routes),
            'data': routes
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_active_routes: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
