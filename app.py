from flask import Flask, request, jsonify, send_from_directory, g, render_template
import google.generativeai as genai
import traceback
import os
import re
import hashlib
import json
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from marshmallow import ValidationError
from backend.utils.validation import validate_input, sanitize_input
from backend.extensions import socketio, db, migrate, mail, limiter, babel, get_locale
from backend.api.v1.files import files_bp
from backend.api.ingestion import ingestion_bp
from backend.middleware.audit import AuditMiddleware
from crop_recommendation.routes import crop_bp
# from disease_prediction.routes import disease_bp
from spatial_analytics.routes import spatial_bp
from backend.extensions.cache import cache
from backend.monitoring.routes import health_bp
from backend.api import register_api
from backend.config import config
from backend.schemas.loan_schema import LoanRequestSchema
from backend.celery_app import celery_app, make_celery
from backend.tasks import predict_crop_task, process_loan_task
import backend.sockets.task_events  # Register socket event handlers
import backend.sockets.supply_events # Register supply chain events
from auth_utils import token_required, roles_required
import backend.sockets.forum_events # Register forum socket events
import backend.sockets.knowledge_events # Register knowledge exchange events
import backend.sockets.alert_socket # Register centralized alert socket events
from backend.utils.i18n import t

from routes.irrigation_routes import irrigation_bp
app.register_blueprint(irrigation_bp)

from server.Routes.rotation_routes import rotation_bp


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
app.register_blueprint(rotation_bp) 

# Load Configuration
env_name = os.getenv('FLASK_ENV', 'default')
app.config.from_object(config[env_name])

# Set upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)
limiter.init_app(app)


# Initialize Celery with app context
celery = make_celery(app)

# Initialize Audit Middleware
audit_mw = AuditMiddleware(app)

# Import models after db initialization
from backend.models import User

CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

app.register_blueprint(crop_bp, url_prefix='/crop')
# app.register_blueprint(disease_bp)
app.register_blueprint(health_bp)
app.register_blueprint(files_bp)
app.register_blueprint(spatial_bp)
app.register_blueprint(ingestion_bp, url_prefix='/api/v1')

# Register API v1 (including loan, weather, schemes, etc.)
register_api(app)

# Initialize SocketIO with app
socketio.init_app(app)

# Initialize Cache with app
cache.init_app(app)


# Initialize Babel with app
babel.init_app(app, locale_selector=get_locale)





# Initialize Marshmallow Schemas
loan_schema = LoanRequestSchema()

with app.app_context():
    db.create_all()

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
@token_required
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
@token_required
@roles_required('farmer', 'admin', 'consultant')
def predict_crop_async():
    """Submit crop prediction as async task."""
    try:
        data = request.get_json(force=True)
        
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
        
        # Get current locale
        lang = get_locale()
        
        # Submit task to Celery
        user_id = data.get('user_id')
        task = predict_crop_task.delay(
            data['N'], data['P'], data['K'],
            data['temperature'], data['humidity'],
            data['ph'], data['rainfall'],
            user_id=user_id,
            lang=lang
        )
        
        return jsonify({
            'status': 'submitted',
            'task_id': task.id,
            'message': 'Task submitted successfully. Poll /api/task/<task_id> for results.'
        }), 202
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/loan/process-async', methods=['POST'])
@token_required
@roles_required('farmer', 'admin')
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
        
        # Get current locale
        lang = get_locale()
        
        # Submit task to Celery
        user_id = json_data.get('user_id')
        task = process_loan_task.delay(json_data, user_id=user_id, lang=lang)
        
        return jsonify({
            'status': 'submitted',
            'task_id': task.id,
            'message': 'Task submitted successfully. Poll /api/task/<task_id> for results.'
        }), 202
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/process-loan', methods=['POST'])
@limiter.limit("5 per minute")
@token_required
@roles_required('farmer', 'admin')
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

        from backend.utils.i18n import get_locale, t, LOCALE_TO_NAME
        locale = get_locale()
        target_language = LOCALE_TO_NAME.get(locale, 'English')

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

IMPORTANT: You must provide your entire response in {target_language}.

Your task is to:
1. Identify the loan type and understand which fields are important for assessing that particular loan.
2. Analyze the farmer's provided details and assess their loan eligibility.
3. Highlight areas of strength and areas where the farmer may face challenges.
4. If any critical data is missing from the JSON, point it out clearly.
5. Provide simple and actionable suggestions the farmer can follow to improve eligibility.
6. Suggest the government schemes or subsidies applicable to their loan type.
7. Ensure the tone is clear, supportive, and easy to understand for farmers.
8. Respond in a structured format with labeled sections (in {target_language}): Loan Type, Eligibility Status, Loan Range, Improvements, Schemes.
9. **IMPORTANT: Return your response in **Markdown format** with:
Headings for each section (Loan Type, Eligibility Status, Loan Range, Improvements, Schemes)
Bullet points ( - ) for lists.
Do not use "\\n" for newlines. Instead, structure properly.

Do not add assumptions that are not supported by the data provided.
"""

        # Create a cache key based on the prompt
        cache_key = f"gemini_loan_{hashlib.md5(prompt.encode()).hexdigest()}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info("Serving loan processing from cache")
            return jsonify({
                "status": "success",
                "message": "Loan processed successfully (cached)",
                "result": cached_response
            }), 200

        response = model.generate_content(prompt)
        reply = response.text

        
        if not response.candidates:
            return jsonify({
                "status": "error",
                "message": "No response generated from Gemini API"
          }), 500

        reply = response.candidates[0].content.parts[0].text
        
        # Cache the result for 24 hours (86400 seconds)
        cache.set(cache_key, reply, timeout=86400)
        
        return jsonify({
            "status": "success",
            "message": "Loan processed successfully",
            "result": reply
        }), 200

    except Exception:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "Failed to process loan request. Please try again later."
        }), 500


@app.route('/generate-loan-report', methods=['POST'])
def generate_loan_report_endpoint():
    """
    Generate and send loan report via email (async)
    Request body should contain:
    - farmer_data: Application data
    - assessment_result: AI assessment text
    - email: Farmer's email
    - name: Farmer's name (optional)
    - send_email: Boolean to control email sending (default: True)
    """
    try:
        data = request.get_json(force=True)
        
        # Validate required fields
        if not data.get('farmer_data'):
            return jsonify({
                "status": "error",
                "message": "farmer_data is required"
            }), 400
        
        if not data.get('assessment_result'):
            return jsonify({
                "status": "error",
                "message": "assessment_result is required"
            }), 400
        
        if not data.get('email'):
            return jsonify({
                "status": "error",
                "message": "email is required"
            }), 400
        
        farmer_data = data['farmer_data']
        assessment_result = data['assessment_result']
        farmer_email = data['email']
        farmer_name = data.get('name', farmer_data.get('name', 'Valued Farmer'))
        send_email = data.get('send_email', True)
        
        if send_email:
            # Trigger async task to generate and send report
            task = generate_and_send_report.delay(
                farmer_data=farmer_data,
                assessment_result=assessment_result,
                farmer_email=farmer_email,
                farmer_name=farmer_name
            )
            
            return jsonify({
                "status": "success",
                "message": f"Report generation started. Email will be sent to {farmer_email}",
                "task_id": task.id
            }), 202  # 202 Accepted - processing async
        else:
            # Generate PDF only (sync)
            try:
                pdf_path = generate_loan_report(farmer_data, assessment_result, farmer_email)
                return jsonify({
                    "status": "success",
                    "message": "Report generated successfully",
                    "pdf_path": pdf_path,
                    "download_url": f"/download-report/{os.path.basename(pdf_path)}"
                }), 200
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Failed to generate report: {str(e)}"
                }), 500
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Failed to process report request: {str(e)}"
        }), 500


@app.route('/download-report/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated PDF report"""
    try:
        reports_dir = 'reports'
        return send_from_directory(reports_dir, filename, as_attachment=True)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Report not found"
        }), 404


@app.route('/task-status/<task_id>', methods=['GET'])
def get_task_status_public(task_id):
    """Check status of async task"""
    try:
        from backend.config.celery_config import celery_app
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Task is waiting to be processed'
            }
        elif task.state == 'STARTED':
            response = {
                'status': 'processing',
                'message': 'Task is being processed'
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'completed',
                'message': 'Task completed successfully',
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
                'message': 'Task status unknown'
            }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get task status: {str(e)}"
        }), 500


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

@app.route('/reset-password/<token>')
def reset_password_page(token):
    return send_from_directory('.', 'reset-password.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)


if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, port=5000, debug=True)

#Global Error Handling 
@app.errorhandler(404)
def not_found(error):
    logger.warning("404 Error: %s", request.path)
    return jsonify({
        "status" : "error",
        "message" : t('error_user_not_found') # Using User Not Found as generic for 404 in this context
    }),404

@app.errorhandler(500)
def internal_error(error):
    logger.error("500 Error: %s", str(error), exc_info=True)
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


@app.route('/rotation')
def rotation_page():
    return render_template('crop_rotation.html')

if __name__ == '__main__':
    app.run(debug=True)
