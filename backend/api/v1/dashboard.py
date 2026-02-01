from flask import Blueprint, jsonify, request
from auth_utils import token_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/summary', methods=['GET'])
@token_required
def get_dashboard_summary():
    """Returns a personalized dashboard summary based on user role."""
    user = getattr(request, 'user', {})
    role = user.get('role', 'farmer')
    
    # Mock data for demonstration - in production, fetch from DB
    if role == 'admin':
        data = {
            "total_users": 1250,
            "active_tasks": 15,
            "system_health": "Optimal",
            "pending_registrations": 5
        }
    elif role == 'shopkeeper':
        data = {
            "total_inventory": 4500,
            "recent_orders": 12,
            "low_stock_alerts": 3,
            "today_revenue": "₹25,000"
        }
    elif role == 'consultant':
        data = {
            "pending_consultations": 8,
            "assigned_farmers": 45,
            "expert_score": 4.8
        }
    else: # Default: Farmer
        data = {
            "crop_status": "Healthy",
            "active_schemes": 3,
            "next_task": "Soil Nitrogen Test",
            "market_price_alert": "Tomato prices up by 15%"
        }
        
    return jsonify({
        "status": "success",
        "role": role,
        "data": data
    }), 200
