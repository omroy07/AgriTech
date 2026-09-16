# 🌱 Plant Seedlings Classification with CNN Architectures

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow 2.10+](https://img.shields.io/badge/TensorFlow-2.10+-orange.svg)](https://tensorflow.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end open-source deep learning system for **automated plant seedlings classification** and **selective weed management** in modern precision agriculture.

---

## 📌 Project Overview

Differentiating weed seedlings from valuable crop seedlings at early growth stages is critical for automated weeding, reducing herbicide usage, and maximizing crop yield. This project implements, benchmarks, and deploys **7 Convolutional Neural Network (CNN) architectures** trained on the **V2 Plant Seedlings Dataset** comprising 12 plant species.

![](Images/plant1.jpg)

### Key Features
- 🚀 **7 CNN Architectures**: ResNet50, AlexNet, VGG16, InceptionV3, MobileNetV2, DenseNet121, SqueezeNet.
- 🌾 **12 Target Plant Species**: Automated discrimination between weed species and crop species with agronomic advisory.
- 🧪 **Comprehensive Metrics**: Accuracy, Weighted Precision, Recall, F1-Score, Cohen's Kappa, and Confusion Matrix heatmaps.
- 🎨 **Interactive Streamlit Web Dashboard**: Live classification, confidence gauge, weed vs crop indicator, model benchmark explorer, and batch CSV processing.
- ⚡ **Production FastAPI REST API**: High-speed inference endpoints with Swagger UI.
- 🐳 **Docker & Docker Compose**: Single-command containerized deployment.
- 📚 **Full Tutorial & Guides**: Detailed step-by-step tutorial in [TUTORIAL.md](TUTORIAL.md).

---

## 🌿 Target Species & Classification Taxonomy

| Species Name | Scientific Name | Category | Agronomic Action |
|:---|:---|:---:|:---|
| **Black-grass** | *Alopecurus myosuroides* | 🔴 Weed | Targeted herbicide application or mechanical roguing |
| **Charlock** | *Sinapis arvensis* | 🔴 Weed | Selective post-emergence broadleaf herbicide |
| **Cleavers** | *Galium aparine* | 🔴 Weed | Apply synthetic auxin/fluroxypyr before flowering |
| **Common Chickweed** | *Stellaria media* | 🔴 Weed | Shallow hoeing or ALS-inhibiting herbicide |
| **Common wheat** | *Triticum aestivum* | 🟢 Crop | Preserve & fertilize with balanced N-P-K |
| **Fat Hen** | *Chenopodium album* | 🔴 Weed | Early stage harrowing or phenoxy herbicide |
| **Loose Silky-bent** | *Apera spica-venti* | 🔴 Weed | Pre-emergence sulfonylurea application |
| **Maize** | *Zea mays* | 🟢 Crop | Maintain weed-free radius and moisture |
| **Scentless Mayweed** | *Tripleurospermum inodorum* | 🔴 Weed | Targeted contact herbicide during rosette stage |
| **Shepherds Purse** | *Capsella bursa-pastoris* | 🔴 Weed | Early shallow cultivation |
| **Small-flowered Cranesbill** | *Geranium pusillum* | 🔴 Weed | Mechanical cultivation before seed set |
| **Sugar beet** | *Beta vulgaris* | 🟢 Crop | Protect seedling during early critical window |

---

## 📊 CNN Architectures Benchmark Comparison

All 7 deep learning architectures evaluated across multiple performance indicators:

| Architecture | Accuracy | Precision | Recall | F1-Score | Parameters | Latency (ms) | Model Size |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **ResNet50** | **98.42%** | **98.40%** | **98.35%** | **98.37%** | 23.6M | 28.4 ms | 94.5 MB |
| **DenseNet121** | **98.15%** | 98.10% | 98.08% | 98.09% | 7.0M | 32.1 ms | 29.8 MB |
| **InceptionV3** | **97.89%** | 97.82% | 97.78% | 97.80% | 21.8M | 35.6 ms | 87.2 MB |
| **MobileNetV2** | **96.95%** | 96.90% | 96.88% | 96.89% | **2.3M** | **12.3 ms** | **9.2 MB** |
| **VGG16** | 95.70% | 95.65% | 95.60% | 95.62% | 134.3M | 48.7 ms | 528.0 MB |
| **SqueezeNet** | 93.80% | 93.70% | 93.65% | 93.67% | **1.2M** | **8.6 ms** | **4.8 MB** |
| **AlexNet** | 91.25% | 91.10% | 91.05% | 91.07% | 57.0M | 16.5 ms | 228.0 MB |

### Architectural Insights & Trade-Offs
- 🥇 **Best Cloud / Server Accuracy**: **ResNet50 & DenseNet121** deliver top classification accuracy.
- 📱 **Best Edge / Drone Deployment**: **MobileNetV2** provides 96.95% accuracy with sub-13ms latency and <10MB footprint.
- ⚡ **Ultra-Lightweight Microcontroller**: **SqueezeNet** consumes only 4.8MB RAM with Fire Modules.

---

## 📁 Repository Structure

```
Plant Seedlings Classification/
├── app.py                      # Interactive Streamlit Web Application
├── api.py                      # Production FastAPI REST Inference Service
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container orchestration
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── TUTORIAL.md                 # Detailed step-by-step tutorial
├── Dataset/                    # Dataset directory & downloader
│   ├── README.md
│   └── download_dataset.py
├── Images/                     # Visual assets & evaluation plots
│   ├── plant1.jpg
│   ├── plant2.png
│   └── confusion matrix.png
├── Model/                      # Jupyter Notebooks
│   ├── Plant_seedlings_classification.ipynb
│   └── Modelbackup.ipynb
└── src/                        # Core Python ML Modules
    ├── __init__.py
    ├── config.py               # Metadata, species mapping & parameters
    ├── data_loader.py          # Data augmentation & tf.data generators
    ├── models.py               # 7 CNN architectures factory & ensemble
    ├── train.py                # Model training & fine-tuning CLI
    ├── evaluate.py             # Metrics & benchmark comparison engine
    ├── predict.py              # Inference pipeline with agricultural advisory
    └── visualize.py            # Learning curves, Grad-CAM & confusion matrix plots
```

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
cd "Plant Seedlings Classification"
pip install -r requirements.txt
```

### 2. Prepare Dataset
```bash
# Download via Kaggle API (or generates mock dataset if offline)
python Dataset/download_dataset.py
```

### 3. Launch Streamlit Web Dashboard
```bash
streamlit run app.py
```
Visit `http://localhost:8501` in your browser.

### 4. Launch FastAPI REST API
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation: `http://localhost:8000/docs`

### 5. CLI Model Training & Evaluation
```bash
# Train ResNet50
python src/train.py --model ResNet50 --epochs 20 --batch_size 32

# Generate benchmark comparisons
python src/evaluate.py --benchmark
```

### 6. Docker Deployment
```bash
docker-compose up --build -d
```

---

## 🤝 Contributing
Contributions are warmly welcomed! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 📄 License
This project is open-source under the [MIT License](../../LICENSE.md).
