import streamlit as st
import joblib
import numpy as np

# Load model and encoders
model = joblib.load('yield_predictor_model.pkl')
le_area = joblib.load('area_encoder.pkl')
le_item = joblib.load('item_encoder.pkl')

# Page config
st.set_page_config(page_title="Crop Yield Predictor", page_icon="🌾", layout="centered")

# Title
st.title("🌾 Crop Yield Predictor")
st.write("Predict agricultural crop yield (in hg/ha) using region and climate data.")

# Input form
with st.form("input_form"):
    st.subheader("Enter Details:")

    col1, col2 = st.columns(2)

    with col1:
        area = st.selectbox("Select Area", le_area.classes_)
        rainfall = st.number_input("Average Rainfall (mm/year)", min_value=0.0, step=1.0, value=100.0)
        temperature = st.number_input("Average Temperature (°C)", min_value=-10.0, max_value=60.0, step=0.1, value=25.0)

    with col2:
        item = st.selectbox("Select Crop", le_item.classes_)
        pesticide = st.number_input("Pesticide Usage (tonnes)", min_value=0.0, step=0.1, value=5.0)

    submitted = st.form_submit_button("Predict Yield")

# Prediction
if submitted:
    try:
        area_encoded = le_area.transform([area])[0]
        item_encoded = le_item.transform([item])[0]
        input_data = np.array([[area_encoded, item_encoded, rainfall, pesticide, temperature]])
        prediction = model.predict(input_data)[0]

        st.success(f"📦 Predicted Yield: {prediction:.2f} hg/ha")
    except Exception as e:
        st.error(f"Error: {e}")
