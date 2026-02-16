import os
import json
import re
from functools import wraps
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai

# Try to import auth utilities (assuming these exist in your project)
try:
    from auth_utils import token_required, roles_required
except ImportError:
    # Fallback decorators for testing if auth_utils is missing
    def token_required(f): return f
    def roles_required(*roles): 
        def decorator(f): return f
        return decorator

app = Flask(__name__)
CORS(app)

# 💡 OPTIMIZATION: Use environment variables for API keys for security
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyC4MuJYakQd4T-T74c6kfZ9KBpZNzukJ8Q")

# --- INITIALIZE AI ---
try:
    genai.configure(api_key=API_KEY)
    # 💡 OPTIMIZATION: Set generation_config to ensure JSON output
    genai_model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    print("✅ Google AI Model initialized with JSON mode.")
except Exception as e:
    print(f"❌ AI Init Error: {e}")
    genai_model = None

# --- HELPERS & VALIDATION ---

def sanitize_input(text, max_length=255):
    """Sanitize and trim text input."""
    if not isinstance(text, str): return ""
    cleaned = re.sub(r'[<>"\']', '', text.strip())
    return cleaned[:max_length]

def validate_payload(required_fields):
    """Decorator to validate JSON keys in request.get_json()['data']."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload = request.get_json()
            if not payload or 'data' not in payload:
                return jsonify({'error': True, 'message': 'Missing "data" key in JSON'}), 400
            
            data = payload['data']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return jsonify({'error': True, 'message': f'Field "{field}" is required'}), 400
                if len(str(data[field])) > 150:
                    return jsonify({'error': True, 'message': f'Field "{field}" is too long'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_ai_prediction(user_data):
    """Query Gemini and return a structured agricultural guide."""
    if not genai_model:
        return {"error": "AI model not configured"}

    # Sanitize dictionary values
    clean_data = {k: sanitize_input(v, 100) for k, v in user_data.items()}
    
    # 💡 OPTIMIZATION: Simplified, high-instruction prompt for JSON mode
    prompt = f"""
    Acting as a professional agricultural consultant, provide a farming plan for these conditions: {clean_data}.
    Respond ONLY in JSON format with these keys:
    "predicted_crop", "title", "how_to_plant", "fertilizer", "timeline", "ideal_rainfall", "post_harvest".
    Use '\\n' for list items in string values.
    """
    
    try:
        response = genai_model.generate_content(prompt)
        # Gemini 2.0 with JSON mode usually returns clean JSON directly
        return json.loads(response.text)
    except Exception as e:
        app.logger.error(f"Gemini Error: {e}")
        return {"error": "Failed to generate guide"}

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('cropplan.html')

@app.route('/predict', methods=['POST'])
@token_required
@roles_required('farmer', 'admin')
@validate_payload(['season', 'soil_type', 'climate', 'water_availability'])
def predict():
    try:
        user_input_data = request.get_json()['data']
        
        # Get result from AI
        ai_data = get_ai_prediction(user_input_data)
        
        if "error" in ai_data:
            return jsonify({'error': True, 'message': ai_data['error'], 'code': 500}), 500

        return jsonify({
            'error': False,
            'crop': ai_data.get('predicted_crop', 'Unknown'),
            'guide_json': ai_data, # Return the object directly rather than a string
            'code': 200
        })

    except Exception as e:
        app.logger.error(f"Prediction Crash: {str(e)}")
        return jsonify({'error': True, 'message': 'Internal processing error', 'code': 500}), 500

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def handle_404(e):
    return jsonify({'error': True, 'message': 'Endpoint not found', 'code': 404}), 404

@app.errorhandler(500)
def handle_500(e):
    return jsonify({'error': True, 'message': 'Internal server error', 'code': 500}), 500

if __name__ == '__main__':
    app.run(port=5003, debug=True)
    