from flask import Blueprint, render_template, request, jsonify
import joblib
import numpy as np
import os
from extensions import limiter

crop_bp = Blueprint(
    'crop',
    __name__,
    url_prefix='/crop',
    template_folder='templates',
    static_folder='static'
)


# -------------------- Load Model Safely --------------------

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model", "rf_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "model", "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# -------------------- Routes --------------------

@crop_bp.route("/", methods=["GET"])
def crop_home():
    return render_template("index.html")


@crop_bp.route("/predict", methods=["POST"])
@limiter.limit("10 per minute")
def predict():
    try:
        # Match frontend + ML column names
        data = [
            float(request.form.get("N")),
            float(request.form.get("P")),
            float(request.form.get("K")),
            float(request.form.get("temperature")),
            float(request.form.get("humidity")),
            float(request.form.get("ph")),
            float(request.form.get("rainfall")),
        ]

        # Validate inputs
        if any(v is None for v in data):
            return jsonify({"error": "Missing input fields"}), 400

        prediction = model.predict([data])[0]
        crop = label_encoder.inverse_transform([prediction])[0]

        return render_template(
            "result.html",
            crop=crop,
            params=request.form
        )

    except ValueError:
        return jsonify({"error": "Invalid numeric values"}), 400
