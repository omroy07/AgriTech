"""
Security utilities for AgriTech Flask applications
Provides input validation, sanitization, and security helpers
"""

import re
import bcrypt
import hashlib
import uuid
import datetime
from functools import wraps
from flask import request, jsonify
from email_validator import validate_email, EmailNotValidError

# Input validation patterns
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^\+?1?\d{9,15}$'
USERNAME_PATTERN = r'^[a-zA-Z0-9_]{3,20}$'

def validate_required_fields(required_fields):
    """Decorator to validate required fields in form data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_fields(required_fields):
    """Decorator to validate required fields in JSON data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            json_data = request.get_json()
            if not json_data:
                return jsonify({'error': 'Invalid JSON data'}), 400
                
            for field in required_fields:
                if field not in json_data or not json_data[field].strip():
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(text, max_length=255):
    """Sanitize text input to prevent XSS and injection attacks"""
    if not isinstance(text, str):
        return ""
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\']', '', text.strip())
    return cleaned[:max_length]

def sanitize_numeric_input(value, min_val=None, max_val=None, field_name=""):
    """Sanitize and validate numeric input"""
    try:
        # Remove any non-numeric characters except decimal point and minus
        cleaned = re.sub(r'[^0-9.-]', '', str(value))
        num_value = float(cleaned)
        
        if min_val is not None and num_value < min_val:
            raise ValueError(f"{field_name} must be at least {min_val}")
        if max_val is not None and num_value > max_val:
            raise ValueError(f"{field_name} must be at least {max_val}")
            
        return num_value
    except ValueError as e:
        raise ValueError(f"Invalid {field_name}: {str(e)}")

def validate_email_format(email):
    """Validate email format using email-validator library"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_phone_format(phone):
    """Validate phone number format"""
    return bool(re.match(PHONE_PATTERN, phone))

def validate_username_format(username):
    """Validate username format"""
    return bool(re.match(USERNAME_PATTERN, username))

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_secure_token():
    """Generate a secure random token"""
    return str(uuid.uuid4())

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal attacks"""
    if not filename:
        return ""
    # Remove any path separators and dangerous characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    return cleaned

def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file_size(file, max_size_bytes):
    """Validate file size"""
    if file.content_length and file.content_length > max_size_bytes:
        return False
    return True

def rate_limit(max_requests, window_seconds):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This is a simple implementation
            # In production, use Redis or database for rate limiting
            client_ip = request.remote_addr
            # Add rate limiting logic here
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type, details, user_ip=None):
    """Log security events"""
    if user_ip is None:
        user_ip = request.remote_addr
    
    log_entry = {
        'timestamp': str(datetime.datetime.now()),
        'event_type': event_type,
        'user_ip': user_ip,
        'details': details
    }
    
    # In production, log to a secure logging service
    print(f"SECURITY EVENT: {log_entry}")

def sanitize_sql_input(value):
    """Sanitize input for SQL queries (use parameterized queries instead)"""
    if not isinstance(value, str):
        return ""
    # Remove SQL injection patterns
    dangerous_patterns = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
        r'(\b(and|or)\b\s+\d+\s*=\s*\d+)',
        r'(\b(and|or)\b\s+\'\w+\'\s*=\s*\'\w+\')',
        r'(\b(and|or)\b\s+\w+\s*=\s*\w+)',
    ]
    
    cleaned = value
    for pattern in dangerous_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

# Security headers helper
def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response