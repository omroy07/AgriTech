from flask import Blueprint, g, request
from functools import wraps

from .v1 import api_v1


def add_api_version_header(response):
    """Add API version header to all responses."""
    response.headers['X-API-Version'] = '1.0'
    return response


def deprecated_endpoint(message="This endpoint is deprecated"):
    """Decorator to mark endpoints as deprecated."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-Deprecated'] = 'true'
                response.headers['X-Deprecation-Message'] = message
            return response
        return decorated_function
    return decorator


def register_api(app):
    """Register all API versions with the Flask app."""
    
    # Register v1 API
    app.register_blueprint(api_v1)
    
    # Add version header to all API responses
    @app.after_request
    def after_request(response):
        if request.path.startswith('/api/'):
            response = add_api_version_header(response)
        return response
    
    return app
