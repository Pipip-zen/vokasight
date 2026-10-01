from pydantic import BaseModel

class ModuleItem(BaseModel):
    id: str
    name: str
    description: str
