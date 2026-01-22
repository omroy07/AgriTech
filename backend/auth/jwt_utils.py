"""
JWT utilities for token generation, validation, and refresh token management.
"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify


class JWTManager:
    """Manages JWT token generation and validation."""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.access_token_expiry = timedelta(minutes=15)  # Short-lived
        self.refresh_token_expiry = timedelta(days=7)  # Long-lived
        self.algorithm = 'HS256'
    
    def generate_access_token(self, user_id, username, role):
        """
        Generate a short-lived access token.
        
        Args:
            user_id: User's database ID
            username: User's username/email
            role: User's role (farmer, shopkeeper, admin)
        
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
        Generate a long-lived refresh token.
        
        Args:
            user_id: User's database ID
        
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
            dict: Decoded token payload
        
        Raises:
            jwt.ExpiredSignatureError: Token has expired
            jwt.InvalidTokenError: Token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError('Token has expired')
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError('Invalid token')
    
    def extract_token_from_header(self):
        """
        Extract JWT token from Authorization header.
        
        Returns:
            str: JWT token or None
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
        Validate access token and return payload.
        
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
        Validate refresh token and return payload.
        
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
