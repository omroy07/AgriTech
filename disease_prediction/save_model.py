# save_model.py
# Helper script to save your trained PyTorch model in the correct format

import torch
import joblib
from model import PlantDiseaseNet

def save_model_for_app(model_path, output_path='model.pkl'):
    """
    Save your trained PyTorch model in the format expected by the app
    
    Args:
        model_path: Path to your trained model (.pth or .pt file)
        output_path: Where to save the model for the app (default: model.pkl)
    """
    try:
        # Load your trained model
        model = PlantDiseaseNet(num_classes=38)  # Adjust num_classes as needed
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        model.eval()
        
        # Save the state dict using joblib (this is what the app expects)
        joblib.dump(model.state_dict(), output_path)
        print(f"Model saved successfully to {output_path}")
        print("The app can now load this model!")
        
    except Exception as e:
        print(f"Error saving model: {e}")
        print("\nAlternative method:")
        print("If you have a trained model, you can manually save it like this:")
        print("import joblib")
        print("joblib.dump(your_model.state_dict(), 'model.pkl')")

if __name__ == "__main__":
    print("PyTorch Model Saver for AgriTech App")
    print("=" * 40)
    print("This script helps you save your trained PyTorch model")
    print("in the format expected by the Disease Prediction app.")
    print()
    print("Usage:")
    print("1. Place your trained model file (.pth or .pt) in this directory")
    print("2. Update the model_path variable below")
    print("3. Run this script")
    print()
    
    # Update this path to your actual model file
    model_path = "your_trained_model.pth"  # Change this to your model file
    
    if model_path != "your_trained_model.pth":
        save_model_for_app(model_path)
    else:
        print("Please update the model_path variable to point to your trained model file.")
        print("Example: model_path = 'my_disease_model.pth'") 