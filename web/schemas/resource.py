from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ResourceItem(BaseModel):
    id: Optional[int] = None
    student_id: int
    kp_id: Optional[int] = None
    kp_name: Optional[str] = None
    resource_type: str
    title: str
    url: str
    reason: str = ""
    is_completed: bool = False
    created_at: Optional[datetime] = None
