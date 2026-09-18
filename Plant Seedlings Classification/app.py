"""
Streamlit Web Dashboard for Plant Seedlings Classification using CNN Architectures.
"""

import os
import sys
import io
import time
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

# Setup system path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from src.config import (
    CLASS_NAMES,
    PLANT_SPECIES_INFO,
    SUPPORTED_ARCHITECTURES,
    BENCHMARK_RESULTS,
    RAW_TRAIN_DIR,
    IMAGES_DIR,
)
from src.predict import SeedlingClassifier
from src.evaluate import generate_benchmark_summary
from src.data_loader import generate_mock_dataset
from src.visualize import plot_confusion_matrix, plot_architecture_comparisons

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Plant Seedlings Classification | CNN Suite",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b4332;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #40916c;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 5px solid #2d6a4f;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .weed-badge {
        background-color: #ff4d4f;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .crop-badge {
        background-color: #52c41a;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .advisory-box {
        background-color: #f6ffed;
        border: 1px solid #b7eb8f;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 1.05rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_classifier(architecture):
    """Loads and caches the model for real-time inference."""
    return SeedlingClassifier(architecture=architecture)


# --- Sidebar ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.markdown("### ⚙️ Model Settings")

    selected_architecture = st.selectbox(
        "Select CNN Architecture",
        SUPPORTED_ARCHITECTURES,
        index=0,
        help="Choose from 7 deep learning architectures.",
    )

    use_tta = st.checkbox(
        "Test-Time Augmentation (TTA)",
        value=True,
        help="Averages predictions across multiple image transformations for higher precision.",
    )

    top_k_val = st.slider("Top Predictions (Top-K)", min_value=1, max_value=5, value=3)

    st.markdown("---")
    st.markdown("### 🌾 Species Database")
    st.markdown(f"**Total Species:** {len(CLASS_NAMES)}")
    weed_count = sum(1 for info in PLANT_SPECIES_INFO.values() if info.get("type") == "Weed")
    crop_count = len(CLASS_NAMES) - weed_count
    st.markdown(f"- 🔴 **Weeds:** {weed_count} species\n- 🟢 **Crops:** {crop_count} species")
    
    st.markdown("---")
    st.caption("AgriTech Open-Source Seedling Intelligence System")


# --- Main Dashboard Header ---
st.markdown('<div class="main-header">🌱 Automated Plant Seedlings Classification</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Multi-architecture CNN suite for precise crop identification and selective weed control</div>',
    unsafe_allow_html=True,
)

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🌿 Live Classification",
    "📊 Model Benchmarks",
    "📈 Training & Metrics Explorer",
    "📁 Batch Inference & Export",
])

# ==========================================
# TAB 1: Live Classification
# ==========================================
with tab1:
    col1, col2 = st.columns([1.1, 1.3], gap="large")

    with col1:
        st.subheader("1. Provide Seedling Image")
        input_source = st.radio(
            "Input Method",
            ["Upload Image", "Select Sample Seedling"],
            horizontal=True,
        )

        image_to_classify = None

        if input_source == "Upload Image":
            uploaded_file = st.file_uploader(
                "Upload a seedling photo (JPG, PNG, JPEG)",
                type=["jpg", "jpeg", "png"],
            )
            if uploaded_file is not None:
                image_to_classify = Image.open(uploaded_file).convert("RGB")
                st.image(image_to_classify, caption="Uploaded Image", use_container_width=True)
        else:
            # Check for sample images in Images/ or Dataset/
            sample_options = list(CLASS_NAMES)
            selected_sample_class = st.selectbox("Choose Seedling Class Sample", sample_options)
            
            # Find or generate sample
            sample_dir = Path(RAW_TRAIN_DIR) / selected_sample_class
            if not sample_dir.exists() or len(os.listdir(sample_dir)) == 0:
                generate_mock_dataset(RAW_TRAIN_DIR, samples_per_class=2)
            
            sample_images = list(sample_dir.glob("*.png")) + list(sample_dir.glob("*.jpg"))
            if sample_images:
                image_to_classify = Image.open(sample_images[0]).convert("RGB")
                st.image(image_to_classify, caption=f"Sample: {selected_sample_class}", use_container_width=True)

    with col2:
        st.subheader("2. Prediction & Agricultural Advisory")

        if image_to_classify is not None:
            with st.spinner(f"Classifying with {selected_architecture}..."):
                classifier = get_classifier(selected_architecture)
                start_time = time.time()
                result = classifier.predict(image_to_classify, top_k=top_k_val, use_tta=use_tta)
                infer_latency = (time.time() - start_time) * 1000

            top_pred = result["prediction"]
            plant_type = result["type"]
            conf_val = result["confidence"]
            advisory = result["agricultural_advisory"]

            # Result Header Card
            st.markdown(
                f"""
                <div class="metric-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2 style="margin: 0; color: #1b4332;">{top_pred}</h2>
                        <span class="{ 'weed-badge' if plant_type == 'Weed' else 'crop-badge' }">{plant_type.upper()}</span>
                    </div>
                    <p style="margin: 4px 0 0 0; font-style: italic; color: #555;">Scientific Name: {advisory['scientific_name']}</p>
                    <p style="margin: 6px 0 0 0; font-size: 1.1rem;">Confidence: <strong>{result['confidence_percent']}</strong> | Latency: <strong>{infer_latency:.1f} ms</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Confidence Progress Bar
            st.progress(float(min(1.0, max(0.0, conf_val))))

            # Agricultural Action Box
            st.markdown(
                f"""
                <div class="advisory-box">
                    <h4 style="margin-top: 0; color: #2d6a4f;">🚜 Agronomic Recommendation</h4>
                    <p><strong>Threat Severity:</strong> {advisory['threat_severity']}</p>
                    <p><strong>Action Required:</strong> {advisory['recommended_action']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Top-K Probabilities Bar Chart
            st.markdown("#### 📊 Top Prediction Probabilities")
            top_k_df = pd.DataFrame([
                {
                    "Species": item["class_name"],
                    "Probability (%)": item["confidence"] * 100,
                    "Type": item["type"],
                }
                for item in result["top_k"]
            ])
            st.bar_chart(top_k_df.set_index("Species")["Probability (%)"])

        else:
            st.info("👆 Please upload an image or select a sample seedling to view classification and agronomic advisory.")


# ==========================================
# TAB 2: Model Benchmarks & Comparison
# ==========================================
with tab2:
    st.subheader("📊 CNN Architectures Performance Benchmark")
    st.markdown(
        "Comparison of all 7 evaluated deep learning architectures tested on the Plant Seedlings dataset."
    )

    benchmark_df = generate_benchmark_summary()
    st.dataframe(benchmark_df, use_container_width=True)

    st.markdown("### 📈 Visual Comparison")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("#### Accuracy vs Model Architecture")
        acc_data = pd.DataFrame({
            "Architecture": list(BENCHMARK_RESULTS.keys()),
            "Accuracy (%)": [BENCHMARK_RESULTS[k]["accuracy"] * 100 for k in BENCHMARK_RESULTS],
        }).set_index("Architecture")
        st.bar_chart(acc_data)

    with col_b2:
        st.markdown("#### Inference Latency (ms per image)")
        lat_data = pd.DataFrame({
            "Architecture": list(BENCHMARK_RESULTS.keys()),
            "Latency (ms)": [BENCHMARK_RESULTS[k]["latency_ms"] for k in BENCHMARK_RESULTS],
        }).set_index("Architecture")
        st.bar_chart(lat_data)

    # Architectural Details Accordion
    with st.expander("🔍 Detailed Architecture Trade-offs & Recommendations"):
        st.markdown(
            """
            - **ResNet50 / ResNet50V2**: Recommended for highest accuracy in cloud/server deployment where latency is not strictly constrained.
            - **MobileNetV2**: Ideal for edge devices, drones, handheld smart farming tools, and mobile applications (low latency, lightweight size).
            - **DenseNet121**: Exceptional feature propagation and reuse; great parameter efficiency.
            - **InceptionV3**: Multi-scale spatial convolution filters capable of spotting small seedlings at varying distances.
            - **SqueezeNet**: Extremely compact footprint (<5MB), suitable for microcontrollers and embedded agricultural sensors.
            - **AlexNet & VGG16**: Robust baseline architectures showcasing the evolution of deep convolutional neural networks.
            """
        )


# ==========================================
# TAB 3: Training & Metrics Explorer
# ==========================================
with tab3:
    st.subheader("📈 Training Performance & Confusion Matrix")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("#### Synthetic / Evaluated Confusion Matrix")
        # Check if confusion matrix image exists
        cm_image_path = IMAGES_DIR / "confusion matrix.png"
        if cm_image_path.exists():
            st.image(str(cm_image_path), caption="Plant Seedlings Multi-Class Confusion Matrix", use_container_width=True)
        else:
            dummy_cm = np.eye(len(CLASS_NAMES), dtype=int) * 35 + np.random.randint(0, 3, (len(CLASS_NAMES), len(CLASS_NAMES)))
            fig_cm = plot_confusion_matrix(dummy_cm, class_names=CLASS_NAMES, model_name=selected_architecture)
            st.pyplot(fig_cm)

    with col_t2:
        st.markdown("#### Training & Validation Accuracy Trajectory")
        plant2_path = IMAGES_DIR / "plant2.png"
        if plant2_path.exists():
            st.image(str(plant2_path), caption="Training & Validation Convergence Curves", use_container_width=True)
        else:
            st.info("Learning curves will appear here upon executing training runs.")

    st.markdown("---")
    st.markdown("#### 📋 Target Seedling Species Reference")
    species_df = pd.DataFrame([
        {
            "Class Name": name,
            "Scientific Name": info["scientific_name"],
            "Category": info["type"],
            "Threat Severity": info["severity"],
            "Agronomic Action": info["action"],
        }
        for name, info in PLANT_SPECIES_INFO.items()
    ])
    st.dataframe(species_df, use_container_width=True)


# ==========================================
# TAB 4: Batch Inference & Export
# ==========================================
with tab4:
    st.subheader("📁 Batch Seedling Classification")
    st.markdown("Upload multiple images simultaneously to generate a comprehensive agricultural classification report.")

    batch_files = st.file_uploader(
        "Upload multiple seedling images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )

    if batch_files:
        if st.button(f"Run Batch Classification ({len(batch_files)} images)", type="primary"):
            classifier = get_classifier(selected_architecture)
            records = []
            progress_bar = st.progress(0)

            for i, file in enumerate(batch_files):
                img = Image.open(file).convert("RGB")
                res = classifier.predict(img, top_k=1, use_tta=use_tta)
                records.append({
                    "Filename": file.name,
                    "Predicted Species": res["prediction"],
                    "Scientific Name": res["agricultural_advisory"]["scientific_name"],
                    "Category": res["type"],
                    "Confidence": res["confidence_percent"],
                    "Agronomic Action": res["agricultural_advisory"]["recommended_action"],
                })
                progress_bar.progress((i + 1) / len(batch_files))

            batch_df = pd.DataFrame(records)
            st.success(f"✅ Successfully classified {len(batch_files)} images!")
            st.dataframe(batch_df, use_container_width=True)

            # CSV Download Button
            csv_buffer = io.StringIO()
            batch_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Classification Report (CSV)",
                data=csv_buffer.getvalue(),
                file_name="seedling_classification_report.csv",
                mime="text/csv",
            )
