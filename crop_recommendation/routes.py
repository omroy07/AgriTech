from flask import Blueprint, render_template, request, jsonify
import joblib
import numpy as np
import os
from backend.extensions import cache

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
@cache.memoize(timeout=300)  # Cache for 5 minutes
def predict():
    try:
        from backend.schemas import CropPredictionSchema
        from marshmallow import ValidationError
        
        schema = CropPredictionSchema()
        try:
            # Convert form data to dictionary and validate
            form_data = request.form.to_dict()
            validated_data = schema.load(form_data)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400

        data = [
            validated_data["N"],
            validated_data["P"],
            validated_data["K"],
            validated_data["temperature"],
            validated_data["humidity"],
            validated_data["ph"],
            validated_data["rainfall"],
        ]

        prediction = model.predict([data])[0]
        crop = label_encoder.inverse_transform([prediction])[0]

        return render_template(
            "result.html",
            crop=crop,
            params=request.form
        )

    except ValueError:
        return jsonify({"error": "Invalid numeric values"}), 400
