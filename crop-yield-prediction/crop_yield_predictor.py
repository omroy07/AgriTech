import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import joblib

# Load dataset
df = pd.read_csv("data/crop_yield_dataset.csv")  # Replace with your filename

# Rename columns if needed
df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

# Encode categorical variables
le_area = LabelEncoder()
le_item = LabelEncoder()

df['area_encoded'] = le_area.fit_transform(df['area'])
df['item_encoded'] = le_item.fit_transform(df['item'])

# Feature selection
features = ['area_encoded', 'item_encoded', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']
target = 'hg/ha_yield'

X = df[features]
y = df[target]

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
from sklearn.metrics import r2_score

r2 = r2_score(y_test, y_pred)
print(f"✅ Model trained. Prediction Accuracy: {r2 * 100:.2f}%")


# Save model and encoders
joblib.dump(model, 'yield_predictor_model.pkl')
joblib.dump(le_area, 'area_encoder.pkl')
joblib.dump(le_item, 'item_encoder.pkl')
