from flask import Blueprint, render_template, request
import joblib
import numpy as np
import os

crop_yield_bp = Blueprint('crop_yield', __name__, template_folder='templates', static_folder='static', url_prefix='/crop-yield')

# Load model and encoders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    model = joblib.load(os.path.join(BASE_DIR, 'models', 'xgb_crop_model.pkl'))
    crop_encoder = joblib.load(os.path.join(BASE_DIR, 'models', 'Crop_encoder.pkl'))
    season_encoder = joblib.load(os.path.join(BASE_DIR, 'models', 'Season_encoder.pkl'))
    state_encoder = joblib.load(os.path.join(BASE_DIR, 'models', 'State_encoder.pkl'))
    print("Crop Yield models loaded successfully")
except FileNotFoundError as e:
    print(f"Warning: Model files not found: {e}")
    print("Crop Yield prediction functionality will be limited.")
    model = None
    crop_encoder = None
    season_encoder = None
    state_encoder = None

@crop_yield_bp.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    if request.method == 'POST':
        if model is None:
            return render_template('error.html', message='Crop Yield prediction model is not available. Please ensure the model files are present.'), 503
        try:
            # Get form inputs
            crop = request.form['crop']
            year = int(request.form['year'])
            season = request.form['season']
            state = request.form['state']
            area = float(request.form['area'])
            production = float(request.form['production'])
            rainfall = float(request.form['rainfall'])

            # Encode inputs with error handling
            if crop not in crop_encoder.classes_:
                raise ValueError(f"Unknown crop: {crop}")
            if season not in season_encoder.classes_:
                raise ValueError(f"Unknown season: {season}")
            if state not in state_encoder.classes_:
                raise ValueError(f"Unknown state: {state}")

            crop_encoded = crop_encoder.transform([crop])[0]
            season_encoded = season_encoder.transform([season])[0]
            state_encoded = state_encoder.transform([state])[0]

            # Form feature array
            features = np.array([[crop_encoded, year, season_encoded, state_encoded, area, rainfall, production]])

            # Make prediction
            prediction = model.predict(features)[0]

        except ValueError as ve:
            return render_template('error.html', message=f'Input error: {ve}'), 400
        except Exception as e:
            return render_template('error.html', message=f'Unexpected error: {e}'), 500

    return render_template('index.html', prediction=prediction) 