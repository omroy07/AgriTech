# src/train.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import joblib
import os
from utils import encode_features, soil_encoder, crop_encoder, fertilizer_encoder

# Load dataset
df = pd.read_csv('../data/fertilizer_dataset.csv')

# Encode categorical variables
df, soil_encoder, crop_encoder, fertilizer_encoder = encode_features(df)

# Features and target
X = df.drop(['Fertilizer Name'], axis=1)
y = df['Fertilizer Name']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hyperparameter tuning using GridSearchCV
param_grid = {
    'n_estimators': [50, 100, 150, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)

# Best model
best_clf = grid_search.best_estimator_

# Evaluate model
y_pred = best_clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"[INFO] Model accuracy after tuning: {accuracy:.2f}")

# Create directory to save model and encoders
if not os.path.exists('../saved_model'):
    os.makedirs('../saved_model')

# Save model and encoders
joblib.dump(best_clf, '../saved_model/fertilizer_model.pkl')
joblib.dump(soil_encoder, '../saved_model/soil_encoder.pkl')
joblib.dump(crop_encoder, '../saved_model/crop_encoder.pkl')
joblib.dump(fertilizer_encoder, '../saved_model/fertilizer_encoder.pkl')

print("[INFO] Model and encoders saved successfully.")
