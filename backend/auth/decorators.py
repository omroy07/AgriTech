"""
Decorators for route protection and role-based access control.
"""
from functools import wraps
from flask import request, jsonify
from .jwt_utils import jwt_manager


def token_required(f):
    """
    Decorator to protect routes that require authentication.
    Validates JWT access token from Authorization header.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': f'Hello {current_user["username"]}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = jwt_manager.extract_token_from_header()
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing'
            }), 401
        
        is_valid, result = jwt_manager.validate_access_token(token)
        
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': result
            }), 401
        
        # Pass decoded token payload as current_user to the route
        return f(current_user=result, *args, **kwargs)
    
    return decorated


def roles_accepted(*allowed_roles):
    """
    Decorator to restrict access based on user roles.
    Must be used after @token_required decorator.
    
    Args:
        *allowed_roles: Variable number of role strings (e.g., 'farmer', 'admin', 'shopkeeper')
    
    Usage:
        @app.route('/admin-only')
        @token_required
        @roles_accepted('admin')
        def admin_route(current_user):
            return jsonify({'message': 'Admin access granted'})
        
        @app.route('/farmer-or-admin')
        @token_required
        @roles_accepted('farmer', 'admin')
        def farmer_route(current_user):
            return jsonify({'message': 'Welcome farmer or admin'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Extract current_user from kwargs (passed by @token_required)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401
            
            user_role = current_user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'status': 'error',
                    'message': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


def optional_auth(f):
    """
    Decorator for routes that work with or without authentication.
    If token is present and valid, current_user will be available.
    If no token or invalid token, current_user will be None.
    
    Usage:
        @app.route('/optional')
        @optional_auth
        def optional_route(current_user=None):
            if current_user:
                return jsonify({'message': f'Hello {current_user["username"]}'})
            return jsonify({'message': 'Hello guest'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = jwt_manager.extract_token_from_header()
        
        if token:
            is_valid, result = jwt_manager.validate_access_token(token)
            if is_valid:
                kwargs['current_user'] = result
            else:
                kwargs['current_user'] = None
        else:
            kwargs['current_user'] = None
        
        return f(*args, **kwargs)
    
    return decorated
