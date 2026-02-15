import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split 
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# --- 1. CONFIGURATION & LOAD ---
DATA_PATH = "data/crop_yield_dataset.csv"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

try:
    df = pd.read_csv(DATA_PATH)
    # Clean column names: strip spaces, lowercase, replace spaces with underscores
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    print(f"✅ Dataset loaded. Shape: {df.shape}")
except FileNotFoundError:
    print(f"❌ Error: {DATA_PATH} not found. Please check the file path.")
    exit()

# --- 2. ENCODING & PREPROCESSING ---
# We use LabelEncoders but add a step to handle 'unseen' categories during inference
encoders = {}
categorical_cols = ['area', 'item']

for col in categorical_cols:
    le = LabelEncoder()
    # Adding a placeholder for unknown values if your dataset is small/evolving
    df[f'{col}_encoded'] = le.fit_transform(df[col])
    encoders[col] = le

# Define Features and Target based on your dataset columns
features = ['area_encoded', 'item_encoded', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']
target = 'hg/ha_yield'

# Ensure all feature columns exist before training
if not all(col in df.columns for col in features + [target]):
    missing = [col for col in features + [target] if col not in df.columns]
    print(f"❌ Missing columns in CSV: {missing}")
    exit()

X = df[features]
y = df[target]

# --- 3. TRAIN/TEST SPLIT ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

# --- 4. MODEL TRAINING ---
print("🚀 Training Random Forest Regressor...")
model = RandomForestRegressor(
    n_estimators=100, 
    max_depth=15,       # Prevents extreme overfitting
    n_jobs=-1,          # Uses all CPU cores for faster training
    random_state=42
)
model.fit(X_train, y_train)

# --- 5. EVALUATION ---
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("-" * 30)
print(f"📊 Model Performance:")
print(f"✅ R² Score (Accuracy): {r2 * 100:.2f}%")
print(f"✅ Mean Absolute Error: {mae:.2f} hg/ha")
print(f"✅ Root Mean Squared Error: {rmse:.2f} hg/ha")
print("-" * 30)

# --- 6. SAVE ARTIFACTS ---
# Saving everything into a 'models' folder for better organization
joblib.dump(model, os.path.join(MODEL_DIR, 'yield_predictor_model.pkl'))
joblib.dump(encoders['area'], os.path.join(MODEL_DIR, 'area_encoder.pkl'))
joblib.dump(encoders['item'], os.path.join(MODEL_DIR, 'item_encoder.pkl'))

print(f"💾 Model and encoders saved successfully in '{MODEL_DIR}/'")