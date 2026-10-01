import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image

from backend.app.services.image_processor import ImagePreprocessor
from backend.app.services.scoring_engine import ScoringEngine
from backend.app.core.config import find_weights
from backend.app.api.inspections import get_yolo_model
from backend.app.core.database import get_db_connection

st.set_page_config(
    page_title="VokaSight - Hardware Defect Inspection (Mobile Backend Connected)",
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
    .zero-auth-badge {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 0.3rem 0.6rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Fetch Practicum Modules from DB
def fetch_modules():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM modules;")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "description": r["description"]} for r in rows]

practicum_modules = fetch_modules()
preprocessor = ImagePreprocessor()
scoring_engine = ScoringEngine()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/integrated-circuit.png", width=70)
st.sidebar.title("VokaSight Mobile Portal")
st.sidebar.markdown("<span class='zero-auth-badge'>📱 Mobile App API Backend Ready</span>", unsafe_allow_html=True)
st.sidebar.caption("PRD 2 Modular Architecture")

module_options = {mod["name"]: mod["id"] for mod in practicum_modules}
selected_module_name = st.sidebar.selectbox("🎯 Target Practicum Module", list(module_options.keys()))
selected_module_id = module_options[selected_module_name]

for mod in practicum_modules:
    if mod["id"] == selected_module_id:
        st.sidebar.info(f"**Module Description:**\n{mod['description']}")

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Engine Status")
model_path = find_weights()
model = get_yolo_model()

if model is not None:
    st.sidebar.success(f"YOLOv8-Nano Model Active\n\n`{model_path}`")
else:
    st.sidebar.warning("Model running in fallback mode")

st.sidebar.divider()
st.sidebar.markdown("📦 **GitHub Repository:**")
st.sidebar.markdown("[github.com/Pipip-zen/vokasight.git](https://github.com/Pipip-zen/vokasight.git)")

# Main Header
st.markdown("<div class='main-header'>🔍 VokaSight Hardware Inspection Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated Soldering & Quality Inspection Engine (FastAPI Mobile Backend Connected)</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

uploaded_file = None

with col1:
    st.subheader("1. Gallery / Camera Image Input")
    input_method = st.radio("Select Input Source", ["Gallery Photo Upload (Flutter Picker Spec)", "Live Webcam Capture"], horizontal=True)

    if input_method == "Gallery Photo Upload (Flutter Picker Spec)":
        uploaded_file = st.file_uploader("Choose PCB Image from Gallery", type=["jpg", "jpeg", "png"])
    else:
        uploaded_file = st.camera_input("Capture PCB Photo")

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Uploaded PCB Photo", use_container_width=True)

with col2:
    st.subheader("2. Inspection Results & Feedback")

    if uploaded_file is not None and image is not None:
        with st.spinner("Executing OpenCV pre-processing & YOLOv8 inference..."):
            start_time = time.time()

            processed_img, quality = preprocessor.process(image)
            
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

                        color = (0, 0, 255) if "bridge" in cls_name or "short" in cls_name else (0, 255, 255)
                        if "good" in cls_name:
                            color = (0, 255, 0)

                        x1, y1, x2, y2 = map(int, xyxy)
                        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 3)
                        cv2.putText(annotated_img, f"{cls_name} {conf:.2f}", (x1, max(15, y1 - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            warning = quality.get("warning") if quality.get("is_suboptimal") else None
            score, parsed_defects, recommendations = scoring_engine.evaluate(detections, preprocessor_warning=warning)
            latency = round((time.time() - start_time) * 1000, 1)

            tab1, tab2 = st.tabs(["🎯 AI Defect Bounding Boxes", "🔬 OpenCV CLAHE Image"])
            with tab1:
                st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), caption=f"Defect Overlay ({latency} ms)", use_container_width=True)
            with tab2:
                st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), caption="CLAHE Contrast & Glare Normalized", use_container_width=True)

            st.markdown("---")
            score_color = "#16A34A" if score >= 80 else "#CA8A04" if score >= 60 else "#DC2626"
            st.markdown(f"""
            <div class='score-card'>
                <div style='color: #64748B; font-weight: 600;'>PENALTY-BASED SCORE</div>
                <div class='score-number' style='color: {score_color};'>{score} / 100</div>
                <div style='color: #475569; font-size: 0.9rem;'>Module: {selected_module_id} | Latency: {latency} ms</div>
            </div>
            """, unsafe_allow_html=True)

            if warning:
                st.markdown(f"<div class='warn-box'>⚠️ <b>Lighting Alert:</b> {warning}</div>", unsafe_allow_html=True)

            st.markdown("### 📋 Actionable Repair Recommendations")
            for rec in recommendations:
                st.markdown(f"<div class='rec-box'>💡 {rec}</div>", unsafe_allow_html=True)

            if parsed_defects:
                st.markdown("### 🔍 Detected Defect Breakdown & Penalties")
                st.table(parsed_defects)

    else:
        st.info("👈 Choose a practicum module and upload a PCB photo to analyze.")

st.divider()
st.caption("VokaSight Modular Architecture | Mobile API Backend Ready | GitHub: https://github.com/Pipip-zen/vokasight.git")
