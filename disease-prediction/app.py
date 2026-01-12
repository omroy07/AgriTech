from flask import Flask, render_template, request, jsonify
from utils import load_keras_model, predict_image_keras
import os
import re
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = r'disease/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Security configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

# Input validation helper functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal attacks"""
    if not filename:
        return ""
    # Remove any path separators and dangerous characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    return secure_filename(cleaned)

def validate_file_size(file):
    """Validate file size"""
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        return False
    return True

# Load the Keras model
try:
    model = load_keras_model(r'disease/model.h5')
except Exception as e:
    app.logger.error(f"Failed to load model: {str(e)}")
    model = None

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP'}), 400
        
        # Validate file size
        if not validate_file_size(file):
            return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Sanitize filename
        filename = sanitize_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Create unique filename to prevent overwrites
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Check if model is loaded
        if model is None:
            return jsonify({'error': 'Model not available'}), 500
        
        # Make prediction
        predicted_class, description = predict_image_keras(model, filepath)
        
        # Clean up uploaded file (optional - remove if you want to keep files)
        try:
            os.remove(filepath)
        except:
            pass  # Ignore cleanup errors
        
        return render_template('result.html',
                               prediction=predicted_class,
                               description=description,
                               image_path=filepath)
                               
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

# Global error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)