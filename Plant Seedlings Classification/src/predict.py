"""
Inference and prediction pipeline for Plant Seedlings Classification.
Includes Top-K predictions, Test-Time Augmentation (TTA), and agricultural recommendation generator.
"""

import os
import argparse
import numpy as np
from pathlib import Path
from PIL import Image

try:
    from .config import (
        CLASS_NAMES,
        PLANT_SPECIES_INFO,
        SAVED_MODELS_DIR,
        DEFAULT_CONFIG,
    )
    from .data_loader import preprocess_image
    from .models import build_model
except ImportError:
    from config import (
        CLASS_NAMES,
        PLANT_SPECIES_INFO,
        SAVED_MODELS_DIR,
        DEFAULT_CONFIG,
    )
    from data_loader import preprocess_image
    from models import build_model


class SeedlingClassifier:
    """
    Wrapper for plant seedling inference with crop vs weed advisory.
    """

    def __init__(self, model_path=None, architecture="ResNet50"):
        self.architecture = architecture
        self.model_path = model_path
        self.model = self._load_or_build_model()

    def _load_or_build_model(self):
        """Loads trained model weights or builds architecture."""
        import tensorflow as tf

        if self.model_path and os.path.exists(self.model_path):
            print(f"[INFO] Loading weights from {self.model_path}...")
            return tf.keras.models.load_model(self.model_path)
        
        # Check standard saved models directory
        standard_path = Path(SAVED_MODELS_DIR) / f"{self.architecture.lower()}_best.h5"
        if standard_path.exists():
            print(f"[INFO] Loading weights from {standard_path}...")
            return tf.keras.models.load_model(str(standard_path))

        print(f"[INFO] Pre-trained weights not found on disk. Building initialized {self.architecture} model...")
        weights_arg = "imagenet" if self.architecture.lower() not in ["alexnet", "squeezenet"] else None
        return build_model(architecture=self.architecture, weights=weights_arg)

    def predict(self, image_input, top_k=3, use_tta=False):
        """
        Predicts the species for a given image.
        Returns top-k predictions with probabilities and agricultural guidance.
        """
        img_batch = preprocess_image(image_input)

        if use_tta:
            # Test-Time Augmentation: average predictions over original and flipped/rotated versions
            preds = [self.model.predict(img_batch, verbose=0)[0]]
            # Horizontal flip
            preds.append(self.model.predict(np.flip(img_batch, axis=2), verbose=0)[0])
            # Vertical flip
            preds.append(self.model.predict(np.flip(img_batch, axis=1), verbose=0)[0])
            probs = np.mean(preds, axis=0)
        else:
            probs = self.model.predict(img_batch, verbose=0)[0]

        top_indices = np.argsort(probs)[::-1][:top_k]

        results = []
        for idx in top_indices:
            class_name = CLASS_NAMES[idx]
            info = PLANT_SPECIES_INFO.get(class_name, {})
            results.append({
                "class_name": class_name,
                "scientific_name": info.get("scientific_name", "N/A"),
                "confidence": float(probs[idx]),
                "confidence_percent": f"{probs[idx] * 100:.2f}%",
                "type": info.get("type", "Unknown"),
                "severity": info.get("severity", "N/A"),
                "action": info.get("action", "N/A"),
                "description": info.get("description", ""),
            })

        top_result = results[0]
        return {
            "prediction": top_result["class_name"],
            "type": top_result["type"],
            "confidence": top_result["confidence"],
            "confidence_percent": top_result["confidence_percent"],
            "top_k": results,
            "agricultural_advisory": {
                "species": top_result["class_name"],
                "scientific_name": top_result["scientific_name"],
                "plant_category": top_result["type"],
                "threat_severity": top_result["severity"],
                "recommended_action": top_result["action"],
            },
        }

    def predict_batch(self, image_paths, top_k=1):
        """Processes a batch of images and returns a list of prediction records."""
        batch_results = []
        for img_path in image_paths:
            try:
                res = self.predict(img_path, top_k=top_k)
                batch_results.append({
                    "file_path": str(img_path),
                    "file_name": Path(img_path).name,
                    "prediction": res["prediction"],
                    "type": res["type"],
                    "confidence": res["confidence_percent"],
                    "action": res["agricultural_advisory"]["recommended_action"],
                })
            except Exception as e:
                batch_results.append({
                    "file_path": str(img_path),
                    "file_name": Path(img_path).name,
                    "error": str(e),
                })
        return batch_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify plant seedling image")
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--model", type=str, default="ResNet50", help="Model architecture")
    parser.add_argument("--tta", action="store_true", help="Enable Test-Time Augmentation")

    args = parser.parse_args()
    classifier = SeedlingClassifier(architecture=args.model)
    result = classifier.predict(args.image, use_tta=args.tta)

    print("\n=== Classification Result ===")
    print(f"Plant Species : {result['prediction']}")
    print(f"Classification: {result['type']}")
    print(f"Confidence    : {result['confidence_percent']}")
    print(f"Action        : {result['agricultural_advisory']['recommended_action']}")
