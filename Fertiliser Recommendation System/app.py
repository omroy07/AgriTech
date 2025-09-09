
import streamlit as st
from model import predict_fertilizer

# Page configuration
st.set_page_config(
    page_title="Fertilizer Recommendation System",
    page_icon="🌿",
    layout="centered"
)

# Custom CSS styling for improved visuals
st.markdown("""
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
        }
        .main-box {
            background-color: #f9f9f9;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .stButton > button {
            background-color: #2e8b57;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("🌾 Fertilizer Recommendation System")

st.markdown("Fill in the following information to get the most suitable fertilizer recommendation.")

# Input section
with st.form("fertilizer_form"):
    st.markdown('<div class="main-box">', unsafe_allow_html=True)

    # Environmental Inputs
    st.subheader("📈 Environmental Conditions")
    col1, col2, col3 = st.columns(3)
    with col1:
        temparature = st.number_input("Temparature (°C)", min_value=0.0, max_value=60.0, value=25.0)
    with col2:
        humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=60.0)
    with col3:
        moisture = st.number_input("Moisture (%)", min_value=0.0, max_value=100.0, value=50.0)

    # Soil and Crop Inputs
    st.subheader("🌱 Soil and Crop Details")
    soil_type = st.selectbox(
        "Soil Type", 
        ["Sandy", "Loamy", "Black", "Red", "Clayey"]
    )
    crop_type = st.selectbox(
        "Crop Type", 
        ["Wheat", "Cotton", "Maize", "Paddy", "Barley", "Ground Nuts"]
    )

    # Nutrients
    st.subheader("🧪 Soil Nutrient Levels")
    col4, col5, col6 = st.columns(3)
    with col4:
        nitrogen = st.number_input("Nitrogen (N)", min_value=0, max_value=140, value=60)
    with col5:
        potassium = st.number_input("Potassium (K)", min_value=0, max_value=140, value=50)
    with col6:
        phosphorous = st.number_input("Phosphorous (P)", min_value=0, max_value=140, value=40)

    submitted = st.form_submit_button("🔍 Recommend Fertilizer")

    st.markdown('</div>', unsafe_allow_html=True)

# Prediction logic
if submitted:
    try:
        recommendation = predict_fertilizer(
            temparature=temparature,
            humidity=humidity,
            moisture=moisture,
            soil_type=soil_type,
            crop_type=.crop_type,
            nitrogen=nitrogen,
            potassium=potassium,
            phosphorous=phosphorous
        )

        st.success(f"✅ **Recommended Fertilizer:** {recommendation}")
        st.balloons()
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        st.warning("Please check your input values and try again.")
