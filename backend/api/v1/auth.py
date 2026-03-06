from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.services.audit_service import AuditService
from backend.models import User
from backend.extensions import db, limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Register a new user and send verification email."""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400

    # Validate email domain
    if not email.lower().endswith("@gmail.com"):
        return jsonify({'status': 'error', 'message': 'Please use a @gmail.com address'}), 400

    # Validate username/full_name pattern
    import re
    if not re.match(r'^[A-Za-z\s]+$', username):
        return jsonify({'status': 'error', 'message': 'Full Name should only contain letters and spaces'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
        
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    AuthService.send_verification_email(user)
    
    AuditService.log_action(
        action="USER_REGISTERED",
        user_id=user.id,
        meta_data={"username": username, "email": email}
    )
    
    return jsonify({
        'status': 'success',
        'message': 'User registered. Please check your email to verify your account.'
    }), 201

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify email endpoint."""
    success, message = AuthService.verify_email(token)
    if success:
        AuditService.log_action(action="EMAIL_VERIFIED", meta_data={"token": token})
        return jsonify({'status': 'success', 'message': message}), 200
    AuditService.log_action(action="EMAIL_VERIFICATION_FAILED", risk_level='MEDIUM', meta_data={"error": message})
    return jsonify({'status': 'error', 'message': message}), 400

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    """Request password reset email."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400
        
    user = User.query.filter_by(email=email).first()
    if user:
        AuthService.send_password_reset_email(user)
        AuditService.log_action(action="PASSWORD_RESET_REQUESTED", user_id=user.id)
    else:
        AuditService.log_action(action="UNKNOWN_PASSWORD_RESET_ATTEMPT", risk_level='MEDIUM', meta_data={"email": email})
    
    # Always return same message to prevent email enumeration
    return jsonify({
        'status': 'success',
        'message': 'If an account exists with that email, a reset link has been sent.'
    }), 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password(token):
    """Reset password using token."""
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password:
        return jsonify({'status': 'error', 'message': 'New password is required'}), 400
        
    success, message = AuthService.reset_password(token, new_password)
    if success:
        AuditService.log_action(action="PASSWORD_RESET_SUCCESSFUL")
        return jsonify({'status': 'success', 'message': message}), 200
    AuditService.log_action(action="PASSWORD_RESET_FAILED", risk_level='MEDIUM', meta_data={"error": message})
    return jsonify({'status': 'error', 'message': message}), 400
