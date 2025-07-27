from flask import Blueprint, render_template, request
import joblib
import numpy as np
import os

crop_recommendation_bp = Blueprint('crop_recommendation', __name__, template_folder='templates', static_folder='static', url_prefix='/crop-recommendation')

# Get the absolute path to the model directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    model = joblib.load(os.path.join(BASE_DIR, 'model', 'rf_model.pkl'))
    label_encoder = joblib.load(os.path.join(BASE_DIR, 'model', 'label_encoder.pkl'))
    print("Crop Recommendation models loaded successfully")
except FileNotFoundError as e:
    print(f"Warning: Crop Recommendation model files not found: {e}")
    print("Crop Recommendation functionality will be limited.")
    model = None
    label_encoder = None

@crop_recommendation_bp.route('/')
def home():
    print("Crop Recommendation route accessed - rendering index.html")
    return render_template('index.html')

@crop_recommendation_bp.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template('error.html', message='Crop Recommendation model is not available. Please ensure the model files are present.'), 503
    try:
        data = [
            float(request.form['N']),
            float(request.form['P']),
            float(request.form['K']),
            float(request.form['temperature']),
            float(request.form['humidity']),
            float(request.form['ph']),
            float(request.form['rainfall'])
        ]
        prediction_num = model.predict([data])[0]
        prediction_label = label_encoder.inverse_transform([prediction_num])[0]
        return render_template('result.html', crop=prediction_label)
    except Exception as e:
        return render_template('error.html', message=f'Prediction error: {e}'), 500 