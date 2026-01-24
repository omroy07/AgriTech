import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
csv_path = './Crop_recommendation.csv'
df = pd.read_csv(csv_path)

# Features and target
X = df.drop('label', axis=1)
y = df['label']

# Encode target labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y_encoded)

# Save model and label encoder
joblib.dump(clf, 'model/rf_model.pkl')
joblib.dump(le, 'model/label_encoder.pkl')

print('Model and label encoder saved successfully!')
