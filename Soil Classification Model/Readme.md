 # Soil Type Classification Model

This project is a **Deep Learning model** for classifying different types of soil using images. The model uses **MobileNetV2** as a base and has been fine-tuned to predict six types of soil:

- **Alluvial soil**  
- **Clayey soils**  
- **Laterite soil**  
- **Loamy soil**  
- **Sandy loam**  
- **Sandy soil**

---

## Dataset
- Dataset Link: https://www.kaggle.com/datasets/matshidiso/soil-types
- The dataset contains images of six soil types.  
- Data augmentation was applied to increase dataset diversity and improve model generalization.  
- Augmentation techniques used: rotation, width/height shift, shear, zoom, horizontal & vertical flip, and brightness adjustment.  

---

## Model Architecture

- **Base Model:** MobileNetV2 (pre-trained on ImageNet)  
- **Top Layers:** Fine-tuned dense layers for soil classification  
- **Loss Function:** Categorical Crossentropy  
- **Optimizer:** Adam  
- **Metrics:** Accuracy  

---

## Training Details

- Class weights were used to handle class imbalance.  
- Callbacks used:  
  - EarlyStopping  
  - ReduceLROnPlateau  
- Input image size: 150x150 pixels  
- Final validation dataset: 726 images across 6 classes  

---

## Model Performance

### Classification Report

| Class         | Precision | Recall | F1-score | Support |
|---------------|-----------|--------|----------|---------|
| Alluvial soil | 0.75      | 0.33   | 0.46     | 55      |
| Clayey soils  | 1.00      | 0.36   | 0.53     | 144     |
| Laterite soil | 1.00      | 0.36   | 0.53     | 145     |
| Loamy soil    | 0.62      | 0.88   | 0.73     | 97      |
| Sandy loam    | 0.61      | 0.90   | 0.73     | 126     |
| Sandy soil    | 0.57      | 0.99   | 0.72     | 159     |

- **Overall Accuracy:** 0.66  
- **Macro Avg:** Precision: 0.76 | Recall: 0.64 | F1-score: 0.62  
- **Weighted Avg:** Precision: 0.77 | Recall: 0.66 | F1-score: 0.63  

**Observation:**  
- The model performs very well on Loamy, Sandy loam, and Sandy soil.  
- Misclassification occurs mostly between **Alluvial and Clayey soils**.  
- Further augmentation or more training images for minority classes can improve performance.  

---

## Usage

### Load the model and predict single image with confidence 
```python
from tensorflow.keras.models import load_model

model = load_model("soil_classification_model.h5")
from tensorflow.keras.preprocessing import image
import numpy as np


# Load and preprocess image
img_path = "path_to_new_image.jpg"
img = image.load_img(img_path, target_size=(150, 150))
x = image.img_to_array(img)/255.0
x = np.expand_dims(x, axis=0)

# Make prediction
pred = model.predict(x)
pred_class = np.argmax(pred)
confidence = pred[0][pred_class]

print(f"Predicted Soil Type: {class_labels[pred_class]}")
print(f"Confidence: {confidence:.2f}")



