from flask import Blueprint, request, jsonify
from backend.services.weather_service import WeatherService
from auth_utils import token_required

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/current', methods=['GET'])
def get_weather():
    location = request.args.get('location')
    if not location:
        return jsonify({'status': 'error', 'message': 'Location required'}), 400
        
    weather = WeatherService.get_latest_weather(location)
    if not weather:
        return jsonify({'status': 'error', 'message': 'Could not fetch weather'}), 500
        
    return jsonify({
        'status': 'success',
        'data': weather.to_dict()
    }), 200

@weather_bp.route('/subscribe', methods=['POST'])
@token_required
def subscribe(current_user):
    data = request.get_json()
    if not data or 'crop_name' not in data or 'location' not in data:
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400
        
    sub = WeatherService.subscribe_user(
        user_id=current_user.id,
        crop_name=data['crop_name'],
        location=data['location'],
        soil_type=data.get('soil_type'),
        sowing_date=data.get('sowing_date')
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Subscribed to automated advisories'
    }), 201
