from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RiskAlertItem(BaseModel):
    alert_id: Optional[int] = None
    student_id: int
    alert_type: str
    risk_level: str
    alert_message: str
    rule_triggered: str = ""
    is_resolved: bool = False
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BatchDeleteRequest(BaseModel):
    alert_ids: list[int]
