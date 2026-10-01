from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class InspectionTaskResponse(BaseModel):
    task_id: str
    status: str
    module_id: str
    created_at: str

class InspectionResultDetail(BaseModel):
    task_id: str
    module_id: str
    status: str
    score: float
    lighting_warning: Optional[str] = None
    detected_defects: List[Dict[str, Any]]
    recommendations: List[str]
    processed_at: str
