from flask import Flask, render_template, request
from utils import load_keras_model, predict_image_keras
import os

app = Flask(__name__)

UPLOAD_FOLDER = r'disease/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the Keras model
model = load_keras_model(r'disease/model.h5')

# Route for homepage


@app.route('/')
def index():
    return render_template('index.html')

# Route for prediction


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return "No file uploaded."
    file = request.files['file']
    if file.filename == '':
        return "No selected file."

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    predicted_class, description = predict_image_keras(model, filepath)

    return render_template('result.html',
                           prediction=predicted_class,
                           description=description,
                           image_path=filepath)


if __name__ == '__main__':
    app.run(debug=True)
