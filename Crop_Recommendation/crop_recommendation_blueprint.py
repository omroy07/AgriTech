from flask import Blueprint, render_template, request
import joblib
import numpy as np

crop_recommendation_bp = Blueprint('crop_recommendation', __name__, template_folder='templates', static_folder='static', url_prefix='/crop-recommendation')

model = joblib.load('model/rf_model.pkl')
label_encoder = joblib.load('model/label_encoder.pkl')

@crop_recommendation_bp.route('/')
def home():
    return render_template('index.html')

@crop_recommendation_bp.route('/predict', methods=['POST'])
def predict():
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