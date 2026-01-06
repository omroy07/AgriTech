import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from keras_facenet import FaceNet
from numpy.linalg import norm
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
KNOWN_DIR = os.path.join(BASE_DIR, "known_faces")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(UPLOAD_DIR, exist_ok=True)


face_nonface_model = load_model(
    os.path.join(MODEL_DIR, "face_vs_nonface_model.h5"),
    compile=False
)

embedder = FaceNet()

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (norm(a) * norm(b))

def get_embedding(face):
    face = cv2.resize(face, (160, 160))
    face = face.astype("float32")
    face = np.expand_dims(face, axis=0)
    return embedder.embeddings(face)[0]


known_embeddings = {}

for file in os.listdir(KNOWN_DIR):
    path = os.path.join(KNOWN_DIR, file)
    img = cv2.imread(path)
    if img is None:
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        continue

    x, y, w, h = faces[0]
    face = img[y:y+h, x:x+w]

    name = os.path.splitext(file)[0]
    known_embeddings[name] = get_embedding(face)

print("FINAL loaded identities:", known_embeddings.keys())


def recognize_face(face):
    emb = get_embedding(face)
    min_dist = 999
    identity = "Unknown"

    for name, known_emb in known_embeddings.items():
        dist = cosine_distance(emb, known_emb)
        if dist < min_dist:
            min_dist = dist
            identity = name

    if min_dist > 0.6:
        identity = "Unknown"

    return identity, float(min_dist)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recognize", methods=["POST"])
def recognize():
    if "image" not in request.files:
        return jsonify({"face_detected": False})

    file = request.files["image"]
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)

    img = cv2.imread(path)
    if img is None:
        return jsonify({"face_detected": False})

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        return jsonify({"face_detected": False})

    x, y, w, h = faces[0]
    face = img[y:y+h, x:x+w]

    test = cv2.resize(face, (224, 224))
    test = test / 255.0
    test = np.expand_dims(test, axis=0)

    pred = face_nonface_model.predict(test)[0][0]
    if pred < 0.5:
        return jsonify({"face_detected": False})

    name, dist = recognize_face(face)

    return jsonify({
        "face_detected": True,
        "identity": name,
        "distance": dist
    })

if __name__ == "__main__":
    app.run(debug=True)
