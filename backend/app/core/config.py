import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = os.path.join(BASE_DIR, "vokasight.db")

LOCAL_MODULE_WEIGHTS_MAP = {
    "mod-soldering-basic": os.path.join(BASE_DIR, "ml_engine", "weights", "soldering_basic_best.pt"),
    "mod-min-sys-avr": os.path.join(BASE_DIR, "ml_engine", "weights", "soldering_basic_best.pt"),
    "mod-power-supply": os.path.join(BASE_DIR, "ml_engine", "weights", "soldering_basic_best.pt"),
    "mod-pcb-defect-general": os.path.join(BASE_DIR, "ml_engine", "weights", "pcb_defect_general_best.pt"),
    "mod-nbcm-soldering": os.path.join(BASE_DIR, "ml_engine", "weights", "nbcm_soldering_best.pt")
}

DEFAULT_LOCAL_WEIGHTS = os.path.join(BASE_DIR, "ml_engine", "weights", "best.pt")

def find_module_weights(module_id: str = "mod-soldering-basic") -> str:
    target_path = LOCAL_MODULE_WEIGHTS_MAP.get(module_id, DEFAULT_LOCAL_WEIGHTS)
    if os.path.exists(target_path):
        return target_path
    elif os.path.exists(DEFAULT_LOCAL_WEIGHTS):
        return DEFAULT_LOCAL_WEIGHTS
    return os.path.join(BASE_DIR, "runs", "detect", "runs", "vokasight_soldering", "soldering_defect_yolov8n", "weights", "best.pt")

def find_weights() -> str:
    return find_module_weights("mod-soldering-basic")
