"""
CNN Architectures for Plant Seedlings Classification.
Includes ResNet50, AlexNet, VGG16, InceptionV3, MobileNetV2, DenseNet121, and SqueezeNet.
"""

import tensorflow as tf
from tensorflow.keras import layers, Model, Sequential
from tensorflow.keras.applications import (
    ResNet50,
    VGG16,
    InceptionV3,
    MobileNetV2,
    DenseNet121,
)

try:
    from .config import NUM_CLASSES, DEFAULT_CONFIG, SUPPORTED_ARCHITECTURES
except ImportError:
    from config import NUM_CLASSES, DEFAULT_CONFIG, SUPPORTED_ARCHITECTURES


def _build_head(base_output, num_classes=NUM_CLASSES, dropout_rate=0.4):
    """Adds a standard dense classification head."""
    x = layers.GlobalAveragePooling2D()(base_output)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(512, activation="relu")(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(dropout_rate / 2)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="classification_head", dtype="float32")(x)
    return outputs


def build_alexnet(input_shape=(224, 224, 3), num_classes=NUM_CLASSES):
    """
    Constructs an AlexNet architecture tailored for plant seedling classification.
    """
    inputs = layers.Input(shape=input_shape, name="input_image")

    # Layer 1
    x = layers.Conv2D(96, kernel_size=(11, 11), strides=(4, 4), padding="valid", activation="relu")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(x)

    # Layer 2
    x = layers.Conv2D(256, kernel_size=(5, 5), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(x)

    # Layer 3
    x = layers.Conv2D(384, kernel_size=(3, 3), padding="same", activation="relu")(x)

    # Layer 4
    x = layers.Conv2D(384, kernel_size=(3, 3), padding="same", activation="relu")(x)

    # Layer 5
    x = layers.Conv2D(256, kernel_size=(3, 3), padding="same", activation="relu")(x)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(x)

    # Classifier
    x = layers.Flatten()(x)
    x = layers.Dense(4096, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(4096, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="alexnet_output")(x)

    model = Model(inputs=inputs, outputs=outputs, name="AlexNet")
    return model


def _fire_module(x, squeeze_planes, expand_planes, name="fire"):
    """SqueezeNet Fire Module composed of squeeze and expand layers."""
    # Squeeze
    sq = layers.Conv2D(squeeze_planes, (1, 1), activation="relu", padding="valid", name=f"{name}_squeeze")(x)
    # Expand 1x1
    exp1x1 = layers.Conv2D(expand_planes, (1, 1), activation="relu", padding="valid", name=f"{name}_expand1x1")(sq)
    # Expand 3x3
    exp3x3 = layers.Conv2D(expand_planes, (3, 3), activation="relu", padding="same", name=f"{name}_expand3x3")(sq)
    # Concat
    out = layers.concatenate([exp1x1, exp3x3], axis=-1, name=f"{name}_concat")
    return out


def build_squeezenet(input_shape=(224, 224, 3), num_classes=NUM_CLASSES):
    """
    Constructs a SqueezeNet architecture (v1.1) optimized for lightweight seedling classification.
    """
    inputs = layers.Input(shape=input_shape, name="input_image")

    # Initial Conv
    x = layers.Conv2D(64, (3, 3), strides=(2, 2), padding="same", activation="relu", name="conv1")(inputs)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding="same", name="maxpool1")(x)

    # Fire modules 2 & 3
    x = _fire_module(x, squeeze_planes=16, expand_planes=64, name="fire2")
    x = _fire_module(x, squeeze_planes=16, expand_planes=64, name="fire3")
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding="same", name="maxpool3")(x)

    # Fire modules 4 & 5
    x = _fire_module(x, squeeze_planes=32, expand_planes=128, name="fire4")
    x = _fire_module(x, squeeze_planes=32, expand_planes=128, name="fire5")
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding="same", name="maxpool5")(x)

    # Fire modules 6, 7, 8, 9
    x = _fire_module(x, squeeze_planes=48, expand_planes=192, name="fire6")
    x = _fire_module(x, squeeze_planes=48, expand_planes=192, name="fire7")
    x = _fire_module(x, squeeze_planes=64, expand_planes=256, name="fire8")
    x = _fire_module(x, squeeze_planes=64, expand_planes=256, name="fire9")

    # Classifier
    x = layers.Dropout(0.5, name="drop9")(x)
    x = layers.Conv2D(num_classes, (1, 1), padding="valid", name="conv10")(x)
    x = layers.GlobalAveragePooling2D(name="avgpool10")(x)
    outputs = layers.Activation("softmax", name="squeezenet_output")(x)

    model = Model(inputs=inputs, outputs=outputs, name="SqueezeNet")
    return model


def build_model(
    architecture="ResNet50",
    input_shape=(224, 224, 3),
    num_classes=NUM_CLASSES,
    weights="imagenet",
    freeze_base=True,
):
    """
    Factory method to instantiate any of the 7 supported CNN architectures.
    """
    arch = architecture.strip().lower()

    if arch in ["resnet50", "resnet"]:
        base_model = ResNet50(weights=weights, include_top=False, input_shape=input_shape)
        if freeze_base and weights is not None:
            base_model.trainable = False
        outputs = _build_head(base_model.output, num_classes=num_classes)
        model = Model(inputs=base_model.input, outputs=outputs, name="ResNet50")

    elif arch in ["vgg16", "vgg"]:
        base_model = VGG16(weights=weights, include_top=False, input_shape=input_shape)
        if freeze_base and weights is not None:
            base_model.trainable = False
        outputs = _build_head(base_model.output, num_classes=num_classes)
        model = Model(inputs=base_model.input, outputs=outputs, name="VGG16")

    elif arch in ["inceptionv3", "inception"]:
        base_model = InceptionV3(weights=weights, include_top=False, input_shape=input_shape)
        if freeze_base and weights is not None:
            base_model.trainable = False
        outputs = _build_head(base_model.output, num_classes=num_classes)
        model = Model(inputs=base_model.input, outputs=outputs, name="InceptionV3")

    elif arch in ["mobilenetv2", "mobilenet"]:
        base_model = MobileNetV2(weights=weights, include_top=False, input_shape=input_shape)
        if freeze_base and weights is not None:
            base_model.trainable = False
        outputs = _build_head(base_model.output, num_classes=num_classes)
        model = Model(inputs=base_model.input, outputs=outputs, name="MobileNetV2")

    elif arch in ["densenet121", "densenet"]:
        base_model = DenseNet121(weights=weights, include_top=False, input_shape=input_shape)
        if freeze_base and weights is not None:
            base_model.trainable = False
        outputs = _build_head(base_model.output, num_classes=num_classes)
        model = Model(inputs=base_model.input, outputs=outputs, name="DenseNet121")

    elif arch in ["alexnet"]:
        model = build_alexnet(input_shape=input_shape, num_classes=num_classes)

    elif arch in ["squeezenet"]:
        model = build_squeezenet(input_shape=input_shape, num_classes=num_classes)

    else:
        raise ValueError(
            f"Unsupported architecture '{architecture}'. Supported: {SUPPORTED_ARCHITECTURES}"
        )

    return model


def compile_model(model, learning_rate=DEFAULT_CONFIG["learning_rate"], optimizer_type="adam"):
    """Compiles model with categorical cross-entropy and accuracy/top-k metrics."""
    if optimizer_type.lower() == "adam":
        opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    elif optimizer_type.lower() == "sgd":
        opt = tf.keras.optimizers.SGD(learning_rate=learning_rate, momentum=0.9, nesterov=True)
    elif optimizer_type.lower() == "rmsprop":
        opt = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
    else:
        opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)

    model.compile(
        optimizer=opt,
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def build_ensemble(models, input_shape=(224, 224, 3)):
    """Creates a soft-voting ensemble across multiple trained models."""
    inputs = layers.Input(shape=input_shape, name="ensemble_input")
    outputs = [model(inputs) for model in models]
    avg_output = layers.Average(name="ensemble_average")(outputs)
    ensemble_model = Model(inputs=inputs, outputs=avg_output, name="SeedlingEnsemble")
    return ensemble_model
