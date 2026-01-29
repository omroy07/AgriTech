from flask import Blueprint, request, jsonify
from backend.services.scheme_service import scheme_service

schemes_bp = Blueprint('schemes', __name__)

@schemes_bp.route('/schemes', methods=['GET'])
def get_schemes():
    """Get agricultural schemes with optional filtering."""
    category = request.args.get('category')
    
    if category:
        schemes = scheme_service.get_schemes_by_category(category)
    else:
        schemes = scheme_service.get_all_schemes()
        
    return jsonify({
        "status": "success",
        "count": len(schemes),
        "data": schemes
    }), 200

@schemes_bp.route('/schemes/refresh', methods=['POST'])
def refresh_schemes():
    """Admin endpoint to invalidate cache."""
    scheme_service.invalidate_cache()
    return jsonify({"status": "success", "message": "Cache invalidated"}), 200
