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
    
    # Insert default modules if empty
    cursor.execute("SELECT COUNT(*) FROM modules;")
    if cursor.fetchone()[0] == 0:
        default_modules = [
            ("mod-soldering-basic", "Praktikum Soldering & Desoldering Dasar", "Inspeksi kualitas sambungan solder pad, void, dan deteksi solder bridge pada board latihan."),
            ("mod-min-sys-avr", "Praktikum Perakitan Minimum System AVR / Arduino", "Verifikasi orientasi IC (pin 1 notch), polaritas kapasitor elko/dioda, dan solder pin header."),
            ("mod-power-supply", "Praktikum Modul Regulator Catu Daya (Power Supply)", "Pemeriksaan jalur komponen regulator, dioda bridge, trafo, dan jalur sambungan PCB.")
        ]
        cursor.executemany("INSERT INTO modules VALUES (?, ?, ?);", default_modules)
        conn.commit()
    conn.close()
