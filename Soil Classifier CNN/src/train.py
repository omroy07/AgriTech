# src/train.py

import os
from data_loader import get_data_generators
from model import build_cnn_model
from utils import plot_training_history

DATASET_DIR = "../dataset"
MODEL_PATH = "../saved_model/soil_classifier_cnn.h5"
IMG_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 20

def main():
    # Step 1: Load Data
    train_gen, val_gen = get_data_generators(DATASET_DIR, img_size=IMG_SIZE, batch_size=BATCH_SIZE)

    # Step 2: Build Model
    model = build_cnn_model(input_shape=(128, 128, 3), num_classes=train_gen.num_classes)

    # Step 3: Train Model
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS
    )

    # Step 4: Save Model
    os.makedirs("../saved_model", exist_ok=True)
    model.save(MODEL_PATH)
    print(f"[INFO] Model saved to {MODEL_PATH}")

    # Step 5: Plot training history
    os.makedirs("../images", exist_ok=True)
    plot_training_history(history)

if __name__ == "__main__":
    main()
