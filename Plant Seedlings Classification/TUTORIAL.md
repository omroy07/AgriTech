# 📖 Step-by-Step Tutorial: Plant Seedlings Classification with CNNs

Welcome to the **Plant Seedlings Classification** guide. This tutorial provides end-to-end instructions for data preprocessing, building 7 distinct CNN architectures, training and fine-tuning models, evaluating metrics, and deploying through Streamlit and FastAPI.

---

## Table of Contents
1. [Environment Setup](#1-environment-setup)
2. [Dataset Acquisition & Preparation](#2-dataset-acquisition--preparation)
3. [Data Preprocessing & Augmentation](#3-data-preprocessing--augmentation)
4. [Building CNN Architectures](#4-building-cnn-architectures)
5. [Model Training & Fine-Tuning](#5-model-training--fine-tuning)
6. [Evaluation & Confusion Matrix Analysis](#6-evaluation--confusion-matrix-analysis)
7. [Running the Streamlit Dashboard](#7-running-the-streamlit-dashboard)
8. [Running the FastAPI REST API](#8-running-the-fastapi-rest-api)
9. [Docker Deployment](#9-docker-deployment)

---

## 1. Environment Setup

Clone the repository and install the dependencies:

```bash
cd "Plant Seedlings Classification"
pip install -r requirements.txt
```

Verify TensorFlow and GPU availability:
```python
import tensorflow as tf
print("TensorFlow Version:", tf.__version__)
print("GPU Available:", tf.config.list_physical_devices('GPU'))
```

---

## 2. Dataset Acquisition & Preparation

The project classifies **12 plant species** (weeds and crops) using the [V2 Plant Seedlings Dataset](https://www.kaggle.com/vbookshelf/v2-plant-seedlings-dataset).

### Option A: Automatic Download via Kaggle API
Place your `kaggle.json` in `~/.kaggle/kaggle.json` (or `C:\Users\<user>\.kaggle\kaggle.json` on Windows):
```bash
python Dataset/download_dataset.py
```

### Option B: Offline Synthetic Mock Generation
If working offline without Kaggle credentials, generate synthetic mock seedlings for immediate testing:
```bash
python src/data_loader.py
```

---

## 3. Data Preprocessing & Augmentation

High-yield seedling identification requires handling varying lighting conditions, soil colors, and leaf orientations.

```python
from src.data_loader import get_image_generators

train_gen, val_gen = get_image_generators(
    data_dir="Dataset/train",
    img_size=(224, 224),
    batch_size=32,
    validation_split=0.2
)
```

**Applied Augmentations:**
- Random Rotations ($\pm 40^\circ$)
- Horizontal & Vertical Flips
- Width & Height Shifts ($\pm 20\%$)
- Shear and Zoom Transformations ($\pm 20\%$)
- RGB Normalization ($1/255.0$)

---

## 4. Building CNN Architectures

You can build and test any of the 7 supported architectures using the `build_model` factory:

```python
from src.models import build_model, compile_model

# Supported: 'ResNet50', 'AlexNet', 'VGG16', 'InceptionV3', 'MobileNetV2', 'DenseNet121', 'SqueezeNet'
model = build_model(architecture="ResNet50", num_classes=12, weights="imagenet", freeze_base=True)
model = compile_model(model, learning_rate=1e-3)
model.summary()
```

---

## 5. Model Training & Fine-Tuning

### CLI Training
Train any architecture using the command line:

```bash
# Train ResNet50 for 25 epochs
python src/train.py --model ResNet50 --epochs 25 --batch_size 32 --lr 0.001

# Train MobileNetV2 with fine-tuning enabled
python src/train.py --model MobileNetV2 --epochs 20 --fine_tune --lr 0.001

# Train AlexNet from scratch
python src/train.py --model AlexNet --epochs 30 --batch_size 32
```

Outputs will be saved to:
- Saved Weights: `saved_models/<architecture>_best.h5`
- Training Curves: `outputs/<architecture>_learning_curves.png`
- CSV Logs: `logs/<architecture>_training_log.csv`

---

## 6. Evaluation & Confusion Matrix Analysis

### Benchmark All Architectures
```bash
python src/evaluate.py --benchmark
```

### Evaluate a Specific Trained Model
```bash
python src/evaluate.py --model_path saved_models/resnet50_best.h5 --model_name ResNet50
```

Calculated metrics include:
- **Accuracy**: Overall classification accuracy
- **Precision, Recall, F1-Score**: Weighted and per-class metrics
- **Cohen's Kappa**: Inter-rater agreement score
- **Confusion Matrix**: Visualized with Seaborn heatmaps

---

## 7. Running the Streamlit Dashboard

Launch the interactive web UI:

```bash
streamlit run app.py
```

### Key Features of the Dashboard:
1. **Live Classification Tab**: Upload or pick a seedling sample $\to$ instant prediction, confidence bar, weed/crop badge, and agronomic recommendations.
2. **Model Benchmark Explorer**: Interactive comparison table & charts for all 7 architectures.
3. **Visualizer Tab**: Review convergence curves and multi-class confusion matrices.
4. **Batch Processing Tab**: Upload multiple images and download a CSV report.

---

## 8. Running the FastAPI REST API

Start the REST API server:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `GET /health`
- **Model List & Benchmarks**: `GET /models`
- **Species Database**: `GET /species`
- **Classify Image**: `POST /predict` (multipart/form-data)

---

## 9. Docker Deployment

Deploy both the Streamlit Dashboard and FastAPI service using Docker Compose:

```bash
# Build and run containers
docker-compose up --build -d

# View running containers
docker-compose ps
```

- **Streamlit Dashboard**: `http://localhost:8501`
- **FastAPI Documentation**: `http://localhost:8000/docs`

To stop the containers:
```bash
docker-compose down
```
