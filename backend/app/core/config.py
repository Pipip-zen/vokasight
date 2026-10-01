import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = os.path.join(BASE_DIR, "vokasight.db")

MODEL_WEIGHT_CANDIDATES = [
    os.getenv("YOLO_WEIGHTS", ""),
    os.path.join(BASE_DIR, "ml_engine", "weights", "best.pt"),
    os.path.join(BASE_DIR, "runs", "detect", "runs", "vokasight_soldering", "soldering_defect_yolov8n", "weights", "best.pt")
]

def find_weights() -> str:
    for p in MODEL_WEIGHT_CANDIDATES:
        if p and os.path.exists(p):
            return p
    return os.path.join(BASE_DIR, "ml_engine", "weights", "best.pt")
