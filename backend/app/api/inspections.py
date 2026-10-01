import os
import uuid
import cv2
import json
import sqlite3
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status, BackgroundTasks
from backend.app.schemas.inspection import InspectionTaskResponse, InspectionResultDetail
from backend.app.services.image_processor import ImagePreprocessor
from backend.app.services.scoring_engine import ScoringEngine
from backend.app.services.roboflow_service import RoboflowHostedInference
from backend.app.core.config import find_module_weights, DB_PATH

router = APIRouter()

preprocessor = ImagePreprocessor()
scoring_engine = ScoringEngine()
roboflow_cloud = RoboflowHostedInference()

yolo_models_cache: Dict[str, Any] = {}

def get_yolo_model_for_module(module_id: str):
    weights_path = find_module_weights(module_id)
    if weights_path in yolo_models_cache:
        return yolo_models_cache[weights_path]

    if os.path.exists(weights_path):
        try:
            from ultralytics import YOLO
            model = YOLO(weights_path)
            yolo_models_cache[weights_path] = model
            print(f"Loaded local YOLOv8 model for module {module_id} from {weights_path}")
            return model
        except Exception as e:
            print(f"Failed to load local YOLO model from {weights_path}: {e}")
    return None

def process_inspection_task(task_id: str, image: np.ndarray, module_id: str, roboflow_key: Optional[str] = None):
    try:
        processed_img, quality_report = preprocessor.process(image)
        detections = []
        inference_source = "local_yolov8"

        # Jalur A: Try Roboflow Hosted API if Key Provided
        cloud_engine = RoboflowHostedInference(api_key=roboflow_key) if roboflow_key else roboflow_cloud
        if cloud_engine.is_configured():
            cloud_detections = cloud_engine.predict_image(processed_img, module_id=module_id, confidence=0.35)
            if cloud_detections is not None:
                detections = cloud_detections
                inference_source = "roboflow_hosted_api"

        # Jalur B: Local YOLOv8 Fallback if Jalur A not used or failed
        if not detections and inference_source == "local_yolov8":
            model = get_yolo_model_for_module(module_id)
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
                            "bbox": xyxy,
                            "source": "local_yolov8"
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

@router.post("/inspections", response_model=InspectionTaskResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/inspections/submit", response_model=InspectionTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_inspection(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    module_id: str = Form("mod-soldering-basic"),
    student_id: Optional[str] = Form(None),
    roboflow_key: Optional[str] = Form(None)
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

    background_tasks.add_task(process_inspection_task, task_id, image, module_id, roboflow_key)

    return InspectionTaskResponse(
        task_id=task_id,
        status="processing",
        module_id=module_id,
        student_id=student_id,
        message="Foto berhasil diunggah. Analisis AI sedang berjalan...",
        created_at=created_at
    )

@router.get("/inspections/{task_id}", response_model=InspectionResultDetail)
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

    recs = json.loads(row[6]) if row[6] else []
    recs_text = "\n".join([f"• {r}" for r in recs]) if recs else None

    return InspectionResultDetail(
        task_id=row[0],
        module_id=row[1],
        status=row[2],
        score=row[3],
        lighting_warning=row[4],
        detected_defects=json.loads(row[5]) if row[5] else [],
        recommendations=recs,
        recommendations_text=recs_text,
        processed_at=row[8] or row[7]
    )

