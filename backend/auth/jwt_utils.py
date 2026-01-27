"""
JWT token management utilities.
Handles token generation, validation, and refresh logic.
"""
import jwt
import os
from datetime import datetime, timedelta
from flask import request


class JWTManager:
    """Manages JWT token operations."""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'change-this-secret-key-in-production')
        self.access_token_expiry = timedelta(minutes=30)  # Short-lived access tokens
        self.refresh_token_expiry = timedelta(days=30)  # Long-lived refresh tokens
        self.algorithm = 'HS256'
    
    def generate_access_token(self, user_id, username, role):
        """
        Generate short-lived access token.
        
        Args:
            user_id: User database ID
            username: Username
            role: User role (farmer, shopkeeper, admin)
        
        Returns:
            str: JWT access token
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'type': 'access',
            'exp': datetime.utcnow() + self.access_token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id):
        """
        Generate long-lived refresh token.
        
        Args:
            user_id: User database ID
        
        Returns:
            str: JWT refresh token
        """
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + self.refresh_token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token):
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            dict: Decoded payload
        
        Raises:
            jwt.ExpiredSignatureError: Token expired
            jwt.InvalidTokenError: Invalid token
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    
    def extract_token_from_header(self):
        """
        Extract JWT from Authorization header.
        
        Returns:
            str: Token or None
        """
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    
    def extract_refresh_token_from_cookie(self):
        """
        Extract refresh token from HTTPOnly cookie.
        
        Returns:
            str: Refresh token or None
        """
        return request.cookies.get('refresh_token')
    
    def validate_access_token(self, token):
        """
        Validate access token.
        
        Args:
            token: JWT access token
        
        Returns:
            tuple: (is_valid, payload_or_error_message)
        """
        try:
            payload = self.decode_token(token)
            if payload.get('type') != 'access':
                return False, 'Invalid token type'
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, 'Token has expired'
        except jwt.InvalidTokenError:
            return False, 'Invalid token'
        except Exception as e:
            return False, str(e)
    
    def validate_refresh_token(self, token):
        """
        Validate refresh token.
        
        Args:
            token: JWT refresh token
        
        Returns:
            tuple: (is_valid, payload_or_error_message)
        """
        try:
            payload = self.decode_token(token)
            if payload.get('type') != 'refresh':
                return False, 'Invalid token type'
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, 'Refresh token has expired'
        except jwt.InvalidTokenError:
            return False, 'Invalid refresh token'
        except Exception as e:
            return False, str(e)


# Global JWT manager instance
jwt_manager = JWTManager()
