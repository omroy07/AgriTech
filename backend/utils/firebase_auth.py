import firebase_admin
from firebase_admin import auth, credentials
import os
from security_utils import log_security_event

# Initialize Firebase Admin SDK
# In production, path to service account JSON should be in FIREBASE_SERVICE_ACCOUNT
service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

if service_account_path and os.path.exists(service_account_path):
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
else:
    # Initialize with default credentials for dev/local
    try:
        firebase_admin.initialize_app()
    except Exception as e:
        print(f"Warning: Firebase Admin SDK not initialized: {e}")

def set_user_role(uid, role):
    """Sets a custom role claim for a Firebase user."""
    try:
        # Valid roles: admin, farmer, shopkeeper, consultant
        valid_roles = ['admin', 'farmer', 'shopkeeper', 'consultant']
        if role not in valid_roles:
            raise ValueError(f"Invalid role: {role}")
            
        auth.set_custom_user_claims(uid, {'role': role})
        log_security_event('ROLE_UPDATE', f"Updated role for UID {uid} to {role}")
        return True
    except Exception as e:
        log_security_event('ROLE_UPDATE_FAILURE', f"Failed to update role for UID {uid}: {str(e)}")
        return False

def verify_firebase_token(id_token):
    """Verifies a Firebase ID token and returns decoded claims."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        log_security_event('AUTH_FAILURE', f"Firebase token verification failed: {str(e)}")
        return None
