from flask import Blueprint, render_template, request, current_app, abort
import sys
import os

# Add the current directory to the path to import the local utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_keras_model, predict_image_keras

import uuid
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
disease_bp = Blueprint('disease', __name__, template_folder='templates', static_folder='static', url_prefix='/disease')

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load the PyTorch model once - Fixed path to model subdirectory
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model.pkl')  # Changed from rf_model.pkl to model.pkl
try:
    model = load_keras_model(MODEL_PATH)  # This now loads PyTorch model
    model_loaded = True
    print(f"PyTorch model loaded successfully from {MODEL_PATH}")
except FileNotFoundError:
    print(f"Warning: PyTorch model file not found at {MODEL_PATH}")
    print("Disease prediction functionality will be limited.")
    print("Please ensure you have a PyTorch model file named 'model.pkl' in the disease_prediction/model/ directory.")
    model = None
    model_loaded = False
except Exception as e: # Added a general exception for model loading issues
    print(f"Error loading PyTorch model: {e}")
    print("Disease prediction functionality will be limited.")
    model = None
    model_loaded = False

@disease_bp.route('/')
def index():
    print("Disease Prediction route accessed - rendering index.html")
    return render_template('index.html')

@disease_bp.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return render_template('error.html', message='No file uploaded.'), 400
    file = request.files['file']
    if file.filename == '':
        return render_template('error.html', message='No selected file.'), 400
    if not allowed_file(file.filename):
        return render_template('error.html', message='Invalid file type.'), 415

    # Generate a unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)

    try:
        if not model_loaded:
            return render_template('error.html', 
                                 message='Disease prediction model is not available. Please ensure the model.pkl file is present in the Disease prediction directory.'), 503
        predicted_class, description = predict_image_keras(model, filepath)
    except Exception as e:
        return render_template('error.html', message=f'Prediction error: {e}'), 500

    return render_template('result.html',
                           prediction=predicted_class,
                           description=description,
                           image_path=filepath) 