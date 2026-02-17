import streamlit as st
import joblib
import numpy as np
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="AgriPredict | Crop Yield AI", 
    page_icon="🌾", 
    layout="wide"
)

# --- 2. ASSET LOADING (Optimized with Caching) ---
@st.cache_resource
def load_assets():
    """Load model and encoders once and cache them in memory."""
    try:
        # Adjust paths if your files are in a 'models/' folder
        model = joblib.load('models/yield_predictor_model.pkl')
        le_area = joblib.load('models/area_encoder.pkl')
        le_item = joblib.load('models/item_encoder.pkl')
        return model, le_area, le_item
    except Exception as e:
        st.error(f"⚠️ Error loading model files: {e}")
        return None, None, None

model, le_area, le_item = load_assets()

# --- 3. UI HEADER ---
st.title("🌾 Crop Yield Prediction Dashboard")
st.markdown("""
    Predict agricultural crop yield (in **hg/ha**) by providing regional data and climate parameters. 
    *This model uses Random Forest regression trained on global agricultural datasets.*
""")
st.divider()

# --- 4. INPUT SECTION ---
if model:
    with st.container():
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.subheader("📍 Location & Crop")
            area = st.selectbox("Select Country/Region", le_area.classes_)
            item = st.selectbox("Select Crop Type", le_item.classes_)
            
        with col2:
            st.subheader("🌦️ Environmental Factors")
            rainfall = st.number_input("Average Rainfall (mm/year)", min_value=0.0, max_value=10000.0, value=1200.0)
            pesticide = st.number_input("Pesticide Usage (tonnes)", min_value=0.0, max_value=500000.0, value=50.0)
            temperature = st.slider("Average Temperature (°C)", -10.0, 50.0, 25.0)

    # --- 5. PREDICTION LOGIC ---
    st.write("") # Spacer
    if st.button("Calculate Predicted Yield", type="primary", use_container_width=True):
        try:
            # Encoding inputs
            area_encoded = le_area.transform([area])[0]
            item_encoded = le_item.transform([item])[0]
            
            # Feature array: [area, item, rainfall, pesticide, temp]
            input_data = np.array([[area_encoded, item_encoded, rainfall, pesticide, temperature]])
            
            # Predict
            prediction = model.predict(input_data)[0]
            
            # Display Results
            st.divider()
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col2:
                st.metric(label="Predicted Yield", value=f"{prediction:,.2f} hg/ha")
                
            if prediction > 0:
                st.success(f"Calculation complete for **{item}** in **{area}**.")
            else:
                st.warning("The model predicts a negligible yield for these specific conditions.")
                
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")

else:
    st.warning("Please ensure 'yield_predictor_model.pkl', 'area_encoder.pkl', and 'item_encoder.pkl' are in the project directory.")

# --- 6. FOOTER ---
st.divider()
st.caption("Developed for Agricultural Data Analysis | Powered by Scikit-Learn & Streamlit")
