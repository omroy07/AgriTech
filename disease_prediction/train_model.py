import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm
import os

# ===== CONFIG =====
DATA_DIR = "disease_prediction/tomato disease detection/Dataset"
MODEL_SAVE_PATH = "disease_prediction/model/plant_disease_resnet18.pth"
NUM_CLASSES = 38
BATCH_SIZE = 32
EPOCHS = 5
LR = 0.001

os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

# ===== TRANSFORMS =====
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ===== DATA =====
train_data = datasets.ImageFolder(DATA_DIR, transform=transform)
train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)

print(f"✅ Loaded {len(train_data)} images")

# ===== MODEL (ResNet18 – SAFE) =====
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ===== TRAINING =====
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0

    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f"Epoch {epoch+1} Loss: {running_loss/len(train_loader):.4f}")

# ===== SAVE CLEAN STATE_DICT =====
torch.save(model.state_dict(), MODEL_SAVE_PATH)
print(f"✅ Model saved safely at {MODEL_SAVE_PATH}")
