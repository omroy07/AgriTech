from flask import Blueprint, render_template, request, current_app, abort
from utils import load_keras_model, predict_image_keras
import os
import uuid
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
disease_bp = Blueprint('disease', __name__, template_folder='template', static_folder='static', url_prefix='/disease')

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load the Keras model once
MODEL_PATH = os.path.join(BASE_DIR, 'model.h5')
model = load_keras_model(MODEL_PATH)

@disease_bp.route('/')
def index():
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
        predicted_class, description = predict_image_keras(model, filepath)
    except Exception as e:
        return render_template('error.html', message=f'Prediction error: {e}'), 500

    return render_template('result.html',
                           prediction=predicted_class,
                           description=description,
                           image_path=filepath) 