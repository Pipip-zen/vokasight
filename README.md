# VokaSight - Automated Hardware Inspection Engine & Mobile API Backend

Vision-Based Automated Hardware & Digital Design Inspection Engine for Vocational Lab Practicum (PRD 2 Architecture).

## 📌 Project Overview
VokaSight provides an automated computer vision inspection pipeline to evaluate physical hardware assemblies (soldering defects, short circuits, voids, component orientation, and polarity). 

This FastAPI backend serves as the **mobile API server for Flutter / Mobile applications** and web clients, delivering real-time numerical scores and actionable repair instructions.

---

## 📱 Ringkasan Cepat: Cara Konek ke Mobile (Flutter / React Native)

### 1. Jalankan Backend di PC / Laptop
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Atur Base URL di Aplikasi Mobile
- **Emulator Android**: `http://10.0.2.2:8000/api/v1`
- **HP Fisik Asli**: `http://<IP-LAN-Laptop>:8000/api/v1` *(Wajib terhubung dalam 1 jaringan Wi-Fi yang sama)*.

### 3. Alur 3 Langkah di Kodingan Mobile Client:
1. **Langkah 1 (Get Modul)**: Panggil `GET /modules` untuk mengambil daftar modul praktikum aktif.
2. **Langkah 2 (Upload Foto)**: Kirim foto PCB via `POST /inspections` (`multipart/form-data`) $\rightarrow$ server mengembalikan `task_id` dan status `processing`.
3. **Langkah 3 (Cek Hasil / Polling)**: Panggil `GET /inspections/{task_id}` tiap 1 detik sampai status `completed` $\rightarrow$ ambil nilai (0–100), daftar cacat, dan saran perbaikan.

---

## 📂 Modular Project Structure

```
compvis/
├── mobile/                     # Flutter Mobile App (BLoC/Cubit, Dio, Offline Cache)
│   ├── lib/
│   │   ├── bloc/               # State management (module, inspection, history)
│   │   ├── core/               # API client, network, app colors
│   │   ├── models/             # Data models (Module, Task, InspectionResult, History)
│   │   ├── services/           # ApiService & LocalStorageService
│   │   ├── views/              # 5 Core Screens (Home, Upload, Scanning, Result, History)
│   │   └── main.dart
│   └── test/                   # Unit & Widget tests
├── backend/                    # FastAPI Backend API Server (Serves Mobile Apps & Web Clients)
│   ├── app/
│   │   ├── api/                # REST API Routers & Endpoints
│   │   │   ├── health.py       # Health check endpoint
│   │   │   ├── modules.py      # Practicum modules catalog (Zero-Auth)
│   │   │   └── inspections.py  # Async inspection submission & status polling
│   │   ├── core/               # Configuration & SQLite Database Engine
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── services/           # Computer Vision & Scoring Engines
│   │   │   ├── image_processor.py # OpenCV CLAHE & Glare Reduction
│   │   │   ├── scoring_engine.py  # Penalty-based scoring & repair advice
│   │   │   └── roboflow_service.py # Jalur A Roboflow Hosted Cloud API
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
│   ├── weights/                # Model weights directory (best.pt)
│   └── dataset/                # Dataset directory & data.yaml
├── demo_ui/                    # Streamlit Interactive Web & Mobile Demo Client
│   └── app.py
├── docs/                       # Product Requirements Documents (PRD 1 & PRD 2)
│   ├── prd_vokasight_mvp.md
│   └── prd_vokasight_mvp_2.md
├── vokasight.db                # SQLite Persistent Database
├── .gitignore
└── README.md

```

---

## ☁️ Inference Modes Supported

- **Jalur A (Roboflow Cloud Hosted API)**: Calls Roboflow cloud API directly (`https://detect.roboflow.com/soldering-defect-good-condition/1`). Instant cloud inference with zero local GPU usage.
- **Jalur B (Local YOLOv8 PyTorch Engine)**: Uses local YOLOv8-Nano `best.pt` model weights for 100% offline inference.

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

### 5. Run Flutter Mobile App (Android / iOS / Windows)
```bash
cd mobile
flutter pub get

# Jalankan di Emulator Android (default: http://10.0.2.2:8000/api/v1)
flutter run

# Atau jalankan dengan Base URL IP Wi-Fi laptop untuk HP Fisik:
flutter run --dart-define=BASE_URL=http://192.168.1.50:8000/api/v1
```

