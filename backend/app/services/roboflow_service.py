import os
import cv2
import base64
import requests
import numpy as np
from typing import List, Dict, Any, Optional

class RoboflowHostedInference:
    """
    Jalur A: Roboflow Hosted Inference API Service.
    Queries Roboflow Cloud model directly for soldering defects.
    """

    def __init__(self, api_key: Optional[str] = None, model_id: str = "soldering-defect-good-condition", version: int = 1):
        self.api_key = api_key or os.getenv("ROBOFLOW_API_KEY")
        self.model_id = model_id
        self.version = version

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def predict_image(self, image: np.ndarray, confidence: float = 0.35) -> Optional[List[Dict[str, Any]]]:
        if not self.is_configured():
            return None

        try:
            # Encode image to JPEG base64
            _, buffer = cv2.imencode('.jpg', image)
            img_b64 = base64.b64encode(buffer).decode('utf-8')

            url = f"https://detect.roboflow.com/{self.model_id}/{self.version}"
            params = {
                "api_key": self.api_key.strip(),
                "confidence": confidence
            }

            response = requests.post(
                url,
                params=params,
                data=img_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5.0
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
                        "source": "roboflow_hosted_api"
                    })
                return parsed_detections
            else:
                print(f"Roboflow Hosted API returned status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Roboflow Hosted API error: {e}")
            return None
