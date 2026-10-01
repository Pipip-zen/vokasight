from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class InspectionTaskResponse(BaseModel):
    task_id: str
    status: str
    module_id: str
    created_at: str
    student_id: Optional[str] = None
    message: Optional[str] = None

class InspectionResultDetail(BaseModel):
    task_id: str
    module_id: str
    status: str
    score: float
    student_id: Optional[str] = None
    lighting_warning: Optional[str] = None
    detected_defects: List[Dict[str, Any]]
    recommendations: List[str]
    recommendations_text: Optional[str] = None
    processed_at: str

