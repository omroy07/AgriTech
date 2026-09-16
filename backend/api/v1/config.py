import os
from flask import Blueprint, jsonify
from backend.config.settings import get_settings

config_bp = Blueprint('config', __name__)


@config_bp.route('/config', methods=['GET'])
@config_bp.route('/config/public', methods=['GET'])
def get_public_config():
    """
    Public configuration endpoint providing runtime feature flags,
    environment info, and frontend-safe parameters.
    Secrets and database credentials are never exposed.
    """
    try:
        settings = get_settings()
        return jsonify({
            "status": "success",
            "data": settings.get_public_config()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@config_bp.route('/config/features', methods=['GET'])
def get_feature_flags():
    """Endpoint returning only active feature flags."""
    try:
        settings = get_settings()
        return jsonify({
            "status": "success",
            "features": settings.get_public_config()["featureFlags"]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@config_bp.route('/config/firebase', methods=['GET'])
def get_firebase_config():
    """Secure endpoint to provide Firebase configuration to client."""
    try:
        settings = get_settings()
        return jsonify(settings.get_public_config()["firebase"]), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
