from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import traceback
import os
import re
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import limiter
from crop_recommendation.routes import crop_bp
from disease_prediction.routes import disease_bp
from backend.tasks import process_loan_task, predict_crop_task
from backend.celery_app import celery_app




# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

# Load Configuration
env_name = os.getenv('FLASK_ENV', 'default')
app.config.from_object(config[env_name])

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

app.register_blueprint(crop_bp)
app.register_blueprint(disease_bp)

# Initialize Cache
cache.init_app(app)




# Initialize Marshmallow Schemas
loan_schema = LoanRequestSchema()

# Initialize Gemini API
# Configure Gemini Client
genai.configure(api_key=app.config['GEMINI_API_KEY'])
model = genai.GenerativeModel(app.config['GEMINI_MODEL_ID'])



"""Secure endpoint to provide Firebase configuration to client"""
@app.route('/api/firebase-config')
@limiter.limit("10 per minute")
def get_firebase_config():
    try:
        return jsonify({
        return jsonify({
            'apikey': app.config['FIREBASE_API_KEY'],
            'authDomain': app.config['FIREBASE_AUTH_DOMAIN'],
            'projectId': app.config['FIREBASE_PROJECT_ID'],
            'storageBucket': app.config['FIREBASE_STORAGE_BUCKET'],
            'messagingSenderId': app.config['FIREBASE_MESSAGING_SENDER_ID'],
            'appId': app.config['FIREBASE_APP_ID'],
            'measurementId': app.config['FIREBASE_MEASUREMENT_ID']

        })
    except KeyError as e:
        return jsonify({
            "status": "error",
            "message":f"Missing environment variable: {str(e)}"
        }),500


# ==================== ASYNC TASK ENDPOINTS ====================

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Check the status of an async task."""
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'status': 'pending',
            'message': 'Task is waiting to be processed'
        }
    elif task.state == 'STARTED':
        response = {
            'status': 'processing',
            'message': 'Task is currently being processed'
        }
    elif task.state == 'SUCCESS':
        response = {
            'status': 'completed',
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'status': 'failed',
            'message': str(task.info)
        }
    else:
        response = {
            'status': task.state,
            'message': 'Unknown state'
        }
    
    return jsonify(response)


@app.route('/api/crop/predict-async', methods=['POST'])
def predict_crop_async():
    """Submit crop prediction as async task."""
    try:
        data = request.get_json(force=True)
        
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
        
        # Submit task to Celery
        task = predict_crop_task.delay(
            data['N'], data['P'], data['K'],
            data['temperature'], data['humidity'],
            data['ph'], data['rainfall']
        )
        
        return jsonify({
            'status': 'submitted',
            'task_id': task.id,
            'message': 'Task submitted successfully. Poll /api/task/<task_id> for results.'
        }), 202
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/loan/process-async', methods=['POST'])
def process_loan_async():
    """Submit loan processing as async task."""
    try:
        json_data = request.get_json(force=True)
        
        is_valid, validation_message = validate_input(json_data)
        if not is_valid:
            return jsonify({'status': 'error', 'message': validation_message}), 400
        
        # Sanitize input
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    json_data[key] = sanitize_input(value)
        
        # Submit task to Celery
        task = process_loan_task.delay(json_data)
        
        return jsonify({
            'status': 'submitted',
            'task_id': task.id,
            'message': 'Task submitted successfully. Poll /api/task/<task_id> for results.'
        }), 202
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/process-loan', methods=['POST'])
@limiter.limit("5 per minute")
def process_loan():
    try:
        json_data = request.get_json(force=True)
        
        # Validate and sanitize input using Marshmallow
        try:
            validated_data = loan_schema.load(json_data)
        except ValidationError as err:
            return jsonify({
                "status": "error",
                "message": err.messages
            }), 400
        
        # Sanitize any text fields in the JSON data
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    json_data[key] = sanitize_input(value)
        
        logger.info("Received loan processing request for type: %s", json_data.get('loan_type', 'unknown'))

        prompt = f"""
You are a financial loan eligibility advisor specializing in agricultural loans for farmers in India.

You will be given a JSON object that contains information about a farmer's loan application. The fields in this JSON will vary depending on the loan type (e.g., Crop Cultivation, Farm Equipment, Water Resources, Land Purchase).
You will focus only on loan schemes and eligibility criteria followed by:
1. Indian nationalized banks (e.g., SBI, Bank of Baroda)
2. Private sector Indian banks (e.g., ICICI, HDFC)
3. Regional Rural Banks (RRBs)
4. Cooperative Banks
5. NABARD & government schemes
Do not suggest generic or international financing options.

JSON Data = {json_data}

Your task is to:
1. Identify the loan type and understand which fields are important for assessing that particular loan.
2. Analyze the farmer's provided details and assess their loan eligibility.
3. Highlight areas of strength and areas where the farmer may face challenges.
4. If any critical data is missing from the JSON, point it out clearly.
5. Provide simple and actionable suggestions the farmer can follow to improve eligibility.
6. Suggest the government schemes or subsidies applicable to their loan type.
7. Ensure the tone is clear, supportive, and easy to understand for farmers.
8. Respond in a structured format with labeled sections: Loan Type, Eligibility Status, Loan Range, Improvements, Schemes.
9. **IMPORTANT: Return your response in **Markdown format** with:
Headings for each section (Loan Type, Eligibility Status, Loan Range, Improvements, Schemes)
Bullet points ( - ) for lists.
Do not use "\\n" for newlines. Instead, structure properly.

Do not add assumptions that are not supported by the data provided.
"""

        response = model.generate_content(prompt)
        reply = response.text

        
        if not response.candidates:
            return jsonify({
                "status": "error",
                "message": "No response generated from Gemini API"
          }), 500

        reply = response.candidates[0].content.parts[0].text
        return jsonify({
            "status": "success",
            "message": "Loan processes successfully "
            }), 200

    except Exception as e:
        logger.error("Error processing loan request: %s", str(e), exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Failed to process loan request. Please try again later."}), 500


# Serve HTML pages
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/farmer')
def farmer():
    return send_from_directory('.', 'farmer.html')

@app.route('/shopkeeper')
def shopkeeper():
    return send_from_directory('.', 'shopkeeper.html')

@app.route('/main')
def main():
    return send_from_directory('.', 'main.html')

@app.route('/about')
def about():
    return send_from_directory('.', 'about.html')

@app.route('/blog')
def blog():
    return send_from_directory('.', 'blog.html')

@app.route('/contact')
def contact():
    return send_from_directory('.', 'contact.html')

@app.route('/chat')
@limiter.limit("10 per minute")
def chat():
    return send_from_directory('.', 'chat.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)


if __name__ == '__main__':
    app.run(port=5000, debug=True)

#Global Error Handling 
@app.errorhandler(404)
def not_found(error):
    logger.warning("404 Error: %s", request.path)
    return jsonify({
        "status" : "error",
        "message" :"Resource not found"
    }),404

@app.errorhandler(500)
def internal_error(error):
    logger.error("500 Error: %s", str(error), exc_info=True)
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


