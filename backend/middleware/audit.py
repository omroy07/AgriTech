import time
import functools
from flask import request, g, has_request_context
from backend.services.audit_service import AuditService

def audit_request(action_name=None):
    """
    Decorator for explicitly auditing specific route actions.
    Example: @audit_request("VIEW_SENSITIVE_DATA")
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            action = action_name or f"API_CALL_{request.endpoint}"
            
            # Record start time
            start_time = time.time()
            
            # Execute the function
            response = f(*args, **kwargs)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Async log or direct log depends on performance needs
            # For this "hard" issue, we'll do direct logging but capture status codes
            status_code = 200
            if hasattr(response, 'status_code'):
                status_code = response.status_code
            elif isinstance(response, tuple) and len(response) > 1:
                status_code = response[1]
                
            AuditService.log_action(
                action=action,
                meta_data={
                    "duration_ms": int(duration * 1000),
                    "status": status_code,
                    "endpoint": request.endpoint
                }
            )
            return response
        return decorated_function
    return decorator

class AuditMiddleware:
    """
    Global middleware to automatically audit high-risk requests.
    """
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        # Store start time in flask.g for duration calculation
        g.audit_start_time = time.time()

    def after_request(self, response):
        """
        Post-request hook to log non-GET requests or specific endpoints.
        """
        if not has_request_context():
            return response
            
        # We generally audit state-changing requests (POST, PUT, DELETE)
        # and ignore GET requests unless they are to sensitive paths
        is_state_change = request.method in ['POST', 'PUT', 'DELETE', 'PATCH']
        is_sensitive = any(path in request.path for path in ['/admin', '/settings', '/auth'])
        
        if is_state_change or is_sensitive:
            duration = time.time() - getattr(g, 'audit_start_time', time.time())
            
            # Avoid auditing the audit logs themselves to prevent infinite loops
            if 'audit' in request.path:
                return response
                
            AuditService.log_action(
                action=f"{request.method}_{request.endpoint or 'unknown'}",
                risk_level='MEDIUM' if is_state_change else 'LOW',
                meta_data={
                    "duration_ms": int(duration * 1000),
                    "status_code": response.status_code
                }
            )
            
        return response
