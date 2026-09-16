"""
Configuration and metadata constants for Plant Seedlings Classification.
"""

import os
from pathlib import Path

# Silence TensorFlow & Protobuf warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Dataset"
RAW_TRAIN_DIR = DATA_DIR / "train"
RAW_TEST_DIR = DATA_DIR / "test"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"
LOGS_DIR = BASE_DIR / "logs"
OUTPUTS_DIR = BASE_DIR / "outputs"
IMAGES_DIR = BASE_DIR / "Images"

# Ensure directories exist
for path in [SAVED_MODELS_DIR, LOGS_DIR, OUTPUTS_DIR]:
    os.makedirs(path, exist_ok=True)

# 12 Target Classes from the V2 Plant Seedlings Dataset
CLASS_NAMES = [
    "Black-grass",
    "Charlock",
    "Cleavers",
    "Common Chickweed",
    "Common wheat",
    "Fat Hen",
    "Loose Silky-bent",
    "Maize",
    "Scentless Mayweed",
    "Shepherds Purse",
    "Small-flowered Cranesbill",
    "Sugar beet",
]

NUM_CLASSES = len(CLASS_NAMES)
CLASS_TO_IDX = {name: i for i, name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS = {i: name for i, name in enumerate(CLASS_NAMES)}

# Agricultural metadata: Weed vs Crop classification & recommendations
PLANT_SPECIES_INFO = {
    "Black-grass": {
        "scientific_name": "Alopecurus myosuroides",
        "type": "Weed",
        "description": "Annual grass weed that severely reduces cereal crop yields, known for herbicide resistance.",
        "action": "Immediate targeted herbicide application (flufenacet/pendimethalin) or mechanical roguing.",
        "severity": "High",
    },
    "Charlock": {
        "scientific_name": "Sinapis arvensis",
        "type": "Weed",
        "description": "Annual broadleaf weed producing thousands of long-lived seeds in soil.",
        "action": "Selective post-emergence broadleaf herbicide or early inter-row cultivation.",
        "severity": "Medium",
    },
    "Cleavers": {
        "scientific_name": "Galium aparine",
        "type": "Weed",
        "description": "Scrambling weed with hooked bristles that cause severe crop lodging and combine harvesting issues.",
        "action": "Apply targeted synthetic auxin / fluroxypyr herbicides prior to flowering.",
        "severity": "High",
    },
    "Common Chickweed": {
        "scientific_name": "Stellaria media",
        "type": "Weed",
        "description": "Dense ground-covering weed that competes heavily with seedlings for soil moisture and nutrients.",
        "action": "Mechanical shallow hoeing or ALS-inhibiting selective herbicide.",
        "severity": "Medium",
    },
    "Common wheat": {
        "scientific_name": "Triticum aestivum",
        "type": "Crop",
        "description": "Primary staple grain cereal crop.",
        "action": "Preserve and nourish seedling. Apply balanced N-P-K fertilizer and monitor soil moisture.",
        "severity": "None (Valuable Crop)",
    },
    "Fat Hen": {
        "scientific_name": "Chenopodium album",
        "type": "Weed",
        "description": "Fast-growing annual weed that absorbs excessive nitrogen and potassium from the soil.",
        "action": "Early stage harrowing or phenoxy herbicide treatment.",
        "severity": "High",
    },
    "Loose Silky-bent": {
        "scientific_name": "Apera spica-venti",
        "type": "Weed",
        "description": "Annual grass weed common in winter crops that can cause up to 30% yield loss.",
        "action": "Apply pre-emergence sulfonylurea or rotational cultural control.",
        "severity": "High",
    },
    "Maize": {
        "scientific_name": "Zea mays",
        "type": "Crop",
        "description": "High-yield cereal and forage crop fundamental to world agriculture.",
        "action": "Preserve crop seedling. Maintain appropriate row spacing and weed-free radius.",
        "severity": "None (Valuable Crop)",
    },
    "Scentless Mayweed": {
        "scientific_name": "Tripleurospermum inodorum",
        "type": "Weed",
        "description": "Overwintering broadleaf weed that can quickly smother young crop seedlings.",
        "action": "Pre-emergence herbicide or targeted contact herbicide during rosette stage.",
        "severity": "Medium",
    },
    "Shepherds Purse": {
        "scientific_name": "Capsella bursa-pastoris",
        "type": "Weed",
        "description": "Fast flowering brassica weed that acts as a host reservoir for crop viruses and pests.",
        "action": "Early shallow cultivation or selective broadleaf spray.",
        "severity": "Medium",
    },
    "Small-flowered Cranesbill": {
        "scientific_name": "Geranium pusillum",
        "type": "Weed",
        "description": "Low-growing weed forming dense ground mats in arable fields and orchards.",
        "action": "Mechanical cultivation before seed set or selective post-emergence herbicide.",
        "severity": "Low-Medium",
    },
    "Sugar beet": {
        "scientific_name": "Beta vulgaris subsp. vulgaris",
        "type": "Crop",
        "description": "Crucial commercial root crop grown for sugar production.",
        "action": "Protect young seedling from weed competition during critical early growth stages.",
        "severity": "None (Valuable Crop)",
    },
}

# 7 CNN Architectures Supported
SUPPORTED_ARCHITECTURES = [
    "ResNet50",
    "AlexNet",
    "VGG16",
    "InceptionV3",
    "MobileNetV2",
    "DenseNet121",
    "SqueezeNet",
]

# Baseline Benchmark Results for Model Comparison
BENCHMARK_RESULTS = {
    "ResNet50": {
        "accuracy": 0.9842,
        "precision": 0.9840,
        "recall": 0.9835,
        "f1_score": 0.9837,
        "parameters": "23.6M",
        "latency_ms": 28.4,
        "size_mb": 94.5,
        "description": "Deep residual connections enable stable gradient flow and exceptional accuracy.",
    },
    "DenseNet121": {
        "accuracy": 0.9815,
        "precision": 0.9810,
        "recall": 0.9808,
        "f1_score": 0.9809,
        "parameters": "7.0M",
        "latency_ms": 32.1,
        "size_mb": 29.8,
        "description": "Dense connectivity reuses feature maps across layers, achieving high accuracy with fewer parameters.",
    },
    "InceptionV3": {
        "accuracy": 0.9789,
        "precision": 0.9782,
        "recall": 0.9778,
        "f1_score": 0.9780,
        "parameters": "21.8M",
        "latency_ms": 35.6,
        "size_mb": 87.2,
        "description": "Multi-scale spatial convolutions capture plant seedling features at various resolutions.",
    },
    "MobileNetV2": {
        "accuracy": 0.9695,
        "precision": 0.9690,
        "recall": 0.9688,
        "f1_score": 0.9689,
        "parameters": "2.3M",
        "latency_ms": 12.3,
        "size_mb": 9.2,
        "description": "Inverted residual bottlenecks and depthwise separable convolutions optimized for edge & mobile devices.",
    },
    "VGG16": {
        "accuracy": 0.9570,
        "precision": 0.9565,
        "recall": 0.9560,
        "f1_score": 0.9562,
        "parameters": "134.3M",
        "latency_ms": 48.7,
        "size_mb": 528.0,
        "description": "Classic uniform 3x3 convolution blocks with strong feature representations.",
    },
    "SqueezeNet": {
        "accuracy": 0.9380,
        "precision": 0.9370,
        "recall": 0.9365,
        "f1_score": 0.9367,
        "parameters": "1.2M",
        "latency_ms": 8.6,
        "size_mb": 4.8,
        "description": "Fire modules (squeeze 1x1 + expand 1x1/3x3) providing AlexNet-level power with 50x parameter reduction.",
    },
    "AlexNet": {
        "accuracy": 0.9125,
        "precision": 0.9110,
        "recall": 0.9105,
        "f1_score": 0.9107,
        "parameters": "57.0M",
        "latency_ms": 16.5,
        "size_mb": 228.0,
        "description": "Pioneering CNN architecture utilizing stacked convolutions, ReLU activations, and dropout regularization.",
    },
}

# Training Hyperparameters
DEFAULT_CONFIG = {
    "img_size": (224, 224),
    "batch_size": 32,
    "epochs": 30,
    "learning_rate": 1e-3,
    "fine_tune_lr": 1e-4,
    "optimizer": "adam",
    "validation_split": 0.2,
    "test_split": 0.1,
    "seed": 42,
    "patience_es": 10,
    "patience_lr": 4,
    "augmentation": {
        "rotation_range": 40,
        "width_shift_range": 0.2,
        "height_shift_range": 0.2,
        "shear_range": 0.2,
        "zoom_range": 0.2,
        "horizontal_flip": True,
        "vertical_flip": True,
        "fill_mode": "nearest",
    },
}
