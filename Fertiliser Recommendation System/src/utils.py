# src/utils.py

from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Encoders for Soil Type, Crop Type, Fertilizer Name
soil_encoder = LabelEncoder()
crop_encoder = LabelEncoder()
fertilizer_encoder = LabelEncoder()

def encode_features(df):
    df['Soil Type'] = soil_encoder.fit_transform(df['Soil Type'])
    df['Crop Type'] = crop_encoder.fit_transform(df['Crop Type'])
    df['Fertilizer Name'] = fertilizer_encoder.fit_transform(df['Fertilizer Name'])
    return df, soil_encoder, crop_encoder, fertilizer_encoder

def decode_fertilizer(encoded_label):
    return fertilizer_encoder.inverse_transform([encoded_label])[0]
