import os
import sqlite3
from fastapi import APIRouter
from backend.app.core.config import find_weights, DB_PATH

router = APIRouter()

@router.get("/health")
def health_check():
    weights_path = find_weights()
    model_loaded = os.path.exists(weights_path)
    
    task_count = 0
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inspection_tasks;")
        task_count = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass
        
    return {
        "status": "online",
        "service": "VokaSight MVP Mobile API Engine",
        "yolo_model_available": model_loaded,
        "weights_path": weights_path,
        "total_saved_tasks": task_count,
        "database": "SQLite (vokasight.db)"
    }
