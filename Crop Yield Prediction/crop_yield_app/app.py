
from flask import Flask, render_template, request, jsonify
import numpy as np
import re
from functools import wraps

app = Flask(__name__)

# Mock model and encoders for testing
class MockEncoder:
    def __init__(self, classes):
        self.classes_ = classes

    def transform(self, values):
        return [self.classes_.tolist().index(val) if val in self.classes_ else 0 for val in values]

# Mock data
crop_encoder = MockEncoder(np.array(["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Soybean", "Groundnut", "Barley", "Ragi", "Jowar"]))
season_encoder = MockEncoder(np.array(["Kharif", "Rabi", "Summer", "Whole Year"]))
state_encoder = MockEncoder(np.array(["Andhra Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Punjab", "Haryana", "Gujarat", "Rajasthan", "Madhya Pradesh"]))

def mock_predict(features):
    """Mock prediction function that returns a random yield value"""
    # Simulate processing time
    time.sleep(2)
    # Return a mock prediction between 10-100 hg/ha
    return np.random.uniform(10, 100, size=(len(features),))

model = type('MockModel', (), {'predict': mock_predict})()

# Input validation helper functions
def validate_required_fields(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
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

def validate_year(year):
    """Validate year input"""
    try:
        year_int = int(year)
        if year_int < 1900 or year_int > 2100:
            raise ValueError("Year must be between 1900 and 2100")
        return year_int
    except ValueError as e:
        raise ValueError(f"Invalid year: {str(e)}")

@app.route('/')
def index():
    return render_template('input.html')

@validate_required_fields(['crop', 'year', 'season', 'state', 'area', 'production', 'rainfall'])
def predict():
    try:
        form = request.form

        # Sanitize and validate all inputs
        crop = sanitize_input(form['crop'], 50)
        year = validate_year(form['year'])
        season = sanitize_input(form['season'], 20)
        state = sanitize_input(form['state'], 50)
        area = sanitize_numeric_input(form['area'], 0, 1000000, "Area")
        production = sanitize_numeric_input(form['production'], 0, 1000000, "Production")
        rainfall = sanitize_numeric_input(form['rainfall'], 0, 10000, "Rainfall")

        # Validate against encoder classes
        if crop not in crop_encoder.classes_:
            return render_template('input.html', error=f"Unknown crop: {crop}")
        if season not in season_encoder.classes_:
            return render_template('input.html', error=f"Unknown season: {season}")
        if state not in state_encoder.classes_:
            return render_template('input.html', error=f"Unknown state: {state}")

        # Encode values
        crop_encoded = crop_encoder.transform([crop])[0]
        season_encoded = season_encoder.transform([season])[0]
        state_encoded = state_encoder.transform([state])[0]

        # Prepare features
        features = np.array([[crop_encoded, year, season_encoded, state_encoded, area, rainfall, production]])

        # Predict
        prediction = float(round(model.predict(features)[0], 2))

        # Prepare data for template
        params = {
            'crop': crop,
            'year': year,
            'season': season,
            'state': state,
            'area': area,
            'production': production,
            'rainfall': rainfall,
            'temperature': 25.0,  # Default value since not in form
            'humidity': 60.0,     # Default value since not in form
            'ph': 6.5            # Default value since not in form
        }

        # Render result template with prediction data
        return render_template('index.html', crop=crop, params=params)

    except ValueError as e:
        return render_template('input.html', error=str(e))
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return render_template('input.html', error='Prediction failed')

# Global error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5502)