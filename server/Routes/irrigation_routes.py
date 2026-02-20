# Location: /routes/irrigation_routes.py
from flask import Blueprint, request, jsonify

irrigation_bp = Blueprint('irrigation', __name__)

@irrigation_bp.route('/api/irrigation-schedule', methods=['POST'])
def get_schedule():
    data = request.json
    crop = data.get('crop')
    temp = int(data.get('temp'))
    
    # Logic: More temp + Sandy soil = More water
    base_water = 5 if crop == 'wheat' else 10
    if temp > 35: base_water += 3
    
    schedule = []
    for i in range(1, 8):
        # Alternate days for rice, daily for wheat in heat
        action = "Water Morning" if (i % 2 != 0 or temp > 30) else "Skip"
        schedule.append({
            "day": i,
            "water": base_water if action != "Skip" else 0,
            "action": action
        })
    
    return jsonify({"schedule": schedule})