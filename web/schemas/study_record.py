from datetime import date
from typing import Optional
from pydantic import BaseModel


class StudyRecordResponse(BaseModel):
    record_id: Optional[int] = None
    student_id: int
    course_id: Optional[int] = None
    study_date: Optional[date] = None
    study_hours: float = 0.0
    task_completed: int = 0
    focus_score: Optional[int] = None
    notes: Optional[str] = None
    course_name: Optional[str] = None

    class Config:
        from_attributes = True


class StudyRecordCreate(BaseModel):
    study_date: date
    study_hours: float
    course_id: Optional[int] = None
    task_completed: int = 0
    focus_score: Optional[int] = None
    notes: Optional[str] = None
