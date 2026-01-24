"""
Authentication module for JWT-based authentication with RBAC.
"""
from .routes import auth_bp
from .decorators import token_required, roles_accepted

__all__ = ['auth_bp', 'token_required', 'roles_accepted']
