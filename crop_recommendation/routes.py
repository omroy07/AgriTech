import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from flask import Blueprint, render_template, request, send_file, jsonify
from auth_utils import token_required, roles_required
import joblib
import numpy as np
import re
from functools import wraps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime

crop_bp = Blueprint('crop', __name__, template_folder='templates', static_folder='static')

try:
    model = joblib.load('model/rf_model.pkl')
    label_encoder = joblib.load('model/label_encoder.pkl')  # Load encoder
except (FileNotFoundError, IndexError):
    model = None
    label_encoder = None
    print("Warning: Crop models not found. Prediction disabled.")

# Input validation helper functions
def validate_required_fields(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_numeric_input(value, min_val=None, max_val=None, field_name=""):
    """Sanitize and validate numeric input"""
    try:
        # Remove any non-numeric characters except decimal point and minus
        cleaned = re.sub(r'[^0-9.-]', '', str(value))
        num_value = float(cleaned)
        
        if min_val is not None and num_value < min_val:
            raise ValueError(f"{field_name} must be at least {min_val}")
        if max_val is not None and num_value > max_val:
            raise ValueError(f"{field_name} must be at most {max_val}")
            
        return num_value
    except ValueError as e:
        raise ValueError(f"Invalid {field_name}: {str(e)}")

def sanitize_input(text, max_length=255):
    """Sanitize text input"""
    if not isinstance(text, str):
        return ""
    return text.strip()[:max_length]

@crop_bp.route('/')
def home():
    return render_template('index.html')

@crop_bp.route('/predict', methods=['GET', 'POST']) # Allow GET requests
def predict():
    # Handle the Page Load (GET)
    if request.method == 'GET':
        # Return the index.html which contains the form
        return render_template('index.html') 

    # Handle the Form Submission (POST)
    if request.method == 'POST':
        try:
            # Manual validation (Moved here so it doesn't block the GET request)
            required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    # Return error with the correct template
                    return render_template('index.html', error=f"Missing required field: {field}")

            # Sanitize and validate all numeric inputs
            data = [
                sanitize_numeric_input(request.form['N'], 0, 200, "Nitrogen (N)"),
                sanitize_numeric_input(request.form['P'], 0, 200, "Phosphorus (P)"),
                sanitize_numeric_input(request.form['K'], 0, 200, "Potassium (K)"),
                sanitize_numeric_input(request.form['temperature'], -50, 100, "Temperature"),
                sanitize_numeric_input(request.form['humidity'], 0, 100, "Humidity"),
                sanitize_numeric_input(request.form['ph'], 0, 14, "pH"),
                sanitize_numeric_input(request.form['rainfall'], 0, 1000, "Rainfall")
            ]
            
            input_params = {
                'N': str(data[0]),
                'P': str(data[1]),
                'K': str(data[2]),
                'temperature': str(data[3]),
                'humidity': str(data[4]),
                'ph': str(data[5]),
                'rainfall': str(data[6])
            }
            
            if model is None or label_encoder is None:
                return render_template('index.html', error="Prediction model is currently unavailable.")

            prediction_num = model.predict([data])[0]
            prediction_label = label_encoder.inverse_transform([prediction_num])[0]
            
            # Handle the Form Submission (POST)
            return render_template('result.html', crop=prediction_label, params=input_params)
            
        except ValueError as e:
            # Render the form again with the error message visible
            return render_template('index.html', error=str(e))
        except Exception as e:
            crop_bp.logger.error(f"Prediction error: {str(e)}")
            return jsonify({'error': 'Prediction failed'}), 500

# PDF download route
@crop_bp.route('/download_report', methods=['POST'])
@token_required
@roles_required('farmer', 'admin')
@validate_required_fields(['crop', 'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
def download_report():
    try:
        # Sanitize inputs
        crop = sanitize_input(request.form['crop'], 100)
        params = {
            'N': str(sanitize_numeric_input(request.form['N'], 0, 200, "Nitrogen")),
            'P': str(sanitize_numeric_input(request.form['P'], 0, 200, "Phosphorus")),
            'K': str(sanitize_numeric_input(request.form['K'], 0, 200, "Potassium")),
            'temperature': str(sanitize_numeric_input(request.form['temperature'], -50, 100, "Temperature")),
            'humidity': str(sanitize_numeric_input(request.form['humidity'], 0, 100, "Humidity")),
            'ph': str(sanitize_numeric_input(request.form['ph'], 0, 14, "pH")),
            'rainfall': str(sanitize_numeric_input(request.form['rainfall'], 0, 1000, "Rainfall"))
        }
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Logo/Header (optional)
        p.setFont('Helvetica-Bold', 18)
        p.drawString(50, height - 60, "AgriTech Crop Recommendation Report")
        
        # Date & Time
        p.setFont('Helvetica', 10)
        p.drawString(50, height - 80, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Input Parameters
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, height - 120, "Input Parameters:")
        p.setFont('Helvetica', 11)
        y = height - 140
        for k, v in params.items():
            p.drawString(70, y, f"{k}: {v}")
            y -= 18
            
        # Prediction Result
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, y - 10, "Prediction Result:")
        p.setFont('Helvetica', 13)
        p.drawString(70, y - 30, f"Recommended Crop: {crop}")
        p.showPage()
        p.save()
        buffer.seek(0)
        
        return send_file(buffer, as_attachment=True, download_name="crop_recommendation_report.pdf", mimetype='application/pdf')
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        crop_bp.logger.error(f"PDF generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF'}), 500