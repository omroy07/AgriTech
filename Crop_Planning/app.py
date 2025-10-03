# app.py
from flask import Flask, request, jsonify, render_template
from auth_utils import token_required, roles_required
import google.generativeai as genai
import json
from flask_cors import CORS
import re
from functools import wraps

app = Flask(__name__)
CORS(app)

API_KEY = "AIzaSyC4MuJYakQd4T-T74c6kfZ9KBpZNzukJ8Q"

# Input validation helper functions
def sanitize_input(text, max_length=255):
    """Sanitize text input"""
    if not isinstance(text, str):
        return ""
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\']', '', text.strip())
    return cleaned[:max_length]

def validate_required_fields(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            json_data = request.get_json()
            if not json_data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            for field in required_fields:
                if field not in json_data or not json_data[field].strip():
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_user_data(data):
    """Validate user input data"""
    required_fields = ['season', 'soil_type', 'climate', 'water_availability']
    for field in required_fields:
        if field not in data or not data[field].strip():
            return False, f"Missing required field: {field}"
    
    # Validate field lengths
    for field, value in data.items():
        if len(value) > 100:
            return False, f"{field} too long (max 100 characters)"
    
    return True, "Valid"

try:
    genai.configure(api_key=API_KEY)
    genai_model = genai.GenerativeModel('gemini-2.0-flash')
    print("Google AI Model initialized successfully.")
except Exception as e:
    print(f"Error initializing Google AI Model: {e}")
    genai_model = None

def clean_ai_response(text_response):
    start = text_response.find('{')
    end = text_response.rfind('}')
    if start != -1 and end != -1:
        return text_response[start:end+1]
    return text_response

def get_ai_prediction_and_guide(user_data):
    if not genai_model:
        return json.dumps({"error": "AI model is not configured."})

    # Sanitize user data before sending to AI
    sanitized_data = {k: sanitize_input(v, 100) for k, v in user_data.items()}
    conditions = ", ".join([f"{key.replace('_', ' ')}: {value}" for key, value in sanitized_data.items()])

    # FINAL, MOST STRICT PROMPT
    prompt = f"""
    You are a JSON API that provides agricultural advice.
    Your entire response MUST be a single, valid JSON object and nothing else.
    
    Analyze these farming conditions: {conditions}
    
    1.  Determine the single best crop that is appropriate for the "Season" provided.
    2.  Generate a farming guide for that crop. **IMPORTANT: For any lists or steps, use the newline character `\\n` to separate items.**
    
    Return a single JSON object with these exact keys: 
    "predicted_crop", "title", "how_to_plant", "fertilizer", "timeline", "ideal_rainfall", "post_harvest".
    """
    
    try:
        response = genai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content from Gemini: {e}")
        return json.dumps({"error": "Failed to generate AI guide."})

@app.route('/')
def home():
    return render_template('cropplan.html')

@app.route('/predict', methods=['POST'])
@token_required
@roles_required('farmer', 'admin')
@validate_required_fields(['data'])
def predict():
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        json_data = request.get_json()
        user_input_data = json_data['data']
        
        # Validate user data
        is_valid, message = validate_user_data(user_input_data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Sanitize user data
        sanitized_data = {k: sanitize_input(v, 100) for k, v in user_input_data.items()}
        
        raw_ai_response = get_ai_prediction_and_guide(sanitized_data)
        cleaned_json_string = clean_ai_response(raw_ai_response)

        try:
            ai_response_data = json.loads(cleaned_json_string)
            return jsonify({
                'crop': ai_response_data.get('predicted_crop', 'Unknown'),
                'guide_json_string': cleaned_json_string
            })
        except json.JSONDecodeError:
            return jsonify({'error': 'The AI returned an invalid response. Please try again.'}), 500

    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

# Global error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=5003, debug=True)