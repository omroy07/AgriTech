"""
Real-Time Logistics Tracking via WebSockets
Broadcasts pickup events, route updates, and delivery status to connected clients.
"""
from flask_socketio import emit, join_room, leave_room, rooms
from extensions import socketio
import logging
from functools import wraps
from flask_jwt_extended import decode_token
from flask import request

logger = logging.getLogger(__name__)


def authenticated_only(f):
    """Decorator to require authentication for Socket.IO events."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        # Get token from connection args
        token = request.args.get('token')
        
        if not token:
            logger.warning("Socket.IO connection attempt without token")
            emit('error', {'message': 'Authentication required'})
            return
        
        try:
            # Verify JWT token
            decoded = decode_token(token)
            user_id = decoded['sub']
            
            # Add user_id to kwargs
            kwargs['user_id'] = user_id
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Socket.IO auth error: {str(e)}")
            emit('error', {'message': 'Invalid authentication token'})
            return
    
    return wrapped


@socketio.on('connect', namespace='/logistics')
def handle_logistics_connect():
    """Handle client connection to logistics tracking namespace."""
    logger.info(f"Client connected to /logistics: {request.sid}")
    emit('connected', {'message': 'Connected to logistics tracking'})


@socketio.on('disconnect', namespace='/logistics')
def handle_logistics_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected from /logistics: {request.sid}")


@socketio.on('subscribe_order', namespace='/logistics')
@authenticated_only
def handle_subscribe_order(data, user_id=None):
    """
    Subscribe to real-time updates for a specific order.
    
    Args:
        data: {'order_id': 'LOG-20240615-...'}
    """
    order_id = data.get('order_id')
    
    if not order_id:
        emit('error', {'message': 'order_id is required'})
        return
    
    # Join room for this order
    join_room(f'order_{order_id}')
    
    logger.info(f"User {user_id} subscribed to order {order_id}")
    emit('subscribed', {'order_id': order_id, 'message': f'Subscribed to order updates'})


@socketio.on('unsubscribe_order', namespace='/logistics')
@authenticated_only
def handle_unsubscribe_order(data, user_id=None):
    """
    Unsubscribe from order updates.
    
    Args:
        data: {'order_id': 'LOG-20240615-...'}
    """
    order_id = data.get('order_id')
    
    if not order_id:
        emit('error', {'message': 'order_id is required'})
        return
    
    # Leave room
    leave_room(f'order_{order_id}')
    
    logger.info(f"User {user_id} unsubscribed from order {order_id}")
    emit('unsubscribed', {'order_id': order_id})


@socketio.on('subscribe_route', namespace='/logistics')
@authenticated_only
def handle_subscribe_route(data, user_id=None):
    """
    Subscribe to real-time updates for an entire route group.
    
    Args:
        data: {'route_group_id': 'ROUTE-20240615-001'}
    """
    route_group_id = data.get('route_group_id')
    
    if not route_group_id:
        emit('error', {'message': 'route_group_id is required'})
        return
    
    # Join room for this route
    join_room(f'route_{route_group_id}')
    
    logger.info(f"User {user_id} subscribed to route {route_group_id}")
    emit('subscribed', {'route_group_id': route_group_id, 'message': 'Subscribed to route updates'})


@socketio.on('unsubscribe_route', namespace='/logistics')
@authenticated_only
def handle_unsubscribe_route(data, user_id=None):
    """
    Unsubscribe from route updates.
    
    Args:
        data: {'route_group_id': 'ROUTE-20240615-001'}
    """
    route_group_id = data.get('route_group_id')
    
    if not route_group_id:
        emit('error', {'message': 'route_group_id is required'})
        return
    
    # Leave room
    leave_room(f'route_{route_group_id}')
    
    logger.info(f"User {user_id} unsubscribed from route {route_group_id}")
    emit('unsubscribed', {'route_group_id': route_group_id})


# Server-side broadcast functions
# These are called by the backend services to broadcast updates

def broadcast_order_update(order_id: str, status: str, data: dict):
    """
    Broadcast order status update to all subscribed clients.
    
    Args:
        order_id: Order identifier
        status: New status
        data: Additional update data
    """
    try:
        payload = {
            'order_id': order_id,
            'status': status,
            'timestamp': data.get('timestamp'),
            'data': data
        }
        
        socketio.emit(
            'order_status_update',
            payload,
            room=f'order_{order_id}',
            namespace='/logistics'
        )
        
        logger.info(f"Broadcasted order update: {order_id} -> {status}")
        
    except Exception as e:
        logger.error(f"Error broadcasting order update: {str(e)}")


def broadcast_route_update(route_group_id: str, event_type: str, data: dict):
    """
    Broadcast route-level event to all subscribed clients.
    
    Args:
        route_group_id: Route identifier
        event_type: Type of event (VEHICLE_ASSIGNED, PICKUP_STARTED, etc.)
        data: Event data
    """
    try:
        payload = {
            'route_group_id': route_group_id,
            'event_type': event_type,
            'timestamp': data.get('timestamp'),
            'data': data
        }
        
        socketio.emit(
            'route_event',
            payload,
            room=f'route_{route_group_id}',
            namespace='/logistics'
        )
        
        logger.info(f"Broadcasted route event: {route_group_id} -> {event_type}")
        
    except Exception as e:
        logger.error(f"Error broadcasting route update: {str(e)}")


def broadcast_vehicle_location(route_group_id: str, vehicle_id: str, latitude: float, longitude: float):
    """
    Broadcast live vehicle location to route subscribers.
    
    Args:
        route_group_id: Route identifier
        vehicle_id: Vehicle identifier
        latitude: Current latitude
        longitude: Current longitude
    """
    try:
        payload = {
            'route_group_id': route_group_id,
            'vehicle_id': vehicle_id,
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit(
            'vehicle_location_update',
            payload,
            room=f'route_{route_group_id}',
            namespace='/logistics'
        )
        
    except Exception as e:
        logger.error(f"Error broadcasting vehicle location: {str(e)}")


def broadcast_pickup_complete(order_id: str, route_group_id: str, data: dict):
    """
    Broadcast pickup completion event.
    
    Args:
        order_id: Order identifier
        route_group_id: Route identifier
        data: Pickup details
    """
    try:
        payload = {
            'order_id': order_id,
            'route_group_id': route_group_id,
            'event': 'PICKUP_COMPLETE',
            'timestamp': data.get('timestamp'),
            'data': data
        }
        
        # Broadcast to both order and route subscribers
        socketio.emit(
            'pickup_complete',
            payload,
            room=f'order_{order_id}',
            namespace='/logistics'
        )
        
        socketio.emit(
            'pickup_complete',
            payload,
            room=f'route_{route_group_id}',
            namespace='/logistics'
        )
        
        logger.info(f"Broadcasted pickup completion: {order_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting pickup completion: {str(e)}")


def broadcast_delivery_complete(order_id: str, data: dict):
    """
    Broadcast delivery completion event.
    
    Args:
        order_id: Order identifier
        data: Delivery details
    """
    try:
        payload = {
            'order_id': order_id,
            'event': 'DELIVERY_COMPLETE',
            'timestamp': data.get('timestamp'),
            'data': data
        }
        
        socketio.emit(
            'delivery_complete',
            payload,
            room=f'order_{order_id}',
            namespace='/logistics'
        )
        
        logger.info(f"Broadcasted delivery completion: {order_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting delivery completion: {str(e)}")


# Import datetime for timestamps
from datetime import datetime
