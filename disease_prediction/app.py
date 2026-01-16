from flask import Flask, render_template, request, jsonify
from utils import load_keras_model, predict_image_keras
import os
import re
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "model.h5")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# ---------------- HELPERS ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    cleaned = re.sub(r'[<>:"/\\|?*]', "", filename)
    return secure_filename(cleaned)

# ---------------- LOAD MODEL ----------------
try:
    model = load_keras_model(MODEL_PATH)
except Exception as e:
    app.logger.error(f"Model load failed: {e}")
    model = None

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return render_template(
                "result.html",
                error="No image uploaded."
            )

        file = request.files["file"]

        if file.filename == "":
            return render_template(
                "result.html",
                error="No image selected."
            )

        if not allowed_file(file.filename):
            return render_template(
                "result.html",
                error="Invalid file type. Upload JPG, PNG, or BMP."
            )

        if model is None:
            return render_template(
                "result.html",
                error="Model not available."
            )

        filename = sanitize_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(filepath)

        predicted_class, description, confidence = predict_image_keras(model, filepath)

        # Cleanup uploaded file
        try:
            os.remove(filepath)
        except Exception:
            pass

        # Confidence handling (IMPORTANT FIX)
        warning = None
        if confidence < 0.5:
            warning = "Low confidence prediction. Results may be less accurate."

        app.logger.info(
            f"Disease Prediction → {predicted_class}, confidence={confidence:.2f}"
        )

        return render_template(
            "result.html",
            prediction=predicted_class,
            description=description,
            confidence=round(confidence * 100, 2),
            warning=warning
        )

    except Exception as e:
        app.logger.error(f"Prediction error: {e}")
        return render_template(
            "result.html",
            error="Prediction failed. Please try again."
        )

# ---------------- ERROR HANDLERS ----------------
@app.errorhandler(413)
def too_large(error):
    return render_template(
        "result.html",
        error="Uploaded file is too large."
    )

@app.errorhandler(500)
def internal_error(error):
    return render_template(
        "result.html",
        error="Internal server error."
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
