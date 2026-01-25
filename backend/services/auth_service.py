import secrets
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_mail import Message
from backend.extensions import db, mail
from backend.models import User, Token
from backend.utils.logger import logger

class AuthService:
    @staticmethod
    def generate_token(user_id, token_type, hours=24):
        """Generate a secure token and save it to the database."""
        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=hours)
        
        # Remove any existing tokens of the same type for this user
        Token.query.filter_by(user_id=user_id, type=token_type).delete()
        
        new_token = Token(
            user_id=user_id,
            token=token_value,
            type=token_type,
            expires_at=expires_at
        )
        db.session.add(new_token)
        db.session.commit()
        return token_value

    @staticmethod
    def send_verification_email(user):
        """Send an email verification link to the user."""
        token = AuthService.generate_token(user.id, 'verification')
        # In a real app, this would be a full URL to the frontend
        verify_url = f"http://localhost:5000/api/v1/auth/verify-email/{token}"
        
        msg = Message(
            "Verify Your AgriTech Account",
            recipients=[user.email],
            body=f"Hello {user.username},\n\nPlease verify your email by clicking the link: {verify_url}\n\nThis link expires in 24 hours."
        )
        try:
            mail.send(msg)
            return True
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(user):
        """Send a password reset link to the user."""
        token = AuthService.generate_token(user.id, 'reset', hours=1)
        reset_url = f"http://localhost:5000/reset-password/{token}"
        
        msg = Message(
            "AgriTech Password Reset",
            recipients=[user.email],
            body=f"Hello,\n\nYou requested a password reset. Click the link to set a new password: {reset_url}\n\nThis link expires in 1 hour. If you didn't request this, ignore this email."
        )
        try:
            mail.send(msg)
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False

    @staticmethod
    def verify_email(token_value):
        """Verify the user's email using the provided token."""
        token_record = Token.query.filter_by(token=token_value, type='verification').first()
        
        if not token_record or token_record.is_expired():
            return False, "Invalid or expired token"
        
        user = User.query.get(token_record.user_id)
        if user:
            user.is_email_verified = True
            user.email_verified_at = datetime.utcnow()
            db.session.delete(token_record)
            db.session.commit()
            return True, "Email verified successfully"
        
        return False, "User not found"

    @staticmethod
    def reset_password(token_value, new_password):
        """Reset the user's password using the provided token."""
        token_record = Token.query.filter_by(token=token_value, type='reset').first()
        
        if not token_record or token_record.is_expired():
            return False, "Invalid or expired token"
        
        user = User.query.get(token_record.user_id)
        if user:
            user.set_password(new_password)
            db.session.delete(token_record)
            db.session.commit()
            return True, "Password reset successfully"
        
        return False, "User not found"
