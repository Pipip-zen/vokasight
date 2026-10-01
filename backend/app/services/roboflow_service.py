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
    Supports multi-model querying tailored to specific practicum modules:
    - mod-pcb-defect-general: queries 'pcb-defects-dataset' (trace breaks, missing hole, mouse bite, open circuit, spur)
      plus 'pcb-defect-vagef' (solder bridge & board damage)
    - mod-soldering-basic: queries 'pcb-defect-vagef' (short circuit, spillover, cold joint, miss welding)
    """

    MODULE_MODEL_MAP = {
        "mod-pcb-defect-general": [
            {"model_id": "pcb-defects-dataset", "version": 1, "confidence": 0.30},
            {"model_id": "pcb-defect-vagef", "version": 1, "confidence": 0.55}
        ],
        "mod-soldering-basic": [
            {"model_id": "pcb-defect-vagef", "version": 1, "confidence": 0.45}
        ]
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
        confidence: Optional[float] = None
    ) -> Optional[List[Dict[str, Any]]]:
        api_key = self.get_api_key()
        if not api_key:
            print("[ROBOFLOW] API Key not configured, skipping cloud inference.")
            return None

        model_configs = self.MODULE_MODEL_MAP.get(
            module_id,
            self.MODULE_MODEL_MAP["mod-soldering-basic"]
        )

        try:
            # Encode image to JPEG base64 once
            _, buffer = cv2.imencode('.jpg', image)
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            all_detections = []

            for cfg in model_configs:
                m_id = cfg["model_id"]
                ver = cfg["version"]
                conf_val = confidence if confidence is not None else cfg.get("confidence", 0.40)

                url = f"https://detect.roboflow.com/{m_id}/{ver}"
                params = {
                    "api_key": api_key,
                    "confidence": conf_val
                }
                print(f"[ROBOFLOW] Querying {m_id}/{ver} (module={module_id}, confidence={conf_val})...")

                try:
                    response = requests.post(
                        url,
                        params=params,
                        data=img_b64,
                        headers=headers,
                        timeout=12.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        predictions = data.get("predictions", [])
                        print(f"[ROBOFLOW] {m_id}/{ver} returned {len(predictions)} predictions.")

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

                            all_detections.append({
                                "class_name": cls_name,
                                "confidence": round(conf, 4),
                                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                                "source": f"roboflow_api_{m_id}"
                            })
                    else:
                        print(f"[ROBOFLOW] {m_id}/{ver} returned status {response.status_code}: {response.text[:120]}")
                except Exception as req_err:
                    print(f"[ROBOFLOW] Error querying {m_id}/{ver}: {req_err}")

            return all_detections
        except Exception as e:
            print(f"[ROBOFLOW] Hosted API error: {e}")
            return None
