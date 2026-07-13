from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class GrowthReportListItem(BaseModel):
    id: int
    student_id: int
    report_type: str
    period_start: str
    period_end: str
    title: str
    created_at: Optional[datetime] = None


class GenerateReportRequest(BaseModel):
    report_type: str


class GrowthReportDetail(BaseModel):
    id: int
    report_type: str
    title: str
    period_start: str
    period_end: str
    academic_score: float
    physical_score: float
    mental_score: float
    social_score: float
    overall_score: float
    total_study_hours: float
    task_completion_rate: float
    avg_focus_score: float
    active_days: int
    highlights: List[str]
    suggestions: List[str]
    created_at: Optional[datetime] = None
