from datetime import date
from typing import Optional
from pydantic import BaseModel


class PhysicalHealthResponse(BaseModel):
    id: Optional[int] = None
    student_id: int
    record_date: Optional[date] = None
    exercise_type: Optional[str] = None
    exercise_duration: int = 0
    sleep_hours: Optional[float] = None
    steps: int = 0

    class Config:
        from_attributes = True


class PhysicalHealthCreate(BaseModel):
    record_date: date
    exercise_type: Optional[str] = None
    exercise_duration: int = 0
    sleep_hours: Optional[float] = None
    steps: int = 0


class MentalHealthResponse(BaseModel):
    id: Optional[int] = None
    student_id: int
    record_date: Optional[date] = None
    mood_score: Optional[int] = None
    stress_level: Optional[int] = None
    anxiety_level: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class MentalHealthCreate(BaseModel):
    record_date: date
    mood_score: Optional[int] = None
    stress_level: Optional[int] = None
    anxiety_level: Optional[int] = None
    notes: Optional[str] = None


class SocialHealthResponse(BaseModel):
    id: Optional[int] = None
    student_id: int
    record_date: Optional[date] = None
    activity_type: Optional[str] = None
    duration_minutes: int = 0
    interaction_count: int = 0

    class Config:
        from_attributes = True


class SocialHealthCreate(BaseModel):
    record_date: date
    activity_type: Optional[str] = None
    duration_minutes: int = 0
    interaction_count: int = 0
