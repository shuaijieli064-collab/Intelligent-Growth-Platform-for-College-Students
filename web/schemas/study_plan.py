from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class StudyPlanTask(BaseModel):
    day: int
    task: str
    type: str
    duration_min: int
    priority: str
    done: bool


class StudyPlan(BaseModel):
    id: Optional[int] = None
    student_id: int
    subject: str
    goal_score: float
    exam_date: date
    plan_content: list[StudyPlanTask] = []
    status: str = "active"
    progress: float = 0.0
    created_at: Optional[datetime] = None


class GeneratePlanRequest(BaseModel):
    subject: str
    course_id: int
    goal_score: float
    exam_date: date
    daily_minutes: int = 90


class UpdateTaskRequest(BaseModel):
    done: bool
