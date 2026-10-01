from typing import Optional
from pydantic import BaseModel

class ModuleItem(BaseModel):
    id: str
    name: str
    description: str
    module_id: Optional[str] = None
    module_name: Optional[str] = None

