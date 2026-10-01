import streamlit as st
import cv2
import numpy as np
import requests
import json
import time
from PIL import Image
import io

from src.preprocessing.image_processor import ImagePreprocessor
from src.backend.scoring_engine import ScoringEngine
from src.backend.main import get_yolo_model, find_weights, preprocessor, scoring_engine

st.set_page_config(
    page_title="VokaSight - Hardware Defect Inspection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .score-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 800;
    }
    .rec-box {
        background-color: #F0FDF4;
        border-left: 4px solid #16A34A;
        padding: 0.8rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
    }
    .warn-box {
        background-color: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 0.8rem;
        border-radius: 4px;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Student Auth
st.sidebar.image("https://img.icons8.com/color/96/integrated-circuit.png", width=70)
st.sidebar.title("VokaSight Student Portal")
st.sidebar.caption("Vision-Based Hardware Inspection")

student_id = st.sidebar.text_input("Student ID (NIM)", value="5324600006")
student_name = st.sidebar.text_input("Student Name", value="Rian Electronics Student")
module_type = st.sidebar.selectbox("Practicum Module", ["Hardware Soldering Inspection", "PCB Component Polarity", "Wiring Route Verification"])

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Engine Status")
model_path = find_weights()
model = get_yolo_model()

if model is not None:
    st.sidebar.success(f"YOLOv8 Model Loaded\n\n`{model_path}`")
else:
    st.sidebar.warning("Model running in heuristic/simulated mode (Weights pending)")

st.sidebar.divider()
st.sidebar.info("💡 **Hackathon Demo Mode**: Upload a PCB photo or take a photo with your webcam to test real-time inspection.")

# Main Interface
st.markdown("<div class='main-header'>🔍 VokaSight Hardware Inspection Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated Soldering & Assembly Quality Assessment for Vocational Practicum</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

uploaded_file = None

with col1:
    st.subheader("1. Image Capture / Upload")
    input_method = st.radio("Select Input Source", ["Upload Image File", "Use Device Camera"], horizontal=True)

    if input_method == "Upload Image File":
        uploaded_file = st.file_uploader("Upload PCB Photo", type=["jpg", "jpeg", "png"])
    else:
        uploaded_file = st.camera_input("Take PCB Photo")

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Original Image", use_container_width=True)

with col2:
    st.subheader("2. Inspection Results & Feedback")

    if uploaded_file is not None and image is not None:
        with st.spinner("Executing OpenCV pre-processing & YOLOv8 inference..."):
            start_time = time.time()

            # 1. OpenCV Pre-processing
            processed_img, quality = preprocessor.process(image)
            
            # 2. YOLOv8 Model Inference
            detections = []
            annotated_img = image.copy()

            if model is not None:
                results = model.predict(processed_img, conf=0.35)
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = model.names[cls_id]
                        conf = float(box.conf[0])
                        xyxy = [float(x) for x in box.xyxy[0]]

                        detections.append({
                            "class_name": cls_name,
                            "confidence": conf,
                            "bbox": xyxy
                        })

                        # Color coding
                        color = (0, 0, 255) if "bridge" in cls_name or "short" in cls_name else (0, 255, 255)
                        if "good" in cls_name:
                            color = (0, 255, 0)

                        x1, y1, x2, y2 = map(int, xyxy)
                        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 3)
                        cv2.putText(annotated_img, f"{cls_name} {conf:.2f}", (x1, max(15, y1 - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # 3. Scoring & Recommendations
            warning = quality.get("warning") if quality.get("is_suboptimal") else None
            score, parsed_defects, recommendations = scoring_engine.evaluate(detections, preprocessor_warning=warning)
            latency = round((time.time() - start_time) * 1000, 1)

            # Tab View for Visualizations
            tab1, tab2 = st.tabs(["🎯 AI Detection Overlay", "🔬 OpenCV CLAHE Image"])
            with tab1:
                st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), caption=f"Defect Overlay ({latency} ms)", use_container_width=True)
            with tab2:
                st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), caption="CLAHE Contrast & Glare Normalized", use_container_width=True)

            # Score Card Display
            st.markdown("---")
            score_color = "#16A34A" if score >= 85 else "#CA8A04" if score >= 60 else "#DC2626"
            st.markdown(f"""
            <div class='score-card'>
                <div style='color: #64748B; font-weight: 600;'>AUTOMATED PRACTICUM SCORE</div>
                <div class='score-number' style='color: {score_color};'>{score} / 100</div>
                <div style='color: #475569; font-size: 0.9rem;'>Student NIM: {student_id} | Latency: {latency} ms</div>
            </div>
            """, unsafe_allow_html=True)

            # Lighting Warning Alert
            if warning:
                st.markdown(f"<div class='warn-box'>⚠️ <b>Lighting Alert:</b> {warning}</div>", unsafe_allow_html=True)

            # Recommendations List
            st.markdown("### 📋 Instant Repair Recommendations")
            for rec in recommendations:
                st.markdown(f"<div class='rec-box'>💡 {rec}</div>", unsafe_allow_html=True)

            # Defect Table Breakdown
            if parsed_defects:
                st.markdown("### 🔍 Detected Defects Breakdown")
                st.table(parsed_defects)

    else:
        st.info("👈 Please upload or capture a PCB photo on the left panel to trigger automatic inspection.")

st.divider()
st.caption("VokaSight MVP Engine | Hackathon Prototype | Dual-Mode Vocational Lab Inspection Platform")
