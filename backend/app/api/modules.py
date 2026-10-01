import sqlite3
from typing import List
from fastapi import APIRouter
from backend.app.schemas.module import ModuleItem
from backend.app.core.config import DB_PATH

router = APIRouter()

@router.get("/modules", response_model=List[ModuleItem])
def get_practicum_modules():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM modules;")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]
