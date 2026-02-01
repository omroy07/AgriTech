from functools import wraps
from flask import request, jsonify
import jwt
import os
from security_utils import roles_required, log_security_event

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if " " in auth_header:
                token = auth_header.split(" ")[1]
            else:
                token = auth_header
        
        if not token:
            log_security_event('AUTH_FAILURE', 'Missing Authorization token')
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            # Note: In production, verify against Firebase or a real DB
            data = jwt.decode(token, os.environ.get('JWT_SECRET', 'agritech_secret_key'), algorithms=["HS256"])
            request.user = data
        except jwt.ExpiredSignatureError:
            log_security_event('AUTH_FAILURE', 'Expired token')
            return jsonify({'message': 'Token has expired!'}), 403
        except Exception as e:
            log_security_event('AUTH_FAILURE', f'Invalid token: {str(e)}')
            return jsonify({'message': 'Token is invalid!'}), 403
            
        return f(*args, **kwargs)
    return decorated


def validate_batch_transition(from_status, to_status, user_role):
    """
    Validate if a batch status transition is allowed for a given user role.
    Implements strict role-based access control for supply chain transitions.
    
    Args:
        from_status: Current batch status
        to_status: Target batch status
        user_role: Role of the user attempting the transition
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    from backend.models import BatchStatus, UserRole
    
    # Define role-specific transition rules
    transition_rules = {
        BatchStatus.HARVESTED: {
            BatchStatus.QUALITY_CHECK: {
                'allowed_roles': [UserRole.FARMER, UserRole.ADMIN],
                'description': 'Only farmers can move batches to quality check'
            }
        },
        BatchStatus.QUALITY_CHECK: {
            BatchStatus.LOGISTICS: {
                'allowed_roles': [UserRole.FARMER, UserRole.ADMIN],
                'description': 'Only farmers can approve quality and move to logistics'
            },
            BatchStatus.HARVESTED: {
                'allowed_roles': [UserRole.ADMIN],
                'description': 'Only admins can rollback to harvested'
            }
        },
        BatchStatus.LOGISTICS: {
            BatchStatus.IN_SHOP: {
                'allowed_roles': [UserRole.SHOPKEEPER, UserRole.ADMIN],
                'description': 'Only shopkeepers can mark batch as received'
            },
            BatchStatus.QUALITY_CHECK: {
                'allowed_roles': [UserRole.ADMIN],
                'description': 'Only admins can rollback to quality check'
            }
        },
        BatchStatus.IN_SHOP: {
            BatchStatus.LOGISTICS: {
                'allowed_roles': [UserRole.ADMIN],
                'description': 'Only admins can rollback from shop'
            }
        }
    }
    
    # Check if transition exists
    if from_status not in transition_rules:
        return False, f"Invalid current status: {from_status}"
    
    if to_status not in transition_rules[from_status]:
        return False, f"Cannot transition from {from_status} to {to_status}"
    
    # Check if user role is allowed
    rule = transition_rules[from_status][to_status]
    if user_role not in rule['allowed_roles']:
        log_security_event(
            'UNAUTHORIZED_BATCH_TRANSITION',
            f"User role {user_role} attempted unauthorized transition from {from_status} to {to_status}"
        )
        return False, f"{rule['description']} (current role: {user_role})"
    
    return True, None


def require_batch_ownership(allow_admin=True):
    """
    Decorator to ensure user owns the batch or is an admin.
    Validates that farmers can only modify their own batches.
    
    Args:
        allow_admin: Whether to allow admin access regardless of ownership
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from backend.models import ProduceBatch, UserRole
            
            user = getattr(request, 'user', None)
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401
            
            # Get batch_id from kwargs or request
            batch_id = kwargs.get('batch_id')
            if not batch_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Batch ID required'
                }), 400
            
            # Check batch exists
            batch = ProduceBatch.query.filter_by(batch_id=batch_id).first()
            if not batch:
                return jsonify({
                    'status': 'error',
                    'message': 'Batch not found'
                }), 404
            
            user_role = user.get('role')
            user_id = user.get('user_id') or user.get('id')
            
            # Admin bypass
            if allow_admin and user_role == UserRole.ADMIN:
                return f(*args, **kwargs)
            
            # Check ownership
            if batch.farmer_id != user_id:
                log_security_event(
                    'UNAUTHORIZED_BATCH_ACCESS',
                    f"User {user.get('email')} attempted to access batch {batch_id} owned by user {batch.farmer_id}"
                )
                return jsonify({
                    'status': 'error',
                    'message': 'Access denied: You do not own this batch'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
