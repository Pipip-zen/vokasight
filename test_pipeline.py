import cv2
import numpy as np
import json
from src.preprocessing.image_processor import ImagePreprocessor
from src.backend.scoring_engine import ScoringEngine

def run_test():
    print("=== Testing ImagePreprocessor ===")
    preprocessor = ImagePreprocessor()

    # Create synthetic test PCB image with high contrast and bright spot
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add background texture
    test_img[:, :] = (50, 80, 50)
    # Add shiny solder joint spot (simulated glare)
    cv2.circle(test_img, (320, 240), 40, (255, 255, 255), -1)

    processed_img, quality = preprocessor.process(test_img)
    print("Quality Report:", json.dumps(quality, indent=2))
    assert processed_img.shape == test_img.shape, "Image shape changed!"
    print("Preprocessor test PASSED!")

    print("\n=== Testing ScoringEngine ===")
    scoring = ScoringEngine()

    sample_detections = [
        {"class_name": "solder_bridge", "confidence": 0.91, "bbox": [100, 100, 150, 150]},
        {"class_name": "void", "confidence": 0.85, "bbox": [200, 200, 230, 230]}
    ]

    score, parsed_defects, recommendations = scoring.evaluate(sample_detections, preprocessor_warning=quality.get("warning"))
    print(f"Calculated Score: {score}/100")
    print("Parsed Defects:", json.dumps(parsed_defects, indent=2))
    print("Recommendations:")
    for r in recommendations:
        print(" -", r)

    assert score < 100.0, "Score should have penalties applied!"
    print("ScoringEngine test PASSED!")

if __name__ == "__main__":
    run_test()
