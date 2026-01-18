from flask import Blueprint, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

from .utils import load_pytorch_model, predict_image_pytorch
from backend.extensions import cache

# ================= BLUEPRINT =================
disease_bp = Blueprint(
    "disease",
    __name__,
    url_prefix="/disease",
    template_folder="template",
    static_folder="static"
)

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "model", "plant_disease_resnet18.pth"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR, "static", "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= CLASS NAMES (LOCKED) =================
# MUST match training order (38 classes)
CLASS_NAMES = [
    'Apple___Black_rot', 'Apple___healthy',
    'Blueberry___healthy',
    'Cherry___Powdery_mildew', 'Cherry___healthy',
    'Corn___Cercospora_leaf_spot', 'Corn___Common_rust',
    'Corn___Northern_Leaf_Blight', 'Corn___healthy',
    'Grape___Black_rot', 'Grape___Esca', 'Grape___Leaf_blight',
    'Grape___healthy',
    'Orange___Haunglongbing',
    'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper___Bacterial_spot', 'Pepper___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight',
    'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites',
    'Tomato___Target_Spot', 'Tomato___Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]


# ================= LOAD MODEL ONCE =================
model = load_pytorch_model(MODEL_PATH)

print("✅ Disease model loaded successfully")
print(f"✅ Model supports {len(CLASS_NAMES)} classes")

# ================= ROUTES =================
@disease_bp.route("/")
def disease_home():
    return render_template("disease_index.html")


@disease_bp.route("/predict", methods=["POST"])
@cache.memoize(timeout=300)  # Cache for 5 minutes
def predict_disease():
    file = request.files.get("file")

    if not file or file.filename == "":
        return redirect(url_for("disease.disease_home"))

    filename = secure_filename(file.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(image_path)

    class_idx, confidence = predict_image_pytorch(model, image_path)
    prediction = CLASS_NAMES[class_idx]

    return render_template(
        "disease_result.html",
        image_url=url_for("disease.static", filename=f"uploads/{filename}"),
        prediction=prediction.replace("___", " "),
        description=f"AI detected {prediction.replace('___', ' ')}",
        confidence=confidence
    )
