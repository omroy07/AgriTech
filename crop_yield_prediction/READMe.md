# 🌾 Crop Yield Predictor

A machine learning-based system to predict **crop yield (hg/ha)** using historical agricultural data including crop type, geographical area, rainfall, pesticide usage, and temperature. This tool aims to support **farmers and agricultural planners** by providing an estimate of crop production, helping them make informed decisions.

---
[!UI screenshot](assets/1a.jpeg)
[!UI screenshot](assets/1b.jpeg)
[!UI screenshot](assets/image.png)
## 📌 Features

- 📍 **Input**: Area, Crop Type, Average Rainfall, Pesticides Used, Average Temperature  
- 📤 **Output**: Predicted Yield (in hectograms per hectare - hg/ha)
- 🧠 Uses a **Random Forest Regressor** trained on real-world data
- 🔄 Includes support for categorical encoding of locations and crops
- 💾 Saves trained model and encoders for easy reuse
- 🧪 Prediction script for real-time yield estimates

---

## 🗃️ Dataset

- **Source**: Kaggle
- **Columns Used**:
  - `Area`: Geographic location (e.g., Albania)
  - `Item`: Crop name (e.g., Maize, Potatoes)
  - `average_rainfall`
  - `pesticides`
  - `avg_temp`
  - `hg/ha_yield`: Target label

---

## 🚀 Getting Started

### 🔧 Installation

```bash
pip install pandas scikit-learn joblib
