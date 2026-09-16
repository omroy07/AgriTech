"""
Training pipeline for Plant Seedlings Classification with CNN architectures.
"""

import os
import argparse
import json
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint,
    CSVLogger,
)

try:
    from .config import (
        DEFAULT_CONFIG,
        SAVED_MODELS_DIR,
        LOGS_DIR,
        OUTPUTS_DIR,
        RAW_TRAIN_DIR,
        SUPPORTED_ARCHITECTURES,
    )
    from .models import build_model, compile_model
    from .data_loader import get_image_generators, generate_mock_dataset
    from .visualize import plot_training_history
except ImportError:
    from config import (
        DEFAULT_CONFIG,
        SAVED_MODELS_DIR,
        LOGS_DIR,
        OUTPUTS_DIR,
        RAW_TRAIN_DIR,
        SUPPORTED_ARCHITECTURES,
    )
    from models import build_model, compile_model
    from data_loader import get_image_generators, generate_mock_dataset
    from visualize import plot_training_history


def train(
    architecture="ResNet50",
    epochs=DEFAULT_CONFIG["epochs"],
    batch_size=DEFAULT_CONFIG["batch_size"],
    learning_rate=DEFAULT_CONFIG["learning_rate"],
    data_dir=RAW_TRAIN_DIR,
    save_dir=SAVED_MODELS_DIR,
    fine_tune=False,
    fine_tune_layers=20,
):
    """
    Executes training workflow for selected CNN architecture.
    """
    print(f"[INFO] Initializing training pipeline for architecture: {architecture}...")
    
    # Check dataset existence, generate mock data if missing
    if not os.path.exists(data_dir) or len(os.listdir(data_dir)) == 0:
        print("[WARNING] Training data not found. Creating mock dataset for local pipeline verification...")
        generate_mock_dataset(target_dir=data_dir, samples_per_class=10)

    # 1. Load Data Generators
    print("[INFO] Loading data generators with augmentation...")
    train_gen, val_gen = get_image_generators(
        data_dir=data_dir,
        img_size=DEFAULT_CONFIG["img_size"],
        batch_size=batch_size,
    )

    # 2. Build and Compile Model
    print(f"[INFO] Building model: {architecture}...")
    model = build_model(
        architecture=architecture,
        input_shape=(*DEFAULT_CONFIG["img_size"], 3),
        weights="imagenet" if architecture.lower() not in ["alexnet", "squeezenet"] else None,
        freeze_base=True,
    )
    model = compile_model(model, learning_rate=learning_rate)

    # 3. Configure Callbacks
    model_save_path = Path(save_dir) / f"{architecture.lower()}_best.h5"
    csv_log_path = Path(LOGS_DIR) / f"{architecture.lower()}_training_log.csv"

    callbacks = [
        ModelCheckpoint(
            filepath=str(model_save_path),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=DEFAULT_CONFIG["patience_es"],
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.2,
            patience=DEFAULT_CONFIG["patience_lr"],
            min_lr=1e-6,
            verbose=1,
        ),
        CSVLogger(str(csv_log_path)),
    ]

    # 4. Train Stage 1 (Frozen Base)
    print(f"[TRAIN] Training Stage 1 ({epochs} epochs)...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1,
    )

    # 5. Optional Fine-Tuning Stage 2
    if fine_tune and architecture.lower() not in ["alexnet", "squeezenet"]:
        print(f"[TRAIN] Unfreezing top {fine_tune_layers} layers for fine-tuning...")
        for layer in model.layers[-fine_tune_layers:]:
            if not isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = True

        model = compile_model(model, learning_rate=DEFAULT_CONFIG["fine_tune_lr"])
        print("[TRAIN] Training Stage 2 (Fine-tuning)...")
        ft_history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs + 15,
            initial_epoch=epochs,
            callbacks=callbacks,
            verbose=1,
        )

    # 6. Save Plot
    plot_path = Path(OUTPUTS_DIR) / f"{architecture.lower()}_learning_curves.png"
    plot_training_history(history, model_name=architecture, save_path=str(plot_path))
    print(f"[INFO] Learning curves saved to: {plot_path}")
    print(f"[SUCCESS] Model saved to: {model_save_path}")

    return model, history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CNN for Plant Seedlings Classification")
    parser.add_argument("--model", type=str, default="ResNet50", choices=SUPPORTED_ARCHITECTURES, help="Architecture to train")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Initial learning rate")
    parser.add_argument("--fine_tune", action="store_true", help="Enable fine-tuning stage")
    parser.add_argument("--data_dir", type=str, default=str(RAW_TRAIN_DIR), help="Dataset root directory")

    args = parser.parse_args()
    train(
        architecture=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        data_dir=args.data_dir,
        fine_tune=args.fine_tune,
    )
