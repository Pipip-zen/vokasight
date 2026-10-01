import os
import io
import uuid
import cv2
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.preprocessing.image_processor import ImagePreprocessor
from src.backend.scoring_engine import ScoringEngine

# Initialize FastAPI app
app = FastAPI(
    title="VokaSight Inspection Engine API",
    description="Vision-Based Automated Hardware & Soldering Defect Inspection Engine for Vocational Lab Practicum (PRD 2 Spec)",
    version="1.1.0"
)

# Enable CORS for Flutter mobile client & Streamlit web client
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

# In-memory storage for inspection tasks (PRD 2 Async Task Queue)
TASKS_DB: Dict[str, Dict[str, Any]] = {}

# Catalog of Practicum Modules (PRD 2 Section 7.2)
PRACTICUM_MODULES = [
    {
        "id": "mod-soldering-basic",
        "name": "Praktikum Soldering & Desoldering Dasar",
        "description": "Inspeksi kualitas sambungan solder pad, void, dan deteksi solder bridge pada board latihan."
    },
    {
        "id": "mod-min-sys-avr",
        "name": "Praktikum Perakitan Minimum System AVR / Arduino",
        "description": "Verifikasi orientasi IC (pin 1 notch), polaritas kapapasitor elko/dioda, dan solder pin header."
    },
    {
        "id": "mod-power-supply",
        "name": "Praktikum Modul Regulator Catu Daya (Power Supply)",
        "description": "Pemeriksaan jalur kompoten regulator, dioda bridge, trafo, dan jalur sambungan PCB."
    }
]

# Schemas
class ModuleItem(BaseModel):
    id: str
    name: str
    description: str

class InspectionTaskResponse(BaseModel):
    task_id: str
    status: str
    module_id: str
    created_at: str

class InspectionResultDetail(BaseModel):
    task_id: str
    module_id: str
    status: str
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
        "weights_path": MODEL_WEIGHTS_PATH,
        "active_tasks": len(TASKS_DB)
    }

@app.get("/api/v1/modules", response_model=List[ModuleItem])
def get_practicum_modules():
    """Returns list of active practicum modules for Zero-Auth selection (PRD 2 Section 7.2)."""
    return PRACTICUM_MODULES

def process_inspection_task(task_id: str, image: np.ndarray, module_id: str):
    """Background task executing OpenCV CLAHE + Glare Reduction + YOLOv8 Inference + Scoring."""
    try:
        # 1. Preprocessing
        processed_img, quality_report = preprocessor.process(image)

        # 2. YOLOv8 Detection
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

        # 3. Scoring
        warning = quality_report.get("warning") if quality_report.get("is_suboptimal") else None
        score, parsed_defects, recommendations = scoring_engine.evaluate(detections, preprocessor_warning=warning)

        # Update DB Record
        TASKS_DB[task_id].update({
            "status": "completed",
            "score": score,
            "lighting_warning": warning,
            "detected_defects": parsed_defects,
            "recommendations": recommendations,
            "processed_at": datetime.utcnow().isoformat() + "Z"
        })
    except Exception as e:
        TASKS_DB[task_id].update({
            "status": "failed",
            "error_message": str(e),
            "score": 0.0,
            "detected_defects": [],
            "recommendations": ["Inspection failed due to an image processing error."],
            "processed_at": datetime.utcnow().isoformat() + "Z"
        })

@app.post("/api/v1/inspections", response_model=InspectionTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_inspection(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    module_id: str = Form("mod-soldering-basic")
):
    """Async inspection submission (PRD 2 Section 7.3 & 7.4)."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file format. Upload JPG or PNG.")

    task_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    TASKS_DB[task_id] = {
        "task_id": task_id,
        "module_id": module_id,
        "status": "processing",
        "score": 0.0,
        "lighting_warning": None,
        "detected_defects": [],
        "recommendations": [],
        "created_at": created_at,
        "processed_at": created_at
    }

    # Queue async processing
    background_tasks.add_task(process_inspection_task, task_id, image, module_id)

    return InspectionTaskResponse(
        task_id=task_id,
        status="processing",
        module_id=module_id,
        created_at=created_at
    )

@app.get("/api/v1/inspections/{task_id}", response_model=InspectionResultDetail)
def get_inspection_result(task_id: str):
    """Polling endpoint returning status, score, defects, and recommendations (PRD 2 Section 7.5)."""
    if task_id not in TASKS_DB:
        raise HTTPException(status_code=404, detail="Inspection task not found.")

    task = TASKS_DB[task_id]
    return InspectionResultDetail(
        task_id=task["task_id"],
        module_id=task["module_id"],
        status=task["status"],
        score=task["score"],
        lighting_warning=task.get("lighting_warning"),
        detected_defects=task.get("detected_defects", []),
        recommendations=task.get("recommendations", []),
        processed_at=task.get("processed_at", task["created_at"])
    )
