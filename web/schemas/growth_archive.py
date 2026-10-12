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


class CourseScoreItem(BaseModel):
    course_name: str
    usual_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None


class DailyStudyItem(BaseModel):
    date: str
    hours: float


class WeakPointItem(BaseModel):
    kp_name: str
    mastery: float


class AlertItem(BaseModel):
    type: str
    level: str
    message: str


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
    daily_study: List[DailyStudyItem] = []
    courses: List[CourseScoreItem] = []
    avg_final_score: Optional[float] = None
    weak_points: List[WeakPointItem] = []
    alerts: List[AlertItem] = []
    created_at: Optional[datetime] = None
