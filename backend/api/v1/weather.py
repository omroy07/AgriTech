from flask import Blueprint, request, jsonify
from backend.services.weather_service import weather_service
from extensions import limiter
from auth_utils import token_required

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather/forecast', methods=['GET'])
@limiter.limit("10 per minute")
@token_required
def get_weather():
    """Get weather forecast for a location."""
    location = request.args.get('location')
    if not location:
        return jsonify({"status": "error", "message": "Location is required"}), 400
    
    days = request.args.get('days', 3, type=int)
    data = weather_service.get_weather_forecast(location, days=days)
    
    if "error" in data:
        return jsonify({"status": "error", "message": data["error"]}), 500
        
    return jsonify({"status": "success", "data": data}), 200

@weather_bp.route('/weather/analysis', methods=['GET'])
@limiter.limit("5 per minute")
@token_required
def get_weather_analysis():
    """Get agricultural weather analysis for a location."""
    location = request.args.get('location')
    if not location:
        return jsonify({"status": "error", "message": "Location is required"}), 400
        
    analysis = weather_service.get_farming_analysis(location)
    
    if "error" in analysis:
        return jsonify({"status": "error", "message": analysis["error"]}), 500
        
    return jsonify({"status": "success", "data": analysis}), 200

@weather_bp.route('/weather/crop-advice', methods=['GET'])
@token_required
def get_crop_advice():
    """Get crop-specific weather advice."""
    location = request.args.get('location')
    crop = request.args.get('crop')
    
    if not location or not crop:
        return jsonify({"status": "error", "message": "Location and crop are required"}), 400
        
    weather_data = weather_service.get_weather_forecast(location, days=1)
    if "error" in weather_data:
        return jsonify({"status": "error", "message": weather_data["error"]}), 500
        
    current = weather_data.get("current", {})
    advice = weather_service.get_crop_specific_advice(
        crop=crop,
        temperature=current.get("temp_c", 0),
        humidity=current.get("humidity", 0),
        rainfall=current.get("precip_mm", 0)
    )
    
    return jsonify({"status": "success", "data": advice}), 200
