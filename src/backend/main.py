import os
import io
import uuid
import cv2
import numpy as np
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.preprocessing.image_processor import ImagePreprocessor
from src.backend.scoring_engine import ScoringEngine

DB_PATH = "vokasight.db"

def init_sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Modules Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    );
    """)
    
    # Inspection Tasks Table (PRD 2 Schema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspection_tasks (
        id TEXT PRIMARY KEY,
        module_id TEXT,
        status TEXT NOT NULL,
        score REAL DEFAULT 0.0,
        lighting_warning TEXT,
        detected_defects TEXT DEFAULT '[]',
        recommendations TEXT DEFAULT '[]',
        created_at TEXT,
        processed_at TEXT
    );
    """)
    
    # Insert default modules if empty
    cursor.execute("SELECT COUNT(*) FROM modules;")
    if cursor.fetchone()[0] == 0:
        default_modules = [
            ("mod-soldering-basic", "Praktikum Soldering & Desoldering Dasar", "Inspeksi kualitas sambungan solder pad, void, dan deteksi solder bridge pada board latihan."),
            ("mod-min-sys-avr", "Praktikum Perakitan Minimum System AVR / Arduino", "Verifikasi orientasi IC (pin 1 notch), polaritas kapasitor elko/dioda, dan solder pin header."),
            ("mod-power-supply", "Praktikum Modul Regulator Catu Daya (Power Supply)", "Pemeriksaan jalur komponen regulator, dioda bridge, trafo, dan jalur sambungan PCB.")
        ]
        cursor.executemany("INSERT INTO modules VALUES (?, ?, ?);", default_modules)
        conn.commit()
    conn.close()

# Initialize SQLite database
init_sqlite_db()

# Initialize FastAPI app
app = FastAPI(
    title="VokaSight Inspection Engine API",
    description="Vision-Based Automated Hardware & Soldering Defect Inspection Engine for Vocational Lab Practicum (PRD 2 SQLite Spec)",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

preprocessor = ImagePreprocessor()
scoring_engine = ScoringEngine()

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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inspection_tasks;")
    task_count = cursor.fetchone()[0]
    conn.close()
    
    return {
        "status": "online",
        "service": "VokaSight MVP API",
        "yolo_model_available": model_loaded,
        "weights_path": MODEL_WEIGHTS_PATH,
        "total_saved_tasks": task_count,
        "database": "SQLite (vokasight.db)"
    }

@app.get("/api/v1/modules", response_model=List[ModuleItem])
def get_practicum_modules():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM modules;")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]

def process_inspection_task(task_id: str, image: np.ndarray, module_id: str):
    try:
        processed_img, quality_report = preprocessor.process(image)
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

        warning = quality_report.get("warning") if quality_report.get("is_suboptimal") else None
        score, parsed_defects, recommendations = scoring_engine.evaluate(detections, preprocessor_warning=warning)
        processed_at = datetime.utcnow().isoformat() + "Z"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE inspection_tasks
        SET status = 'completed', score = ?, lighting_warning = ?, detected_defects = ?, recommendations = ?, processed_at = ?
        WHERE id = ?;
        """, (score, warning, json.dumps(parsed_defects), json.dumps(recommendations), processed_at, task_id))
        conn.commit()
        conn.close()
    except Exception as e:
        processed_at = datetime.utcnow().isoformat() + "Z"
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE inspection_tasks
        SET status = 'failed', score = 0.0, lighting_warning = ?, detected_defects = '[]', recommendations = '["Inspection processing error."]', processed_at = ?
        WHERE id = ?;
        """, (str(e), processed_at, task_id))
        conn.commit()
        conn.close()

@app.post("/api/v1/inspections", response_model=InspectionTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_inspection(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    module_id: str = Form("mod-soldering-basic")
):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image format. Upload JPG or PNG.")

    task_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO inspection_tasks (id, module_id, status, created_at)
    VALUES (?, ?, 'processing', ?);
    """, (task_id, module_id, created_at))
    conn.commit()
    conn.close()

    background_tasks.add_task(process_inspection_task, task_id, image, module_id)

    return InspectionTaskResponse(
        task_id=task_id,
        status="processing",
        module_id=module_id,
        created_at=created_at
    )

@app.get("/api/v1/inspections/{task_id}", response_model=InspectionResultDetail)
def get_inspection_result(task_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, module_id, status, score, lighting_warning, detected_defects, recommendations, created_at, processed_at
    FROM inspection_tasks WHERE id = ?;
    """, (task_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Inspection task not found.")

    return InspectionResultDetail(
        task_id=row[0],
        module_id=row[1],
        status=row[2],
        score=row[3],
        lighting_warning=row[4],
        detected_defects=json.loads(row[5]) if row[5] else [],
        recommendations=json.loads(row[6]) if row[6] else [],
        processed_at=row[8] or row[7]
    )
