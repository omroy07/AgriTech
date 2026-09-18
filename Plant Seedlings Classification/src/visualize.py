"""
Visualization utilities for model training curves, confusion matrices, architecture benchmarks, and Grad-CAM explainability.
"""

import os
import numpy as np
from pathlib import Path
from PIL import Image

try:
    from .config import CLASS_NAMES, OUTPUTS_DIR, BENCHMARK_RESULTS
except ImportError:
    from config import CLASS_NAMES, OUTPUTS_DIR, BENCHMARK_RESULTS


def plot_training_history(history, model_name="Model", save_path=None):
    """
    Plots training and validation loss and accuracy trajectories.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", palette="muted")
    hist = history.history if hasattr(history, "history") else history
    epochs_range = range(1, len(hist["loss"]) + 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Loss plot
    axes[0].plot(epochs_range, hist["loss"], label="Train Loss", color="#e74c3c", linewidth=2)
    if "val_loss" in hist:
        axes[0].plot(epochs_range, hist["val_loss"], label="Val Loss", color="#c0392b", linestyle="--", linewidth=2)
    axes[0].set_title(f"{model_name} - Loss Trajectory", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Epochs", fontsize=12)
    axes[0].set_ylabel("Cross-Entropy Loss", fontsize=12)
    axes[0].legend(loc="upper right", frameon=True)
    axes[0].grid(True, linestyle=":", alpha=0.6)

    # Accuracy plot
    axes[1].plot(epochs_range, hist["accuracy"], label="Train Accuracy", color="#2ecc71", linewidth=2)
    if "val_accuracy" in hist:
        axes[1].plot(epochs_range, hist["val_accuracy"], label="Val Accuracy", color="#27ae60", linestyle="--", linewidth=2)
    axes[1].set_title(f"{model_name} - Accuracy Trajectory", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("Epochs", fontsize=12)
    axes[1].set_ylabel("Accuracy", fontsize=12)
    axes[1].legend(loc="lower right", frameon=True)
    axes[1].grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
    return fig


def plot_confusion_matrix(cm, class_names=CLASS_NAMES, model_name="CNN Model", save_path=None):
    """
    Plots an annotated confusion matrix heatmap.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", palette="muted")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        xticklabels=class_names,
        yticklabels=class_names,
        cbar=True,
        ax=ax,
        linewidths=0.5,
    )
    ax.set_title(f"Confusion Matrix - {model_name}", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlabel("Predicted Label", fontsize=12, labelpad=10)
    ax.set_ylabel("Ground Truth Label", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
    return fig


def plot_architecture_comparisons(benchmark_data=BENCHMARK_RESULTS, save_path=None):
    """
    Generates multi-metric comparison charts across all 7 CNN architectures.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", palette="muted")
    architectures = list(benchmark_data.keys())
    accuracies = [benchmark_data[a]["accuracy"] * 100 for a in architectures]
    f1_scores = [benchmark_data[a]["f1_score"] * 100 for a in architectures]
    latencies = [benchmark_data[a]["latency_ms"] for a in architectures]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Accuracy & F1 Comparison
    x = np.arange(len(architectures))
    width = 0.35

    ax1.bar(x - width/2, accuracies, width, label="Accuracy (%)", color="#2ecc71")
    ax1.bar(x + width/2, f1_scores, width, label="F1-Score (%)", color="#3498db")
    ax1.set_title("Architecture Performance Benchmark (Accuracy & F1)", fontsize=13, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(architectures, rotation=35, ha="right")
    ax1.set_ylim(85, 100)
    ax1.set_ylabel("Score (%)", fontsize=11)
    ax1.legend(loc="lower right")
    ax1.grid(True, linestyle=":", alpha=0.5)

    # Latency Comparison
    ax2.bar(architectures, latencies, color="#e67e22", width=0.5)
    ax2.set_title("Inference Latency (ms per image)", fontsize=13, fontweight="bold")
    ax2.set_xticklabels(architectures, rotation=35, ha="right")
    ax2.set_ylabel("Latency (ms)", fontsize=11)
    ax2.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
    return fig


def generate_gradcam(model, img_array, last_conv_layer_name=None, pred_index=None):
    """
    Computes Grad-CAM explainability heatmap overlay for an image.
    """
    import tensorflow as tf

    if last_conv_layer_name is None:
        # Automatically find the last 4D convolutional layer
        for layer in reversed(model.layers):
            if len(layer.output_shape) == 4 or "conv" in layer.name.lower():
                last_conv_layer_name = layer.name
                break

    try:
        grad_model = tf.keras.models.Model(
            [model.inputs],
            [model.get_layer(last_conv_layer_name).output, model.output],
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            if pred_index is None:
                pred_index = tf.argmax(predictions[0])
            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        return heatmap.numpy()
    except Exception as e:
        print(f"Grad-CAM generation failed: {e}")
        return np.zeros((img_array.shape[1], img_array.shape[2]))
