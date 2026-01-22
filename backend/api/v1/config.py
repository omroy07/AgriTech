import os
from flask import Blueprint, jsonify

config_bp = Blueprint('config', __name__)


@config_bp.route('/config/firebase', methods=['GET'])
def get_firebase_config():
    """Secure endpoint to provide Firebase configuration to client."""
    try:
        return jsonify({
            'apikey': os.environ.get('FIREBASE_API_KEY', ''),
            'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
            'projectId': os.environ.get('FIREBASE_PROJECT_ID', ''),
            'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
            'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
            'appId': os.environ.get('FIREBASE_APP_ID', ''),
            'measurementId': os.environ.get('FIREBASE_MEASUREMENT_ID', '')
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
