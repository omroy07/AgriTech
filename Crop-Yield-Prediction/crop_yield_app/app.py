from flask import Flask, render_template, request
import joblib
import numpy as np
import os

app = Flask(__name__)

# Load model and encoders
model = joblib.load('models/xgb_crop_model.pkl')
crop_encoder = joblib.load('models/Crop_encoder.pkl')
season_encoder = joblib.load('models/Season_encoder.pkl')
state_encoder = joblib.load('models/State_encoder.pkl')

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    if request.method == 'POST':
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
            prediction = f"Input error: {ve}"
        except Exception as e:
            prediction = f"Unexpected error: {e}"

    return render_template('index.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True, port=5502)
