import os
import cv2
import base64
import requests
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

class RoboflowHostedInference:
    """
    Jalur A: Roboflow Hosted Inference API Service.
    Supports multi-model querying (Soldering Defect, PCB Defect & NBCM Soldering Inspection).
    """

    MODULE_MODEL_MAP = {
        "mod-soldering-basic": {"workspace": "nbmachinevision", "model_id": "pcb-defect-vagef", "version": 1},
        "mod-min-sys-avr": {"workspace": "nbmachinevision", "model_id": "pcb-defect-vagef", "version": 1},
        "mod-power-supply": {"workspace": "nbmachinevision", "model_id": "pcb-defect-vagef", "version": 1},
        "mod-pcb-defect-general": {"workspace": "nbmachinevision", "model_id": "pcb-defect-vagef", "version": 1},
        "mod-nbcm-soldering": {"workspace": "sazeh", "model_id": "nbcm-soldering-defect", "version": 1}
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_api_key(self) -> Optional[str]:
        if self.api_key and self.api_key.strip():
            return self.api_key.strip()
        load_dotenv(os.path.join(BASE_DIR, ".env"))
        return os.getenv("ROBOFLOW_API_KEY")

    def is_configured(self) -> bool:
        key = self.get_api_key()
        return bool(key and key.strip())

    def predict_image(
        self,
        image: np.ndarray,
        module_id: str = "mod-soldering-basic",
        confidence: float = 0.20
    ) -> Optional[List[Dict[str, Any]]]:
        api_key = self.get_api_key()
        if not api_key:
            print("[ROBOFLOW] API Key not configured, skipping cloud inference.")
            return None

        model_config = self.MODULE_MODEL_MAP.get(module_id, self.MODULE_MODEL_MAP["mod-soldering-basic"])
        model_id = model_config["model_id"]
        version = model_config["version"]

        try:
            # Encode image to JPEG base64
            _, buffer = cv2.imencode('.jpg', image)
            img_b64 = base64.b64encode(buffer).decode('utf-8')

            url = f"https://detect.roboflow.com/{model_id}/{version}"
            params = {
                "api_key": api_key,
                "confidence": confidence
            }
            print(f"[ROBOFLOW] Querying {url} (confidence={confidence})...")

            response = requests.post(
                url,
                params=params,
                data=img_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", [])
                
                parsed_detections = []
                for p in predictions:
                    cls_name = p.get("class", "defect")
                    conf = float(p.get("confidence", 0.0))
                    
                    # Convert center (x, y, w, h) to (x1, y1, x2, y2)
                    x = float(p.get("x", 0))
                    y = float(p.get("y", 0))
                    w = float(p.get("width", 0))
                    h = float(p.get("height", 0))

                    x1 = max(0.0, x - w / 2.0)
                    y1 = max(0.0, y - h / 2.0)
                    x2 = x + w / 2.0
                    y2 = y + h / 2.0

                    parsed_detections.append({
                        "class_name": cls_name,
                        "confidence": conf,
                        "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                        "source": f"roboflow_api_{model_id}"
                    })
                return parsed_detections
            else:
                print(f"Roboflow Hosted API returned status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Roboflow Hosted API error: {e}")
            return None
