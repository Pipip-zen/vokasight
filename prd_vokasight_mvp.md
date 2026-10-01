# Product Requirements Document (PRD): VokaSight (MVP - Hardware Inspection Module)

## 1. Problem Statement
Instructors and laboratory assistants in vocational educational institutions (particularly electronics engineering) face massive and subjective grading burdens when inspecting thousands of physical hardware assemblies built by students (such as soldering joints, component polarity, and wiring routing). Vocational students also suffer from delayed feedback loops, having to wait days or weeks to discover if their physical assemblies contain defects or misplacements, which hinders independent iterative learning.

## 2. Target User + 2 Persona
*   **Target User:** Vocational engineering students actively performing independent hardware assembly practicals.
*   **Persona 1: Rian (Electronics Practical Vocational Student)**
    *   *Characteristics:* First-year student undergoing soldering and microcontroller PCB assembly practicals.
    *   *Pain Points:* Unsure if his soldering has short circuits or cold joints, and has to wait in long queues for lab assistants to check his board.
    *   *Goals:* Get fast independent assessments at home or in the lab using a smartphone before submitting final assignments.
*   **Persona 2: Budi (Laboratory Assistant / Self-Tester)**
    *   *Characteristics:* Senior student helping guide practicals and validating initial hardware compliance.
    *   *Pain Points:* Overwhelmed by dozens of students asking for physical validation one by one at the lab desk.
    *   *Goals:* Have a rapid verification tool so students can perform self-screening on basic errors before official instructor grading.

## 3. Goals and Non-Goals
*   **Goals (MVP):**
    *   Provide a standalone mobile application for students to photograph physical hardware assemblies (PCB/soldering).
    *   Implement an image processing pipeline (OpenCV) and server-side AI inference (FastAPI + YOLOv8-Nano) to detect primary physical hardware defects (soldering bridge/short, component orientation, polarity).
    *   Display automated scores and text-based repair recommendations instantly to the student.
*   **Non-Goals (MVP):**
    *   Does not include the digital design verification module (UI/UX screenshots or logic diagrams) in this phase.
    *   Does not provide a dedicated Web Dashboard for instructors/teachers (class management, institutional grade aggregation, or grading veto rights).
    *   No external LMS integration (Moodle/Google Classroom) at this stage.

## 4. User Stories
*   As a **student**, I want to **log into the application using my Student ID (NIM)** so that **my practical session is recorded correctly**.
*   As a **student**, I want to **use the mobile camera with a alignment guideline frame and automatic lighting correction** so that **my PCB or assembly photo is not blurry or glary**.
*   As a **student**, I want to **upload my hardware assembly photo for AI analysis** so that **I receive an automated score and instant repair instructions**.
*   As a **student**, I want to **see detailed hardware defect breakdowns (e.g., soldering bridge detected at specific pins)** so that **I know exactly which part to fix**.

## 5. Feature Breakdown: MVP / v2 / Future
*   **MVP (Minimum Viable Product):**
    *   Simple Student Authentication based on Student ID (NIM).
    *   Mobile Inspection Camera with guideline frames and basic image pre-processing (CLAHE & glare reduction).
    *   Backend AI Engine (FastAPI + YOLOv8-Nano) for Physical Hardware Defect Detection (Soldering Inspection & Component Verification).
    *   Instant Results Page (total score and text-based repair recommendation list).
*   **v2 (Next Version):**
    *   Digital Design Verification Module (UI/UX screenshots & logic diagrams).
    *   Instructor Web Dashboard (class management, mass grade aggregation, audit logs).
    *   Student submission history and score progression tracking over time.
*   **Future Roadmap:**
    *   Institutional LMS integration (Moodle/Google Classroom).
    *   On-device edge AI analysis for lower latency without full server internet dependency.

## 6. Functional Requirement Detail per MVP Feature
1.  **Student Authentication:**
    *   The system must accept a Student ID input (e.g., format `5324600006`) to start an inspection session without complex registration workflows.
2.  **Inspection Camera & Pre-processing:**
    *   The camera interface must display a bounding box overlay guideline to center the PCB object.
    *   The backend/frontend must execute image normalization (OpenCV CLAHE for contrast and glare reduction) before sending the image to the AI model.
3.  **AI Hardware Inspection Engine:**
    *   The backend server (FastAPI) must receive image payloads, manage task queues (Celery/Redis if needed), and process images using the YOLOv8-Nano model.
    *   The system must detect at least defect categories: *Soldering Bridge / Short Circuit*, *Void*, and *Component / Polarity Error*.
4.  **Instant Results & Recommendations:**
    *   The system generates a numerical score (0–100) based on defect weight penalties.
    *   The system generates a list of actionable text recommendations (e.g., *"Short circuit detected at IC pins 3-4, use solder wick to clean excess solder"*).

## 7. Data Model Sketch (Entities + Key Fields)
*   **Student:**
    *   `student_id` (PK, String, e.g., `"5324600006"`)
    *   `full_name` (String)
    *   `created_at` (Timestamp)
*   **Inspection_Task:**
    *   `task_id` (PK, UUID)
    *   `student_id` (FK to Student)
    *   `module_type` (String, e.g., `"hardware_soldering"`)
    *   `image_url` (String, path to stored captured image)
    *   `status` (Enum: `processing`, `completed`, `failed`)
    *   `created_at` (Timestamp)
*   **Inspection_Result:**
    *   `result_id` (PK, UUID)
    *   `task_id` (FK to Inspection_Task)
    *   `score` (Float, 0 - 100)
    *   `detected_defects_json` (JSON, storing defect coordinates and types, e.g., `[{"type": "bridge", "confidence": 0.92}]`)
    *   `recommendations_text` (Text, summary of repair recommendations)
    *   `processed_at` (Timestamp)

## 8. Edge Cases and Failure States
*   **Extreme Lighting Conditions (Too Dark / Heavy Glare):**
    *   *Failure State:* OpenCV algorithms fail to normalize contrast, or the AI model yields low accuracy.
    *   *Handling:* The system triggers a mobile pop-up warning: *"Lighting is suboptimal or too glary. Please move to a brighter area or turn off flash."*
*   **PCB Object Out of Frame / Not Detected:**
    *   *Failure State:* Student photographs a non-PCB object (e.g., table or empty hand).
    *   *Handling:* The AI model detects object confidence below minimum threshold (< 50%), and the system rejects the image, prompting the student to retake the photo.
*   **Server Connection Lost During Image Upload:**
    *   *Failure State:* HTTP request to FastAPI backend drops halfway.
    *   *Handling:* The app displays a "Retry" button without erasing the captured photo from device local cache.

## 9. Success Metrics
*   **AI Detection Accuracy:** Match rate between AI hardware defect detection and manual validation reaching $\ge 85\%$.
*   **Response Latency:** Processing time from pressing "Analyze" to score/recommendation appearance on the student's phone $\le 5$ seconds.
*   **Self-Correction Retention:** Percentage of students performing re-uploads after receiving system recommendations $\ge 70\%$.

## 10. Open Questions
1.  Does this MVP mobile application require local inspection history caching on the student's phone in case internet connectivity drops entirely inside the lab environment?
2.  Will component type categories and soldering pin references be generically configured by the system, or will students need to select a specific practical module type (e.g., *ATmega328 Minimum System Module* vs *Power Supply Module*) before taking photos?