"""
JWT Authentication Module
Provides token-based authentication with access/refresh tokens and RBAC.
"""
from .routes import auth_bp
from .decorators import token_required, roles_required
from .jwt_utils import jwt_manager

__all__ = ['auth_bp', 'token_required', 'roles_required', 'jwt_manager']
