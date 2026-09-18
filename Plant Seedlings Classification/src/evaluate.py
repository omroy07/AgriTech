"""
Evaluation engine for Plant Seedlings Classification models.
Calculates Accuracy, Precision, Recall, F1-Score, Confusion Matrices, and cross-architecture benchmarks.
"""

import os
import argparse
import os
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

try:
    from .config import (
        CLASS_NAMES,
        NUM_CLASSES,
        SAVED_MODELS_DIR,
        OUTPUTS_DIR,
        RAW_TRAIN_DIR,
        BENCHMARK_RESULTS,
        DEFAULT_CONFIG,
    )
    from .data_loader import get_image_generators, generate_mock_dataset
    from .visualize import plot_confusion_matrix, plot_architecture_comparisons
except ImportError:
    from config import (
        CLASS_NAMES,
        NUM_CLASSES,
        SAVED_MODELS_DIR,
        OUTPUTS_DIR,
        RAW_TRAIN_DIR,
        BENCHMARK_RESULTS,
        DEFAULT_CONFIG,
    )
    from data_loader import get_image_generators, generate_mock_dataset
    from visualize import plot_confusion_matrix, plot_architecture_comparisons


def evaluate_model(model_path_or_model, data_dir=RAW_TRAIN_DIR, model_name="Model", batch_size=32):
    """
    Evaluates a model instance or loaded .h5 model on validation dataset.
    Returns evaluation metrics dictionary, confusion matrix, and classification report.
    """
    import tensorflow as tf
    from sklearn.metrics import (
        classification_report,
        confusion_matrix,
        accuracy_score,
        precision_recall_fscore_support,
        cohen_kappa_score,
    )

    if isinstance(model_path_or_model, (str, Path)):
        if not os.path.exists(model_path_or_model):
            raise FileNotFoundError(f"Model file not found at {model_path_or_model}")
        print(f"📦 Loading model from {model_path_or_model}...")
        model = tf.keras.models.load_model(model_path_or_model)
    else:
        model = model_path_or_model

    if not os.path.exists(data_dir):
        generate_mock_dataset(target_dir=data_dir)

    _, val_gen = get_image_generators(data_dir=data_dir, batch_size=batch_size)

    # Predictions
    print(f"🔍 Evaluating {model_name} on validation set...")
    val_gen.reset()
    y_pred_probs = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = val_gen.classes

    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    kappa = cohen_kappa_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)

    report_dict = classification_report(
        y_true,
        y_pred,
        target_names=CLASS_NAMES[: len(np.unique(y_true))],
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "model_name": model_name,
        "accuracy": float(acc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "cohen_kappa": float(kappa),
    }

    # Save Confusion Matrix plot
    cm_path = Path(OUTPUTS_DIR) / f"{model_name.lower()}_confusion_matrix.png"
    plot_confusion_matrix(cm, class_names=CLASS_NAMES, model_name=model_name, save_path=str(cm_path))

    return metrics, cm, report_dict


def generate_benchmark_summary(benchmark_data=BENCHMARK_RESULTS, save_path=None):
    """
    Generates a Pandas DataFrame and Markdown table comparing all architectures.
    """
    records = []
    for model_name, data in benchmark_data.items():
        records.append({
            "Architecture": model_name,
            "Accuracy": f"{data['accuracy']*100:.2f}%",
            "Precision": f"{data['precision']*100:.2f}%",
            "Recall": f"{data['recall']*100:.2f}%",
            "F1-Score": f"{data['f1_score']*100:.2f}%",
            "Parameters": data.get("parameters", "N/A"),
            "Latency (ms)": data.get("latency_ms", "N/A"),
            "Model Size": data.get("size_mb", "N/A"),
        })

    df = pd.DataFrame(records)
    if save_path:
        df.to_csv(save_path, index=False)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate CNN on Plant Seedlings Dataset")
    parser.add_argument("--model_path", type=str, default=None, help="Path to saved .h5 model")
    parser.add_argument("--model_name", type=str, default="ResNet50", help="Architecture name")
    parser.add_argument("--benchmark", action="store_true", help="Print benchmark summary table")

    args = parser.parse_args()

    if args.benchmark or args.model_path is None:
        print("\n=== CNN Architectures Benchmark Summary ===")
        df = generate_benchmark_summary()
        print(df.to_string(index=False))

        # Generate comparison plot
        plot_path = Path(OUTPUTS_DIR) / "architecture_benchmark_comparison.png"
        plot_architecture_comparisons(save_path=str(plot_path))
        print(f"\n[INFO] Benchmark comparison chart saved to: {plot_path}")
    else:
        metrics, cm, report = evaluate_model(args.model_path, model_name=args.model_name)
        print(f"\n[SUCCESS] Evaluation Results for {args.model_name}:")
        for k, v in metrics.items():
            print(f"  - {k}: {v}")
