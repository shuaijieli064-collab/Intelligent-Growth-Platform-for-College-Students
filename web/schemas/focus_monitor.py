from pydantic import BaseModel
from typing import List, Dict


class FocusDailyData(BaseModel):
    date: str
    focus_score: float
    total_minutes: int


class FocusTrendPoint(BaseModel):
    date: str
    score: float


class FocusMonitorResponse(BaseModel):
    realtime_score: float
    level: str
    trend: str
    last_14_days: List[FocusDailyData]
    last_30_days: List[FocusDailyData]
