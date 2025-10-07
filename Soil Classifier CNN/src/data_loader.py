# src/data_loader.py

from tensorflow.keras.preprocessing.image import ImageDataGenerator

def get_data_generators(data_dir, img_size=(128, 128), batch_size=32, val_split=0.2):
    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=val_split
    )

    train_generator = datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    val_generator = datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation',
        shuffle=True
    )

    return train_generator, val_generator
