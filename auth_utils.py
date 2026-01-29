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
