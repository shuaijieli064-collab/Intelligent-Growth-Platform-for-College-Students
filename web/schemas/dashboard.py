from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StudentInfo(BaseModel):
    student_id: Optional[int] = None
    name: str
    student_no: str
    major: str
    grade_level: str

    class Config:
        from_attributes = True


class HealthDimensions(BaseModel):
    academic: float
    physical: float
    mental: float
    social: float


class RiskAlertItem(BaseModel):
    alert_id: Optional[int] = None
    alert_type: str
    risk_level: str
    alert_message: str
    created_at: Optional[datetime] = None
    is_resolved: bool

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    student: StudentInfo
    overall_health: float
    risk_level: str
    active_alert_count: int
    dimensions: HealthDimensions
    recent_alerts: list[RiskAlertItem]


class CourseDistributionItem(BaseModel):
    course_name: str
    count: int


class GradeTrendItem(BaseModel):
    date: str
    score: float


class TodayTask(BaseModel):
    task_id: int
    title: str
    due_time: str
    completed: bool
