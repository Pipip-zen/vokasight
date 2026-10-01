import os
import io
import uuid
import cv2
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.preprocessing.image_processor import ImagePreprocessor
from src.backend.scoring_engine import ScoringEngine

# Initialize FastAPI app
app = FastAPI(
    title="VokaSight Inspection Engine API",
    description="Vision-Based Automated Hardware & Soldering Defect Inspection Engine for Vocational Practicum",
    version="1.0.0"
)

# Enable CORS for mobile/web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
preprocessor = ImagePreprocessor()
scoring_engine = ScoringEngine()

# Model placeholder path
MODEL_WEIGHT_CANDIDATES = [
    os.getenv("YOLO_WEIGHTS", ""),
    "runs/detect/runs/vokasight_soldering/soldering_defect_yolov8n/weights/best.pt",
    "runs/vokasight_soldering/soldering_defect_yolov8n/weights/best.pt",
    "runs/soldering_defect_yolov8n/weights/best.pt"
]

def find_weights():
    for p in MODEL_WEIGHT_CANDIDATES:
        if p and os.path.exists(p):
            return p
    return "runs/detect/runs/vokasight_soldering/soldering_defect_yolov8n/weights/best.pt"

MODEL_WEIGHTS_PATH = find_weights()
yolo_model = None

def get_yolo_model():
    global yolo_model
    if yolo_model is None:
        if os.path.exists(MODEL_WEIGHTS_PATH):
            try:
                from ultralytics import YOLO
                yolo_model = YOLO(MODEL_WEIGHTS_PATH)
                print(f"Loaded trained YOLOv8 model from {MODEL_WEIGHTS_PATH}")
            except Exception as e:
                print(f"Failed to load YOLO model: {e}")
                yolo_model = None
    return yolo_model

# Schemas
class StudentAuthRequest(BaseModel):
    student_id: str
    full_name: Optional[str] = "Student"

class StudentAuthResponse(BaseModel):
    student_id: str
    full_name: str
    message: str
    session_id: str

class InspectionResponse(BaseModel):
    task_id: str
    student_id: str
    module_type: str
    score: float
    lighting_warning: Optional[str] = None
    detected_defects: List[Dict[str, Any]]
    recommendations: List[str]
    processed_at: str

@app.get("/health")
def health_check():
    model_loaded = os.path.exists(MODEL_WEIGHTS_PATH)
    return {
        "status": "online",
        "service": "VokaSight MVP API",
        "yolo_model_available": model_loaded,
        "weights_path": MODEL_WEIGHTS_PATH
    }

@app.post("/api/v1/auth/student", response_model=StudentAuthResponse)
def student_auth(req: StudentAuthRequest):
    if not req.student_id or len(req.student_id.strip()) < 3:
        raise HTTPException(status_code=400, detail="Invalid Student ID (NIM). Must be at least 3 characters.")
    
    session_id = str(uuid.uuid4())
    return StudentAuthResponse(
        student_id=req.student_id.strip(),
        full_name=req.full_name or "Student",
        message="Authentication successful. Ready for inspection session.",
        session_id=session_id
    )

@app.post("/api/v1/inspect/hardware", response_model=InspectionResponse)
async def inspect_hardware(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    module_type: str = Form("hardware_soldering")
):
    # 1. Read uploaded image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file uploaded.")

    # 2. Preprocess image (CLAHE, Glare Reduction, Quality Check)
    processed_img, quality_report = preprocessor.process(image)

    # 3. Perform AI Defect Detection
    model = get_yolo_model()
    detections = []

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
    else:
        # Fallback simulation if model weights not yet trained
        # (Allows testing API endpoints prior to training completion)
        detections = []

    # 4. Scoring & Recommendation Engine
    warning = quality_report.get("warning") if quality_report.get("is_suboptimal") else None
    score, parsed_defects, recommendations = scoring_engine.evaluate(detections, preprocessor_warning=warning)

    task_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    return InspectionResponse(
        task_id=task_id,
        student_id=student_id,
        module_type=module_type,
        score=score,
        lighting_warning=warning,
        detected_defects=parsed_defects,
        recommendations=recommendations,
        processed_at=timestamp
    )
