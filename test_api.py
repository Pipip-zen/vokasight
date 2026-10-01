import cv2
import numpy as np
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

    print("\n=== Testing PRD 2 GET /api/v1/modules ===")
    response = client.get("/api/v1/modules")
    print("Modules status code:", response.status_code)
    modules = response.json()
    print("Available Practicum Modules:", len(modules))
    assert response.status_code == 200 and len(modules) > 0, "Modules catalog failed!"

    print("\n=== Testing PRD 2 Async POST /api/v1/inspections ===")
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    test_img[:, :] = (30, 90, 40)
    cv2.circle(test_img, (320, 240), 30, (200, 200, 200), -1)

    _, img_encoded = cv2.imencode('.jpg', test_img)
    img_bytes = img_encoded.tobytes()

    files = {'file': ('test_board.jpg', img_bytes, 'image/jpeg')}
    data = {'module_id': 'mod-soldering-basic'}

    response = client.post("/api/v1/inspections", files=files, data=data)
    print("Async Submit status code:", response.status_code)
    submit_res = response.json()
    print("Submit response:", submit_res)
    task_id = submit_res["task_id"]
    assert response.status_code == 202, "Async submit failed!"

    print(f"\n=== Testing PRD 2 Polling GET /api/v1/inspections/{task_id} ===")
    poll_res = None
    for _ in range(5):
        poll_resp = client.get(f"/api/v1/inspections/{task_id}")
        poll_res = poll_resp.json()
        if poll_res["status"] == "completed":
            break
        time.sleep(0.1)

    print("Polling result status:", poll_res.get("status"))
    print("Polling result score:", poll_res.get("score"))
    print("Polling result recommendations:", poll_res.get("recommendations"))
    assert poll_res.get("status") == "completed", "Polling processing did not complete!"

    print("\nAll PRD 2 FastAPI Endpoint Tests PASSED!")

if __name__ == "__main__":
    test_api_endpoints()
