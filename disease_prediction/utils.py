import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image

# ================= IMAGE TRANSFORM =================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ================= LOAD MODEL =================
def load_pytorch_model(model_path):
    # Load state_dict
    state_dict = torch.load(model_path, map_location="cpu")

    # Infer number of classes
    num_classes = state_dict["fc.weight"].shape[0]
    print(f"✅ Model expects {num_classes} classes")

    # Build same architecture
    model = resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    # Load weights
    model.load_state_dict(state_dict)
    model.eval()

    return model

# ================= PREDICT =================
def predict_image_pytorch(model, img_path):
    img = Image.open(img_path).convert("RGB")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        probs = torch.softmax(outputs, dim=1)
        confidence, idx = torch.max(probs, 1)

    return idx.item(), round(confidence.item() * 100, 2)
