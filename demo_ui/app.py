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
from backend.app.services.roboflow_service import RoboflowHostedInference
from backend.app.core.config import find_weights
from backend.app.api.inspections import get_yolo_model
from backend.app.core.database import get_db_connection

st.set_page_config(
    page_title="VokaSight - Hardware Defect Inspection (Hybrid Cloud/Local)",
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
    .badge-cloud {
        background-color: #F0F9FF;
        color: #0369A1;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-local {
        background-color: #F0FDF4;
        color: #15803D;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
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
st.sidebar.title("VokaSight Portal")
st.sidebar.markdown("<span class='zero-auth-badge'>⚡ Hybrid Cloud + Local Engine</span>", unsafe_allow_html=True)

module_options = {mod["name"]: mod["id"] for mod in practicum_modules}
selected_module_name = st.sidebar.selectbox("🎯 Target Practicum Module", list(module_options.keys()))
selected_module_id = module_options[selected_module_name]

for mod in practicum_modules:
    if mod["id"] == selected_module_id:
        st.sidebar.info(f"**Module Description:**\n{mod['description']}")

st.sidebar.divider()
st.sidebar.markdown("### ☁️ Inference Engine Selector")

inference_mode = st.sidebar.radio(
    "Preferred Inference Engine",
    ["Jalur A: Roboflow Cloud Hosted API", "Jalur B: Local YOLOv8 Engine"],
    help="Jalur A uses Roboflow cloud API (instant, no GPU needed). Jalur B uses local YOLOv8 PyTorch model."
)

roboflow_key_input = None
if "Jalur A" in inference_mode:
    roboflow_key_input = st.sidebar.text_input("Roboflow API Key", type="password", help="Enter Roboflow API key for cloud inference")
    if roboflow_key_input:
        st.sidebar.success("☁️ Jalur A Cloud API Configured")
    else:
        st.sidebar.warning("⚠️ Enter Roboflow API key to enable cloud mode (or fallback to Jalur B)")
else:
    model_path = find_weights()
    st.sidebar.success(f"💻 Jalur B Local YOLOv8 Active\n\n`{model_path}`")

st.sidebar.divider()
st.sidebar.markdown("📦 **GitHub Repository:**")
st.sidebar.markdown("[github.com/Pipip-zen/vokasight.git](https://github.com/Pipip-zen/vokasight.git)")

# Main Header
st.markdown("<div class='main-header'>🔍 VokaSight Hardware Inspection Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Automated Soldering & Quality Inspection (Roboflow Cloud + Local Hybrid Mode)</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

uploaded_file = None

with col1:
    st.subheader("1. Gallery / Camera Image Input")
    input_method = st.radio("Select Input Source", ["Gallery Photo Upload", "Live Webcam Capture"], horizontal=True)

    if input_method == "Gallery Photo Upload":
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
        with st.spinner("Executing OpenCV pre-processing & AI inference..."):
            start_time = time.time()

            # 1. Preprocessing
            processed_img, quality = preprocessor.process(image)
            
            # 2. Hybrid Inference Engine (Jalur A vs Jalur B)
            detections = []
            active_engine = "Jalur B (Local YOLOv8)"
            annotated_img = image.copy()

            # Check Jalur A
            if "Jalur A" in inference_mode and roboflow_key_input:
                rf_client = RoboflowHostedInference(api_key=roboflow_key_input)
                cloud_dets = rf_client.predict_image(processed_img, confidence=0.35)
                if cloud_dets is not None:
                    detections = cloud_dets
                    active_engine = "Jalur A (Roboflow Cloud Hosted API)"

            # Jalur B Fallback
            if not detections:
                model = get_yolo_model()
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

            # Render Bounding Boxes
            for det in detections:
                cls_name = det.get("class_name", "")
                conf = float(det.get("confidence", 0.0))
                xyxy = det.get("bbox", [0, 0, 0, 0])

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

            # Display Tabs
            tab1, tab2 = st.tabs(["🎯 AI Defect Bounding Boxes", "🔬 OpenCV CLAHE Image"])
            with tab1:
                st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), caption=f"Defect Overlay ({active_engine} - {latency} ms)", use_container_width=True)
            with tab2:
                st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), caption="CLAHE Contrast & Glare Normalized", use_container_width=True)

            # Score Card Display
            st.markdown("---")
            score_color = "#16A34A" if score >= 80 else "#CA8A04" if score >= 60 else "#DC2626"
            engine_badge = "badge-cloud" if "Jalur A" in active_engine else "badge-local"
            st.markdown(f"""
            <div class='score-card'>
                <div style='color: #64748B; font-weight: 600;'>AUTOMATED INSPECTION SCORE</div>
                <div class='score-number' style='color: {score_color};'>{score} / 100</div>
                <div style='margin-top: 0.4rem;'>
                    <span class='{engine_badge}'>{active_engine}</span>
                    <span style='color: #475569; font-size: 0.9rem; margin-left: 0.5rem;'>Module: {selected_module_id} | Latency: {latency} ms</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Lighting Alert
            if warning:
                st.markdown(f"<div class='warn-box'>⚠️ <b>Lighting Alert:</b> {warning}</div>", unsafe_allow_html=True)

            # Recommendations
            st.markdown("### 📋 Actionable Repair Recommendations")
            for rec in recommendations:
                st.markdown(f"<div class='rec-box'>💡 {rec}</div>", unsafe_allow_html=True)

            # Defects Table
            if parsed_defects:
                st.markdown("### 🔍 Detected Defect Breakdown")
                st.table(parsed_defects)

    else:
        st.info("👈 Select an inference mode and upload a PCB photo to begin.")

st.divider()
st.caption("VokaSight Hybrid Architecture | Roboflow Cloud Hosted API + Local YOLOv8 | GitHub: https://github.com/Pipip-zen/vokasight.git")
