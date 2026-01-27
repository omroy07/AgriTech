"""
Authentication decorators for route protection and RBAC.
"""
from functools import wraps
from flask import request, jsonify
from .jwt_utils import jwt_manager


def token_required(f):
    """
    Decorator to protect routes requiring authentication.
    Validates JWT access token from Authorization header.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'user': current_user['username']})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = jwt_manager.extract_token_from_header()
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Authentication token is missing'
            }), 401
        
        is_valid, result = jwt_manager.validate_access_token(token)
        
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': result
            }), 401
        
        # Pass decoded payload as current_user to the route
        return f(current_user=result, *args, **kwargs)
    
    return decorated


def roles_required(*allowed_roles):
    """
    Decorator to restrict access based on user roles.
    Must be used after @token_required decorator.
    
    Args:
        *allowed_roles: Variable number of allowed roles
    
    Usage:
        @app.route('/admin')
        @token_required
        @roles_required('admin')
        def admin_route(current_user):
            return jsonify({'message': 'Admin access granted'})
        
        @app.route('/dashboard')
        @token_required
        @roles_required('farmer', 'shopkeeper')
        def dashboard(current_user):
            return jsonify({'message': 'Welcome to dashboard'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
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
    If valid token present, current_user is available; otherwise None.
    
    Usage:
        @app.route('/public')
        @optional_auth
        def public_route(current_user=None):
            if current_user:
                return jsonify({'message': f'Hello {current_user["username"]}'})
            return jsonify({'message': 'Hello guest'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = jwt_manager.extract_token_from_header()
        
        if token:
            is_valid, result = jwt_manager.validate_access_token(token)
            kwargs['current_user'] = result if is_valid else None
        else:
            kwargs['current_user'] = None
        
        return f(*args, **kwargs)
    
    return decorated
