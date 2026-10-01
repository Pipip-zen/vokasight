import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import cv2
import numpy as np
import json
from backend.app.services.image_processor import ImagePreprocessor
from backend.app.services.scoring_engine import ScoringEngine

def run_test():
    print("=== Testing ImagePreprocessor & PCB Validation ===")
    preprocessor = ImagePreprocessor()

    # 1. Valid PCB-like image with pads and tracks
    pcb_img = np.zeros((480, 640, 3), dtype=np.uint8)
    pcb_img[:, :] = (30, 90, 40)
    # Add multiple pad contours and lines
    for i in range(10):
        cv2.circle(pcb_img, (50 + i * 50, 100), 12, (220, 220, 220), -1)
        cv2.circle(pcb_img, (50 + i * 50, 200), 12, (220, 220, 220), -1)
        cv2.line(pcb_img, (50 + i * 50, 100), (50 + i * 50, 200), (180, 180, 180), 3)

    processed_pcb, quality_pcb = preprocessor.process(pcb_img)
    print("PCB Image Quality Report:", json.dumps(quality_pcb, indent=2))
    assert quality_pcb["is_pcb"] == True, "Valid PCB was wrongly rejected!"

    # 2. Non-PCB blank image
    non_pcb_img = np.ones((480, 640, 3), dtype=np.uint8) * 128
    processed_non_pcb, quality_non_pcb = preprocessor.process(non_pcb_img)
    print("Non-PCB Image Quality Report:", json.dumps(quality_non_pcb, indent=2))
    assert quality_non_pcb["is_pcb"] == False, "Non-PCB image was wrongly accepted!"

    print("\n=== Testing ScoringEngine Non-PCB Rejection ===")
    scoring = ScoringEngine()

    score, parsed_defects, recs = scoring.evaluate([], is_pcb=False)
    print(f"Non-PCB Calculated Score: {score}/100")
    print("Non-PCB Defects:", json.dumps(parsed_defects, indent=2))
    print("Non-PCB Recommendations:", recs)

    assert score == 0.0, "Non-PCB image should get 0 score!"
    assert "non_pcb_object" in parsed_defects[0]["class_name"], "Non-PCB defect tag missing!"
    print("ScoringEngine Non-PCB Validation test PASSED!")

if __name__ == "__main__":
    run_test()
