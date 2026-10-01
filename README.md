# VokaSight - Automated Hardware Inspection Engine & Mobile API Backend

Vision-Based Automated Hardware & Digital Design Inspection Engine for Vocational Lab Practicum (PRD 2 Architecture).

## 📌 Project Overview
VokaSight provides an automated computer vision inspection pipeline to evaluate physical hardware assemblies (soldering defects, short circuits, voids, component orientation, and polarity). 

This FastAPI backend serves as the **mobile API server for Flutter / Mobile applications** and web clients, delivering real-time numerical scores and actionable repair instructions.

---

## 📂 Modular Project Structure

```
compvis/
├── backend/                    # Core FastAPI Backend API (Serves Mobile Apps & Web Clients)
│   ├── app/
│   │   ├── api/                # REST API Routers & Endpoints
│   │   │   ├── health.py       # Health check & system status
│   │   │   ├── modules.py      # Practicum modules catalog (Zero-Auth)
│   │   │   └── inspections.py  # Async inspection submission & status polling
│   │   ├── core/               # Configuration & SQLite Database Engine
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── services/           # Computer Vision & Scoring Logic
│   │   │   ├── image_processor.py # OpenCV CLAHE & Glare Reduction
│   │   │   └── scoring_engine.py  # Penalty-based scoring & repair advice
│   │   └── schemas/            # Pydantic Schemas
│   │       ├── module.py
│   │       └── inspection.py
│   ├── tests/                  # Unit & Integration Tests
│   │   ├── test_api.py
│   │   └── test_pipeline.py
│   └── main.py                 # FastAPI Application Entry Point
├── ml_engine/                  # Machine Learning & YOLOv8 Training Pipeline
│   ├── train.py                # YOLOv8 training script
│   ├── generate_synthetic.py   # Synthetic test dataset generator
│   ├── weights/                # Trained YOLOv8 model weights (best.pt)
│   └── dataset/                # Dataset directory & data.yaml
├── demo_ui/                    # Streamlit Interactive Web & Mobile Demo UI
│   └── app.py
├── docs/                       # Product Requirements Documents (PRD 1 & PRD 2)
│   ├── prd_vokasight_mvp.md
│   └── prd_vokasight_mvp_2.md
├── vokasight.db                # SQLite Persistent Database
├── .gitignore
└── README.md
```

---

## 📱 Mobile App Backend Capabilities

FastAPI exposes standard REST endpoints for mobile app clients (Flutter, React Native, Swift, Kotlin):

### 1. `GET /api/v1/modules`
Returns list of active practicum modules for Zero-Auth selection (PRD 2 Section 7.2).

### 2. `POST /api/v1/inspections` (Async Submission)
Accepts `multipart/form-data` with image file and `module_id`. Returns HTTP 202 Accepted with `task_id` and status `processing`.

### 3. `GET /api/v1/inspections/{task_id}` (Polling Endpoint)
Returns inspection result details once status is `completed`:
- Numerical Score (0–100)
- Defect bounding box coordinates & confidence scores
- Actionable step-by-step repair recommendations
- Suboptimal lighting alerts (if overexposed or too dark)

---

## 🚀 Quick Start Guide

### 1. Run FastAPI Mobile Backend Server
```bash
python backend/main.py
# or
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`

### 2. Run Streamlit Interactive Demo Client
```bash
streamlit run demo_ui/app.py
```
- Web UI Client: `http://localhost:8501`

### 3. Run Automated Tests
```bash
python backend/tests/test_pipeline.py
python backend/tests/test_api.py
```

### 4. Train YOLOv8-Nano Model
```bash
# Train on custom Roboflow dataset
python ml_engine/train.py --roboflow_key YOUR_ROBOFLOW_API_KEY --epochs 50 --batch 16
```
