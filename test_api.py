import cv2
import numpy as np
import requests
import time
from fastapi.testclient import TestClient
from src.backend.main import app

def test_api_endpoints():
    client = TestClient(app)

    print("=== Testing GET /health ===")
    response = client.get("/health")
    print("Health check status code:", response.status_code)
    print("Health check response:", response.json())
    assert response.status_code == 200, "Health check failed!"

    print("\n=== Testing POST /api/v1/auth/student ===")
    auth_payload = {"student_id": "5324600006", "full_name": "Rian Hardware Student"}
    response = client.post("/api/v1/auth/student", json=auth_payload)
    print("Auth status code:", response.status_code)
    print("Auth response:", response.json())
    assert response.status_code == 200, "Auth failed!"

    print("\n=== Testing POST /api/v1/inspect/hardware ===")
    # Generate test image
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    test_img[:, :] = (30, 90, 40)
    cv2.circle(test_img, (320, 240), 30, (200, 200, 200), -1)

    _, img_encoded = cv2.imencode('.jpg', test_img)
    img_bytes = img_encoded.tobytes()

    files = {'file': ('test_board.jpg', img_bytes, 'image/jpeg')}
    data = {'student_id': '5324600006', 'module_type': 'hardware_soldering'}

    response = client.post("/api/v1/inspect/hardware", files=files, data=data)
    print("Inspection status code:", response.status_code)
    res_json = response.json()
    print("Inspection response keys:", list(res_json.keys()))
    print(f"Task ID: {res_json.get('task_id')}")
    print(f"Score: {res_json.get('score')}")
    print(f"Recommendations: {res_json.get('recommendations')}")
    assert response.status_code == 200, "Hardware inspection failed!"
    print("\nAll FastAPI Endpoint Tests PASSED!")

if __name__ == "__main__":
    test_api_endpoints()
