from datetime import date
from typing import Optional
from pydantic import BaseModel


class HealthDimensions(BaseModel):
    academic: float
    physical: float
    mental: float
    social: float


class DigitalTwinResponse(BaseModel):
    overall_health: float
    risk_level: str
    dimensions: HealthDimensions
    assessment_date: Optional[date] = None


class HealthAssessmentItem(BaseModel):
    assessment_id: Optional[int] = None
    assessment_date: Optional[date] = None
    academic_score: float
    physical_score: float
    mental_score: float
    social_score: float
    overall_health: float
    risk_level: str

    class Config:
        from_attributes = True
