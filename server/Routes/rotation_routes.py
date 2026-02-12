from flask import Blueprint, request, jsonify
from server.Utils.soil_analysis_logic import SoilRecoveryEngine
import json
import os

rotation_bp = Blueprint('rotation', __name__)

# Correctly locate the JSON database relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'models', 'crop_database.json')

def load_crop_data():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

@rotation_bp.route('/api/analyze-rotation', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        soil = data.get('soil_status')
        crop = data.get('selected_crop')
        
        # Initialize engine with fresh data
        engine = SoilRecoveryEngine(load_crop_data())
        
        analysis = engine.calculate_soil_impact(soil, crop)
        suggestion = engine.suggest_recovery_crop(analysis) if analysis["is_depleted"] else None
        
        return jsonify({
            "status": "success",
            "analysis": analysis,
            "recommendation": suggestion
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500