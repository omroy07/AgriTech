# utils.py
import numpy as np
import torch
import torch.nn as nn
import joblib
from PIL import Image
import torchvision.transforms as transforms
import os
from disease_prediction.model import PlantDiseaseNet

# Class labels (update if needed)
class_names = [
    'Apple___Black_rot', 'Apple___healthy',
    'Corn___Cercospora_leaf_spot', 'Corn___Common_rust',
    'Corn___healthy', 'Grape___Black_rot', 'Grape___Esca',
    'Grape___healthy', 'Potato___Early_blight', 'Potato___Late_blight',
    'Potato___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight',
    'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites', 'Tomato___Target_Spot', 'Tomato___Yellow_Leaf_Curl_Virus',
    'Tomato___mosaic_virus', 'Tomato___healthy'
]

# Add this in utils.py
class_descriptions = {
    'Apple___Black_rot': 'Black rot is a fungal disease. Remove affected fruit and apply fungicide.',
    'Apple___healthy': 'The apple plant is healthy.',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 'Gray leaf spot detected. Use resistant varieties and rotate crops.',
    'Corn_(maize)___Common_rust_': 'Common rust detected. Remove infected leaves and apply fungicide.',
    'Corn_(maize)___healthy': 'The corn plant is healthy.',
    'Grape___Black_rot': 'Black rot detected on grapes. Remove infected parts.',
    'Grape___Esca_(Black_Measles)': 'Esca disease detected. Prune and burn affected wood.',
    'Grape___healthy': 'The grape plant is healthy.',
    'Potato___Early_blight': 'Early blight detected. Use certified disease-free seeds.',
    'Potato___Late_blight': 'Late blight detected. Avoid overhead irrigation and apply fungicide.',
    'Potato___healthy': 'The potato plant is healthy.',
    'Tomato___Bacterial_spot': 'Bacterial spot found. Use copper-based sprays.',
    'Tomato___Early_blight': 'Early blight detected. Improve air circulation and remove infected leaves.',
    'Tomato___Late_blight': 'Late blight found. Remove and destroy infected plants.',
    'Tomato___Leaf_Mold': 'Leaf mold detected. Reduce humidity and ensure ventilation.',
    'Tomato___Septoria_leaf_spot': 'Septoria leaf spot detected. Remove lower leaves and apply fungicide.',
    'Tomato___Spider_mites Two-spotted_spider_mite': 'Spider mites present. Use insecticidal soap.',
    'Tomato___Target_Spot': 'Target spot found. Use proper spacing and apply fungicide.',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Viral infection found. Remove infected plants.',
    'Tomato___Tomato_mosaic_virus': 'Mosaic virus detected. Control aphid population.',
    'Tomato___healthy': 'The tomato plant is healthy.'
}

def load_pytorch_model(model_path):
    """Load PyTorch model from .pkl file"""
    try:
        # Load the model state dict
        model_state = joblib.load(model_path)
        
        # Create model instance
        model = PlantDiseaseNet(num_classes=len(class_names))
        
        # Load the state dict
        model.load_state_dict(model_state)
        model.eval()  # Set to evaluation mode
        
        # Move to GPU if available
        if torch.cuda.is_available():
            model = model.cuda()
            print(f"Model moved to GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("CUDA not available, using CPU")
        
        return model
    except Exception as e:
        print(f"Error loading PyTorch model: {e}")
        return None

def predict_image_pytorch(model, img_path):
    """Predict using PyTorch model"""
    try:
        # Define image transformations
        transform = transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Load and transform image
        img = Image.open(img_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0)  # Add batch dimension
        
        # Move to GPU if available
        if torch.cuda.is_available():
            img_tensor = img_tensor.cuda()
        
        # Make prediction
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            predicted_index = torch.argmax(probabilities, dim=1).item()
        
        predicted_class = class_names[predicted_index]
        description = class_descriptions.get(predicted_class, "No description available.")
        
        return predicted_class, description
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Error", f"Prediction failed: {str(e)}"

# Keep the old function names for compatibility
def load_keras_model(model_path):
    """Compatibility function - now loads PyTorch model"""
    return load_pytorch_model(model_path)

def predict_image_keras(model, img_path):
    """Compatibility function - now uses PyTorch prediction"""
    return predict_image_pytorch(model, img_path)