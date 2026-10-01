# Product Requirements Document (PRD): VokaSight (MVP - Hardware Inspection Module)

## 1. Problem Statement
Instruktur dan asisten laboratorium di institusi pendidikan vokasi (khususnya teknik elektronika) menghadapi beban penilaian yang tinggi dan subjektif saat memeriksa ratusan rakitan perangkat keras fisik mahasiswa (sambungan solder, polaritas komponen, dan perakitan PCB). Mahasiswa vokasi juga mengalami keterlambatan umpan balik (feedback loop) karena harus menunggu antrean pemeriksaan asisten lab, sehingga menghambat proses belajar mandiri yang iteratif.

## 2. Target User & Persona
*   **Target User:** Mahasiswa vokasi teknik elektronika yang sedang melakukan praktikum perakitan hardware fisik secara mandiri maupun di lab.
*   **Persona 1: Rian (Mahasiswa Praktikum Elektronika)**
    *   *Karakteristik:* Mahasiswa tingkat awal yang sedang menempuh praktikum soldering dan perakitan PCB mikrokontroler.
    *   *Pain Points:* Ragu apakah hasil soldernya mengalami short circuit/cold joint dan lelah mengantre asistensi.
    *   *Goals:* Mendapatkan evaluasi instan mandiri hanya dengan mengunggah foto board dari smartphone sebelum dikumpulkan ke instruktur.
*   **Persona 2: Budi (Asisten Laboratorium)**
    *   *Karakteristik:* Mahasiswa senior yang bertugas memvalidasi kelayakan hardware mahasiswa praktikum.
    *   *Pain Points:* Kewalahan melayani puluhan mahasiswa yang meminta validasi fisik satu per satu di meja lab.
    *   *Goals:* Mahasiswa melakukan self-screening mandiri untuk kesalahan dasar sebelum mengajukan penilaian resmi.

---

## 3. Tech Stack Architecture

| Layer | Komponen / Teknologi | Deskripsi |
| :--- | :--- | :--- |
| **Mobile Client** | **Flutter** (Dart) | Aplikasi mobile cross-platform (Android/iOS) |
| **Backend API** | **FastAPI** (Python 3.10+) | REST API performa tinggi untuk manajemen task & interaksi client |
| **Task Queue & Broker** | **Celery + Redis** | Pemrosesan antrean inferensi AI secara asynchronous |
| **AI Inference** | **YOLOv8-Nano** (Ultralytics) | Object detection model dilatih pada custom dataset cacat PCB |
| **Image Pre-processing** | **OpenCV** (Python) | CLAHE (Contrast Limited Adaptive Histogram Equalization) & glare reduction |
| **Database** | **PostgreSQL** | Relational database untuk menyimpan modul, task inspeksi, dan hasil analisis |
| **Image Storage** | **Server Local Filesystem** | Penyimpanan file gambar terunggah langsung di media disk server |
| **Client Storage** | **Local Cache (Device)** | Penyimpanan riwayat inspeksi secara lokal di smartphone mahasiswa (offline history) |
| **Deployment** | **Cloud Environment** | VPS / Railway / Render |

---

## 4. Goals and Non-Goals

### Goals (MVP)
*   Menyediakan aplikasi mobile berbasis **Flutter** tanpa registrasi/login yang rumit (langsung masuk ke aplikasi).
*   Mahasiswa dapat memilih modul praktikum target sebelum melakukan inspeksi.
*   Pengunggahan foto dari **galeri HP** (image picker) secara praktis dan fleksibel.
*   Pipeline backend async (**FastAPI + Celery + Redis**) dengan pra-pemrosesan citra (**OpenCV**) dan deteksi cacat hardware fisik (**YOLOv8-Nano custom dataset**).
*   Sistem penilaian berbasis penalti (**Penalty-based scoring**): Nilai dasar 100, dikurangi bobot penalti untuk tiap cacat yang terdeteksi.
*   Pemberian rekomendasi perbaikan instan berbasis teks serta visualisasi bounding box cacat.
*   Penyimpanan riwayat inspeksi lokal di perangkat (offline history caching).

### Non-Goals (MVP)
*   Tidak ada sistem autentikasi / login (tidak membutuhkan NIM atau SSO di fase MVP).
*   Tidak menyediakan fitur live camera interface dengan custom alignment overlay guideline (menggunakan native gallery picker).
*   Belum menyertakan modul verifikasi desain digital (screenshot UI/UX atau diagram logika rangkaian).
*   Belum menyediakan Web Dashboard khusus instruktur/dosen (manajemen kelas, rekap nilai massal, audit log) — *direncanakan pada v2*.
*   Tidak ada integrasi LMS eksternal (Moodle/Google Classroom) pada tahap ini.

---

## 5. User Stories
1.  **Akses Langsung:** Sebagai mahasiswa, saya ingin **langsung membuka aplikasi tanpa login** agar dapat segera memeriksa hasil solderan saya tanpa hambatan administratif.
2.  **Pemilihan Modul:** Sebagai mahasiswa, saya ingin **memilih modul praktikum spesifik** (misal: *Modul Catu Daya*, *Modul Mikrokontroler Minimum System*) agar AI mengevaluasi sesuai konteks tugas praktikum.
3.  **Unggah Galeri:** Sebagai mahasiswa, saya ingin **memilih dan mengunggah foto PCB dari galeri smartphone saya** agar saya bebas mengambil foto menggunakan aplikasi kamera bawaan yang memiliki kualitas/fokus terbaik.
4.  **Analisis AI & Status:** Sebagai mahasiswa, saya ingin **melihat status antrean pemrosesan secara transparan** selagi server menganalisis gambar.
5.  **Hasil Skor & Rekomendasi:** Sebagai mahasiswa, saya ingin **melihat skor akhir (0–100) dan rekomendasi perbaikan terperinci** (contoh: *"Terdeteksi jembatan solder pada Pin 3-4, gunakan solder wick untuk membersihkan timah berlebih"*).
6.  **Riwayat Lokal:** Sebagai mahasiswa, saya ingin **melihat riwayat pemeriksaan sebelumnya di perangkat saya** meskipun sedang offline atau koneksi lab kurang stabil.

---

## 6. Feature Breakdown: MVP / v2 / Future Roadmap

### MVP (Minimum Viable Product)
1.  **Zero-Auth Entry:** Langsung masuk ke beranda / katalog modul praktikum tanpa form login.
2.  **Module Selector:** Daftar modul praktikum yang dapat dipilih oleh mahasiswa sebelum upload.
3.  **Gallery Image Picker:** Akses galeri perangkat dengan validasi format (JPG, PNG) dan ukuran file.
4.  **Backend Image Pre-processing:** OpenCV CLAHE & glare reduction untuk normalisasi kontras sebelum inferensi.
5.  **Async AI Inference Engine:** Celery worker menjalankan inferensi YOLOv8-Nano (custom PCB dataset) via Redis broker.
6.  **Penalty-Based Scoring System:** Kalkulasi skor transparan: $\text{Skor} = \max(0, 100 - \sum \text{Penalti Cacat})$.
7.  **Instant Result Screen:** Menampilkan skor numerik, bounding box cacat yang terdeteksi, dan poin rekomendasi perbaikan.
8.  **Local Offline History:** Penyimpanan riwayat inspeksi di storage lokal smartphone.

### v2 (Next Version)
*   Web Dashboard Dosen / Instruktur (manajemen kelas, monitoring nilai angkatan, verifikasi manual / override score).
*   Sistem akun/autentikasi terintegrasi NIM mahasiswa untuk sinkronisasi nilai ke cloud.
*   Modul verifikasi desain digital (UI/UX layout and schematic logic checks).
*   Sinkronisasi riwayat multi-perangkat via cloud account.

### Future Roadmap
*   Integrasi LMS Institusional (Moodle, Canvas, Google Classroom).
*   On-device Edge AI Inference (TensorFlow Lite / ONNX Runtime di Flutter) untuk latensi ultra-rendah tanpa koneksi internet sama sekali.

---

## 7. Functional Requirements Detail per MVP Feature

### 7.1. Akses & Onboarding (Zero-Auth)
*   Aplikasi langsung menampilkan halaman utama berisi daftar modul praktikum aktif tanpa meminta kredensial apa pun.
*   Device ID acak (UUID lokal) dibuat saat pertama kali aplikasi di-install untuk menandai sesi inspeksi lokal.

### 7.2. Pemilihan Modul Praktikum
*   Mahasiswa wajib memilih 1 modul praktikum dari daftar sebelum tombol upload aktif.
*   Daftar modul didapatkan dari endpoint `GET /api/v1/modules` (dengan fallback cache lokal di Flutter jika offline).

### 7.3. Gallery Picker & Upload
*   Menggunakan native image picker untuk memilih foto dari galeri HP.
*   Pratinjau (preview) foto ditampilkan sebelum pengguna menekan tombol "Mulai Analisis".
*   Aplikasi mengirimkan payload multipart/form-data ke endpoint `POST /api/v1/inspections` berisi file gambar dan `module_id`.

### 7.4. Pre-processing & Async AI Engine
*   Backend FastAPI menerima file gambar, menyimpannya di direktori lokal server (`/uploads/{date}/{task_id}.jpg`), dan mencatat record task di PostgreSQL.
*   Task dipush ke Celery queue melalui Redis broker.
*   Celery worker memproses citra menggunakan OpenCV:
    *   Konversi color space, penerapan CLAHE untuk menyeimbangkan kontras refleksi solder.
    *   Deteksi glare/over-exposure berlebih.
*   Model YOLOv8-Nano (custom trained PCB dataset) mendeteksi kelas cacat:
    *   *Soldering Bridge / Short Circuit*
    *   *Insufficient Solder / Cold Joint*
    *   *Excess Solder / Balling*
    *   *Component Misplacement / Polarity Error*
*   Worker menyimpan hasil inferensi (bounding box coordinates, label, confidence, penalti) ke PostgreSQL dan mengubah status task menjadi `completed`.

### 7.5. Polling & Hasil Penilaian (Penalty-Based Scoring)
*   Aplikasi Flutter melakukan polling status ke `GET /api/v1/inspections/{task_id}` sampai status menjadi `completed` atau `failed`.
*   Formula Skor:
    $$\text{Score} = \max\left(0, 100 - \sum_{i=1}^{n} \text{Weight}(\text{Defect}_i)\right)$$
    *Contoh bobot penalti:*
    *   Short Circuit / Bridge: -25 poin
    *   Polarity / Misalignment: -20 poin
    *   Cold Joint / Insufficient: -15 poin
    *   Excess Solder: -10 poin
*   Halaman hasil menampilkan:
    *   Badge skor (misal: `75 / 100`) dengan indikator warna (Hijau $\ge 80$, Kuning $60-79$, Merah $< 60$).
    *   Gambar hasil inspeksi dengan overlay bounding box defect.
    *   Daftar instruksi perbaikan konkret per cacat yang ditemukan.

### 7.6. Offline Device History
*   Setelah hasil diterima dari server, aplikasi Flutter secara otomatis menyimpan metadata inspeksi, thumbnail, skor, dan rekomendasi ke database lokal HP (SQLite / Hive / ObjectBox).
*   Mahasiswa dapat membuka tab "Riwayat" kapan saja tanpa koneksi internet.

---

## 8. Data Model Sketch (PostgreSQL)

```sql
-- 1. Practical Modules
CREATE TABLE modules (
    id VARCHAR(50) PRIMARY KEY, -- e.g., 'mod-soldering-basic', 'mod-min-sys-avr'
    name VARCHAR(150) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Inspection Tasks
CREATE TABLE inspection_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id VARCHAR(50) REFERENCES modules(id) ON DELETE SET NULL,
    device_fingerprint VARCHAR(100), -- identifier unik lokal device (opsional)
    original_image_path TEXT NOT NULL,
    annotated_image_path TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Inspection Results
CREATE TABLE inspection_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID UNIQUE REFERENCES inspection_tasks(id) ON DELETE CASCADE,
    score NUMERIC(5, 2) NOT NULL, -- 0.00 to 100.00
    detected_defects JSONB NOT NULL DEFAULT '[]'::jsonb, 
    -- e.g. [{"class": "bridge", "confidence": 0.93, "bbox": [x1, y1, x2, y2], "penalty": 25}]
    recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- e.g. ["Gunakan solder wick pada pin 3-4 untuk membersihkan jembatan solder."]
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 9. Edge Cases and Failure States

*   **Pencahayaan Sangat Ekstrem (Terlalu Silau / Terlalu Gelap):**
    *   *Kondisi:* Foto dari galeri memiliki pantulan timah solder yang overexposed atau terlalu gelap sehingga CLAHE tidak dapat mengekstrak kontur.
    *   *Penanganan:* Worker mencatat warning, dan aplikasi menampilkan panduan: *"Foto terlalu silau/gelap. Disarankan mengambil ulang foto di pencahayaan merata tanpa flash langsung."*
*   **Foto Bukan PCB atau Salah Modul:**
    *   *Kondisi:* Pengguna mengunggah foto acak (misal foto selfie atau objek non-elektronika).
    *   *Penanganan:* Model YOLO mendeteksi tidak ada komponen/PCB valid (confidence < 40%). Task berstatus `failed` dengan pesan: *"Objek PCB tidak terdeteksi. Pastikan foto memperlihatkan papan rangkaian yang jelas."*
*   **Koneksi Terputus Saat Polling:**
    *   *Kondisi:* Mahasiswa keluar dari aplikasi atau sinyal hilang saat Celery sedang memproses.
    *   *Penanganan:* `task_id` tersimpan di local cache Flutter. Ketika koneksi pulih, aplikasi dapat mengecek kembali status task yang tertunda via `GET /api/v1/inspections/{task_id}`.

---

## 10. Success Metrics (MVP)
*   **Akurasi Deteksi AI:** Kesesuaian klasifikasi defect model YOLOv8-Nano dibanding verifikasi manual $\ge 85\%$.
*   **Kecepatan Pemrosesan (Latency):** Total waktu dari tombol "Mulai Analisis" diklik hingga hasil tampil di HP $\le 5$ detik pada jaringan stabil.
*   **Tingkat Keberhasilan Upload Galeri:** Kegagalan upload berkas akibat kompresi atau format tidak didukung $< 2\%$.
*   **Kemandirian Belajar:** $\ge 60\%$ mahasiswa melakukan perbaikan fisik solderan berdasarkan rekomendasi sistem sebelum asistensi lab.

---

## 11. Kesimpulan Keputusan Desain (Design Decisions Summary)
1.  **Autentikasi:** Tanpa login — mahasiswa langsung dapat mengakses aplikasi.
2.  **Pemilihan Modul:** Wajib memilih modul praktikum dari daftar sebelum inspeksi.
3.  **Input Gambar:** Upload foto dari galeri HP (native gallery picker).
4.  **Model AI:** YOLOv8-Nano dengan custom dataset cacat PCB.
5.  **Frontend:** Flutter (Android/iOS).
6.  **Backend:** FastAPI + Celery + Redis.
7.  **Database:** PostgreSQL.
8.  **Penyimpanan Gambar:** Local filesystem pada server.
9.  **Sistem Penilaian:** Penalty-based (nilai dasar 100, dikurangi penalti per jenis cacat).
10. **Riwayat Inspeksi:** Caching offline di lokal smartphone mahasiswa.
11. **Deployment:** Cloud VPS / Container Platform (Railway / Render).