from flask import Blueprint, render_template, request, render_template_string
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

@crop_yield_bp.route('/')
def home():
    print("Crop Yield route accessed - rendering Crop Yield page")
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crop Yield Prediction | AgriTech</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
                margin: 0;
            }
            .container {
                max-width: 500px;
                margin: 40px auto 0 auto;
                background: #fff;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.10);
                padding: 36px 32px 32px 32px;
            }
            .header {
                text-align: center;
                margin-bottom: 24px;
            }
            .header h1 {
                font-size: 2.2rem;
                color: #667eea;
                margin-bottom: 10px;
                font-weight: 700;
            }
            .header p {
                color: #555;
                font-size: 1.1rem;
            }
            form {
                display: flex;
                flex-direction: column;
                gap: 18px;
            }
            .input-group {
                display: flex;
                align-items: center;
                gap: 12px;
                background: #f7fafc;
                border-radius: 10px;
                padding: 10px 14px;
                box-shadow: 0 2px 8px rgba(102,126,234,0.04);
            }
            .input-group i {
                color: #667eea;
                font-size: 1.2rem;
                min-width: 22px;
            }
            label {
                font-weight: 600;
                color: #667eea;
                font-size: 1rem;
                min-width: 120px;
            }
            input[type="number"], input[type="text"] {
                flex: 1;
                padding: 10px 12px;
                border: 1px solid #b2bec3;
                border-radius: 8px;
                font-size: 1rem;
                outline: none;
                background: #fff;
                transition: border 0.2s;
            }
            input[type="number"]:focus, input[type="text"]:focus {
                border: 1.5px solid #667eea;
            }
            button {
                margin-top: 10px;
                padding: 14px 0;
                background: linear-gradient(90deg, #667eea, #764ba2);
                color: #fff;
                border: none;
                border-radius: 10px;
                font-size: 1.15rem;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 4px 16px rgba(102,126,234,0.13);
                transition: background 0.2s, transform 0.2s;
                letter-spacing: 1px;
            }
            button:hover {
                background: linear-gradient(90deg, #764ba2, #667eea);
                transform: translateY(-2px) scale(1.03);
            }
            .how-it-works {
                background: rgba(102,126,234,0.08);
                border-radius: 16px;
                margin-top: 36px;
                padding: 24px 18px;
            }
            .how-it-works h2 {
                color: #764ba2;
                font-size: 1.2rem;
                margin-bottom: 16px;
                text-align: center;
                font-weight: 700;
            }
            .how-it-works ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            .how-it-works li {
                margin-bottom: 10px;
                padding-left: 22px;
                position: relative;
                color: #444;
                font-size: 1rem;
            }
            .how-it-works li:before {
                content: '\\2714';
                position: absolute;
                left: 0;
                color: #43cea2;
                font-weight: bold;
            }
            .footer {
                text-align: center;
                color: #888;
                margin-top: 32px;
                font-size: 0.98rem;
                opacity: 0.85;
            }
            @media (max-width: 600px) {
                .container {
                    padding: 18px 6px 14px 6px;
                }
                .header h1 {
                    font-size: 1.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-chart-line"></i> Crop Yield Prediction</h1>
                <p>Predict expected crop yields using machine learning models trained on historical agricultural data.</p>
            </div>
            <form method="post" action="/crop-yield/predict">
                <div class="input-group">
                    <i class="fas fa-ruler-combined"></i>
                    <label for="area">Area (hectares)</label>
                    <input type="number" step="any" name="area" id="area" required placeholder="e.g. 2.5">
                </div>
                <div class="input-group">
                    <i class="fas fa-seedling"></i>
                    <label for="crop">Crop Name</label>
                    <input type="text" name="crop" id="crop" required placeholder="e.g. wheat">
                </div>
                <div class="input-group">
                    <i class="fas fa-cloud-rain"></i>
                    <label for="rainfall">Rainfall (mm)</label>
                    <input type="number" step="any" name="rainfall" id="rainfall" required placeholder="e.g. 200">
                </div>
                <div class="input-group">
                    <i class="fas fa-flask"></i>
                    <label for="fertilizer">Fertilizer Used (kg)</label>
                    <input type="number" step="any" name="fertilizer" id="fertilizer" required placeholder="e.g. 50">
                </div>
                <button type="submit"><i class="fas fa-calculator"></i> Predict Yield</button>
            </form>
            <div class="how-it-works">
                <h2>How It Works</h2>
                <ul>
                    <li>Input your field area, crop name, rainfall, and fertilizer usage</li>
                    <li>Our AI model analyzes your data</li>
                    <li>Receive crop yield predictions instantly</li>
                </ul>
            </div>
        </div>
        <div class="footer">
            &copy; 2024 AgriTech - Crop Yield Prediction
        </div>
    </body>
    </html>
    ''')

@crop_yield_bp.route('/predict', methods=['POST'])
def predict():
    # Example: Collect form data (adjust field names/types as per your form/model)
    try:
        area = float(request.form['area'])
        crop = request.form['crop']
        rainfall = float(request.form['rainfall'])
        fertilizer = float(request.form['fertilizer'])
        # TODO: Add your model prediction logic here
        # For demonstration, we'll just echo the input and show a fake yield
        predicted_yield = round(area * 2.5 + rainfall * 0.1 + fertilizer * 0.2, 2)
        return render_template_string(f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Crop Yield Prediction Result | AgriTech</title>
                <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
                <style>
                    body {{
                        background: linear-gradient(135deg, #fffbe7 0%, #ffd200 100%);
                        font-family: 'Montserrat', Arial, sans-serif;
                        min-height: 100vh;
                        margin: 0;
                        color: #222;
                    }}
                    .navbar {{
                        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                        padding: 0 32px;
                        height: 60px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        box-shadow: 0 2px 12px rgba(102,126,234,0.08);
                    }}
                    .navbar .brand {{
                        color: #fff;
                        font-size: 1.4rem;
                        font-weight: 700;
                        letter-spacing: 1px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        text-decoration: none;
                    }}
                    .navbar .nav-links {{
                        display: flex;
                        gap: 24px;
                    }}
                    .navbar .nav-links a {{
                        color: #fff;
                        text-decoration: none;
                        font-weight: 500;
                        font-size: 1rem;
                        transition: color 0.2s;
                    }}
                    .navbar .nav-links a:hover {{
                        color: #ffd700;
                    }}
                    .result-container {{
                        max-width: 420px;
                        margin: 80px auto;
                        background: #fff;
                        border-radius: 18px;
                        box-shadow: 0 8px 32px rgba(247,151,30,0.18);
                        padding: 36px 32px 32px 32px;
                        text-align: center;
                    }}
                    .result-container h2 {{
                        color: #f7971e;
                        font-size: 2rem;
                        margin-bottom: 18px;
                    }}
                    .result-container .icon {{
                        font-size: 3rem;
                        color: #ffd200;
                        margin-bottom: 16px;
                    }}
                    .result-container .yield {{
                        font-size: 1.5rem;
                        color: #f7971e;
                        font-weight: 700;
                        margin-bottom: 12px;
                    }}
                    .back-btn {{
                        display: inline-block;
                        margin-top: 24px;
                        padding: 10px 24px;
                        background: linear-gradient(90deg, #f7971e, #ffd200);
                        color: #fff;
                        border: none;
                        border-radius: 8px;
                        font-size: 1rem;
                        font-weight: 600;
                        text-decoration: none;
                        transition: background 0.2s;
                    }}
                    .back-btn:hover {{
                        background: linear-gradient(90deg, #ffd200, #f7971e);
                    }}
                    @media (max-width: 600px) {{
                        .navbar {{
                            flex-direction: column;
                            height: auto;
                            padding: 12px 8px;
                        }}
                        .navbar .nav-links {{
                            gap: 12px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <nav class="navbar">
                    <a href="/" class="brand"><i class="fas fa-seedling"></i> AgriTech</a>
                    <div class="nav-links">
                        <a href="/disease/"><i class="fas fa-bug"></i> Disease Prediction</a>
                        <a href="/crop-recommendation/"><i class="fas fa-leaf"></i> Crop Recommendation</a>
                        <a href="/crop-yield/"><i class="fas fa-chart-line"></i> Crop Yield</a>
                    </div>
                </nav>
                <div class="result-container">
                    <div class="icon"><i class="fas fa-chart-line"></i></div>
                    <h2>Predicted Yield</h2>
                    <div class="yield">{predicted_yield} tons</div>
                    <div style="margin-bottom:10px;color:#444;">
                        <b>Crop:</b> {crop}<br>
                        <b>Area:</b> {area} ha<br>
                        <b>Rainfall:</b> {rainfall} mm<br>
                        <b>Fertilizer:</b> {fertilizer} kg
                    </div>
                    <a href="/crop-yield/" class="back-btn"><i class="fas fa-arrow-left"></i> Try Again</a>
                </div>
            </body>
            </html>
        ''')
    except Exception as e:
        return render_template_string(f'''
            <h2>Error</h2>
            <p>{e}</p>
            <a href="/crop-yield/">Back</a>
        '''), 500