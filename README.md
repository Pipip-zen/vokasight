# VokaSight MVP - Hardware & Soldering Defect Inspection Engine

Vision-Based Automated Hardware & Digital Design Inspection Engine for Vocational Lab Practicum.

## 📌 Project Overview
VokaSight provides an automated computer vision inspection pipeline to evaluate physical hardware assemblies (soldering defects, short circuits, voids, component orientation, and polarity). Students receive real-time numerical scores and actionable repair instructions prior to official lab instructor grading.

---

## 🏗️ Architecture & Features

```
          +-----------------------+
          |  Student Mobile App   |
          |  (NIM Authentication) |
          +-----------+-----------+
                      | Upload Image
                      v
      +-------------------------------+
      |   FastAPI Backend Server      |
      |   (http://localhost:8000)     |
      +---------------+---------------+
                      |
        +-------------+-------------+
        |                           |
        v                           v
+------------------+     +-----------------------+
|  OpenCV Preproc  |     |   YOLOv8-Nano Engine  |
|  - CLAHE Contrast|     |   - Soldering Bridge  |
|  - Glare Reduction     |   - Void & Short      |
|  - Lighting Check|     |   - Polarity Error    |
+---------+--------+     +-----------+-----------+
          |                         |
          +------------+------------+
                       |
                       v
            +--------------------+
            |   Scoring Engine   |
            |   (Score 0 - 100)  |
            +---------+----------+
                      | JSON Response
                      v
            +--------------------+
            | Score & Actionable |
            | Repair Advice      |
            +--------------------+
```

### Key Modules:
- **`src/preprocessing/image_processor.py`**: OpenCV pipeline implementing CLAHE (Contrast Limited Adaptive Histogram Equalization) in LAB color space, specular glare reduction, and lighting quality checks (too dark / overexposed).
- **`src/model/train_yolo.py`**: YOLOv8-Nano object detection pipeline supporting Roboflow Universe dataset downloads and custom model training.
- **`src/backend/scoring_engine.py`**: Automated scoring calculator (0-100 scale) with weighted defect penalties and targeted repair recommendations.
- **`src/backend/main.py`**: FastAPI application exposing endpoints for student authentication (`/api/v1/auth/student`) and hardware image inspection (`/api/v1/inspect/hardware`).

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install torch torchvision ultralytics roboflow opencv-python fastapi uvicorn python-multipart
```

### 2. Prepare Dataset & Train YOLOv8 Model

#### Option A: Download from Roboflow Universe
Download the [Soldering Defect Dataset](https://universe.roboflow.com/fyp-fjnfe/soldering-defect-good-condition) using your Roboflow API key:
```bash
python src/model/train_yolo.py --roboflow_key YOUR_ROBOFLOW_API_KEY --epochs 50 --batch 16
```

#### Option B: Test with Synthetic Dataset
Generate a sample dataset for instant local training:
```bash
python src/model/generate_sample_dataset.py
python src/model/train_yolo.py --data dataset/data.yaml --epochs 10 --batch 4
```

### 3. Run FastAPI Backend Server
```bash
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger API Docs will be available at: `http://localhost:8000/docs`

---

## 🧪 Verification & Testing

Run pipeline and API unit tests:
```bash
# Test Image Preprocessor & Scoring Engine
python test_pipeline.py

# Test FastAPI Endpoints
python test_api.py
```

---

## 📊 API Specification

### `POST /api/v1/auth/student`
Authenticates student using Student ID (NIM).
- **Payload:** `{"student_id": "5324600006", "full_name": "Rian Hardware Student"}`
- **Response:** `{"student_id": "5324600006", "session_id": "...", "message": "Authentication successful..."}`

### `POST /api/v1/inspect/hardware`
Uploads PCB photo for automated defect inspection.
- **Form Data:**
  - `file`: Multipart image file (`.jpg` or `.png`)
  - `student_id`: `"5324600006"`
  - `module_type`: `"hardware_soldering"`
- **Response Structure:**
```json
{
  "task_id": "a40cb786-aafa-4004-85e8-fc3a8dfb1376",
  "student_id": "5324600006",
  "module_type": "hardware_soldering",
  "score": 75.0,
  "lighting_warning": null,
  "detected_defects": [
    {
      "class_name": "solder_bridge",
      "confidence": 0.91,
      "penalty": 25.0,
      "bbox": [100.0, 100.0, 150.0, 150.0]
    }
  ],
  "recommendations": [
    "Solder bridge detected between pins. Apply flux and reheat joint with soldering iron tip to break unwanted connection."
  ],
  "processed_at": "2026-10-01T13:22:53Z"
}
```
