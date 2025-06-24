from pydantic import BaseModel
from typing import List

class ScopeRequest(BaseModel):
    project_type: str
    level_of_work: str
    finish_level: str
    rooms: List[str]
    description: str