"""
Data handling, preprocessing, and augmentation pipeline for Plant Seedlings Classification.
"""

import os
import shutil
import random
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

try:
    from .config import (
        CLASS_NAMES,
        NUM_CLASSES,
        DEFAULT_CONFIG,
        DATA_DIR,
        RAW_TRAIN_DIR,
        RAW_TEST_DIR,
    )
except ImportError:
    from config import (
        CLASS_NAMES,
        NUM_CLASSES,
        DEFAULT_CONFIG,
        DATA_DIR,
        RAW_TRAIN_DIR,
        RAW_TEST_DIR,
    )


def get_image_generators(
    data_dir=RAW_TRAIN_DIR,
    img_size=DEFAULT_CONFIG["img_size"],
    batch_size=DEFAULT_CONFIG["batch_size"],
    validation_split=DEFAULT_CONFIG["validation_split"],
    augment_config=DEFAULT_CONFIG["augmentation"],
):
    """
    Creates standard training and validation Keras ImageDataGenerators with data augmentation.
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    if not os.path.exists(data_dir):
        raise FileNotFoundError(
            f"Dataset directory not found at: {data_dir}. "
            f"Run download_dataset.py or generate_mock_dataset() first."
        )

    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=augment_config.get("rotation_range", 40),
        width_shift_range=augment_config.get("width_shift_range", 0.2),
        height_shift_range=augment_config.get("height_shift_range", 0.2),
        shear_range=augment_config.get("shear_range", 0.2),
        zoom_range=augment_config.get("zoom_range", 0.2),
        horizontal_flip=augment_config.get("horizontal_flip", True),
        vertical_flip=augment_config.get("vertical_flip", True),
        fill_mode=augment_config.get("fill_mode", "nearest"),
        validation_split=validation_split,
    )

    # Only rescaling for validation/testing
    val_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        validation_split=validation_split,
    )

    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        subset="training",
        shuffle=True,
        seed=DEFAULT_CONFIG["seed"],
    )

    val_generator = val_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
        seed=DEFAULT_CONFIG["seed"],
    )

    return train_generator, val_generator


def create_tf_datasets(
    data_dir=RAW_TRAIN_DIR,
    img_size=DEFAULT_CONFIG["img_size"],
    batch_size=DEFAULT_CONFIG["batch_size"],
    validation_split=DEFAULT_CONFIG["validation_split"],
):
    """
    Creates high-performance tf.data.Dataset pipelines with caching and prefetching.
    """
    import tensorflow as tf

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=validation_split,
        subset="training",
        seed=DEFAULT_CONFIG["seed"],
        image_size=img_size,
        batch_size=batch_size,
        label_mode="categorical",
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=validation_split,
        subset="validation",
        seed=DEFAULT_CONFIG["seed"],
        image_size=img_size,
        batch_size=batch_size,
        label_mode="categorical",
    )

    # Normalization layer
    normalization_layer = tf.keras.layers.Rescaling(1.0 / 255)

    # Augmentation layer for training
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.2),
        tf.keras.layers.RandomTranslation(0.1, 0.1),
    ])

    train_ds = train_ds.map(
        lambda x, y: (data_augmentation(normalization_layer(x)), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )
    val_ds = val_ds.map(
        lambda x, y: (normalization_layer(x), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds


def preprocess_image(image_input, target_size=DEFAULT_CONFIG["img_size"]):
    """
    Preprocess a single image (filepath, numpy array, or PIL Image) for model inference.
    Returns normalized numpy array with shape (1, height, width, 3).
    """
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, np.ndarray):
        if image_input.dtype == np.uint8:
            img = Image.fromarray(image_input)
        else:
            img = Image.fromarray((image_input * 255).astype(np.uint8))
        if img.mode != "RGB":
            img = img.convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    img = img.resize(target_size, Image.Resampling.BILINEAR)
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_batch = np.expand_dims(img_array, axis=0)
    return img_batch


def generate_mock_dataset(target_dir=RAW_TRAIN_DIR, samples_per_class=5):
    """
    Generates synthetic seedling-like sample images for all 12 classes
    to allow immediate development, local testing, and automated checks
    even without downloading the multi-GB Kaggle dataset.
    """
    os.makedirs(target_dir, exist_ok=True)
    class_palette = {
        "Black-grass": (34, 139, 34),
        "Charlock": (154, 205, 50),
        "Cleavers": (46, 139, 87),
        "Common Chickweed": (107, 142, 35),
        "Common wheat": (218, 165, 32),
        "Fat Hen": (85, 107, 47),
        "Loose Silky-bent": (60, 179, 113),
        "Maize": (255, 215, 0),
        "Scentless Mayweed": (144, 238, 144),
        "Shepherds Purse": (32, 178, 170),
        "Small-flowered Cranesbill": (128, 128, 0),
        "Sugar beet": (0, 100, 0),
    }

    for class_name in CLASS_NAMES:
        class_folder = Path(target_dir) / class_name
        os.makedirs(class_folder, exist_ok=True)

        for i in range(samples_per_class):
            img_path = class_folder / f"sample_{i+1}.png"
            if not img_path.exists():
                # Create synthetic seedling on soil background
                img = Image.new("RGB", (224, 224), color=(60 + random.randint(-10, 10), 40 + random.randint(-5, 5), 25 + random.randint(-5, 5)))
                draw = ImageDraw.Draw(img)

                # Draw stem and leaf shapes
                base_color = class_palette.get(class_name, (34, 139, 34))
                stem_color = (max(0, base_color[0] - 20), max(0, base_color[1] - 20), base_color[2])
                
                # Draw stem
                draw.line([(112, 180), (112 + random.randint(-10, 10), 100)], fill=stem_color, width=4)
                
                # Draw leaves
                for _ in range(random.randint(2, 5)):
                    lx = random.randint(70, 150)
                    ly = random.randint(70, 130)
                    draw.ellipse([lx, ly, lx + random.randint(20, 45), ly + random.randint(15, 30)], fill=base_color)

                img = img.filter(ImageFilter.SMOOTH)
                img.save(img_path)

    print(f"[SUCCESS] Generated mock dataset at {target_dir} ({samples_per_class} images/class across {len(CLASS_NAMES)} classes).")


if __name__ == "__main__":
    generate_mock_dataset()
