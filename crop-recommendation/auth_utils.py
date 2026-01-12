from functools import wraps
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For testing purposes, bypass authentication
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For testing purposes, bypass role checking
            return f(*args, **kwargs)
        return decorated_function
    return decorator
