import time
import re
import numpy as np
from flask import Flask, render_template, request, jsonify, flash
from functools import wraps
from dataclasses import dataclass

app = Flask(__name__)
app.secret_key = "super_secret_agricultural_key" # Required for flash messages

# --- MOCK MODELS & ENCODERS ---
class MockEncoder:
    def __init__(self, classes):
        self.classes_ = np.array(classes)

    def transform(self, values):
        return [np.where(self.classes_ == val)[0][0] if val in self.classes_ else 0 for val in values]

# Initializing encoders with your data
crop_enc = MockEncoder(["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Soybean", "Groundnut", "Barley", "Ragi", "Jowar"])
season_enc = MockEncoder(["Kharif", "Rabi", "Summer", "Whole Year"])
state_enc = MockEncoder(["Andhra Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Punjab", "Haryana", "Gujarat", "Rajasthan", "Madhya Pradesh"])

class YieldModel:
    def predict(self, features):
        """Simulates an ML model inference"""
        time.sleep(0.5) # Reduced sleep for better UX
        return np.random.uniform(10, 100, size=(len(features),))

model = YieldModel()

# --- UTILITIES & VALIDATION ---

@dataclass
class PredictionParams:
    crop: str
    year: int
    season: str
    state: str
    area: float
    production: float
    rainfall: float
    temperature: float = 25.0
    humidity: float = 60.0
    ph: float = 6.5

def validate_and_sanitize(form):
    """Centralized validation logic to keep routes clean."""
    try:
        # Sanitize text
        crop = form.get('crop', '').strip()
        season = form.get('season', '').strip()
        state = form.get('state', '').strip()
        
        # Validate against encoders
        if crop not in crop_enc.classes_: raise ValueError(f"Unsupported crop: {crop}")
        if season not in season_enc.classes_: raise ValueError(f"Unsupported season: {season}")
        if state not in state_enc.classes_: raise ValueError(f"Unsupported state: {state}")

        # Sanitize and validate numbers
        def to_float(val, name, min_v=0):
            clean = re.sub(r'[^0-9.-]', '', str(val))
            f_val = float(clean)
            if f_val < min_v: raise ValueError(f"{name} cannot be negative")
            return f_val

        year = int(form.get('year', 0))
        if not (1900 <= year <= 2100): raise ValueError("Year must be between 1900-2100")

        return PredictionParams(
            crop=crop,
            year=year,
            season=season,
            state=state,
            area=to_float(form.get('area'), "Area"),
            production=to_float(form.get('production'), "Production"),
            rainfall=to_float(form.get('rainfall'), "Rainfall")
        )
    except (TypeError, ValueError) as e:
        raise ValueError(str(e))

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('input.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Validation & Sanitization
        params = validate_and_sanitize(request.form)

        # 2. Encoding
        features = np.array([[
            crop_enc.transform([params.crop])[0],
            params.year,
            season_enc.transform([params.season])[0],
            state_enc.transform([params.state])[0],
            params.area,
            params.rainfall,
            params.production
        ]])

        # 3. Inference
        prediction_raw = model.predict(features)[0]
        prediction = round(float(prediction_raw), 2)

        # 4. Success Response
        return render_template('index.html', 
                               crop=params.crop, 
                               prediction=prediction, 
                               params=params.__dict__)

    except ValueError as e:
        # User input error
        return render_template('input.html', error=str(e))
    except Exception as e:
        # System error
        app.logger.error(f"Prediction Crash: {e}")
        return render_template('input.html', error="An internal error occurred. Please try again.")

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(e):
    return render_template('input.html', error="Page not found"), 404

if __name__ == '__main__':
    # Using '0.0.0.0' makes it accessible on your local network
    app.run(debug=True, port=5502, host='0.0.0.0')
    