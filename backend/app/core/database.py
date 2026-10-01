import sqlite3
from backend.app.core.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Modules Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    );
    """)
    
    # Inspection Tasks Table (PRD 2 Schema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspection_tasks (
        id TEXT PRIMARY KEY,
        module_id TEXT,
        status TEXT NOT NULL,
        score REAL DEFAULT 0.0,
        lighting_warning TEXT,
        detected_defects TEXT DEFAULT '[]',
        recommendations TEXT DEFAULT '[]',
        created_at TEXT,
        processed_at TEXT
    );
    """)
    
    # Ensure default modules exist
    default_modules = [
        ("mod-soldering-basic", "Praktikum Soldering & Desoldering Dasar", "Inspeksi kualitas sambungan solder pad, void, dan deteksi solder bridge pada board latihan."),
        ("mod-min-sys-avr", "Praktikum Perakitan Minimum System AVR / Arduino", "Verifikasi orientasi IC (pin 1 notch), polaritas kapasitor elko/dioda, dan solder pin header."),
        ("mod-power-supply", "Praktikum Modul Regulator Catu Daya (Power Supply)", "Pemeriksaan jalur komponen regulator, dioda bridge, trafo, dan jalur sambungan PCB."),
        ("mod-pcb-defect-general", "Praktikum Inspeksi Cacat PCB General (PCB Defect Detection)", "Pemeriksaan cacat fisik PCB secara menyeluruh (missing component, short/open circuit, spur, pin hole, dan sisa tembaga)."),
        ("mod-nbcm-soldering", "Praktikum Inspeksi NBCM Soldering Defect", "Pemeriksaan cacat penyolderan tingkat lanjut NBCM (excess solder, insufficient solder, cold joint, solder bridge, pin hole).")
    ]

    for m_id, m_name, m_desc in default_modules:
        cursor.execute("INSERT OR IGNORE INTO modules (id, name, description) VALUES (?, ?, ?);", (m_id, m_name, m_desc))
    
    conn.commit()
    conn.close()
