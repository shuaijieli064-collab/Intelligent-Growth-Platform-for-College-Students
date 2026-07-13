from pydantic import BaseModel
from typing import List, Dict, Any


class StudyCurvePoint(BaseModel):
    date: str
    study_minutes: float
    focus_score: float
    avg_7day: float


class StudyCurveResponse(BaseModel):
    data: List[StudyCurvePoint]


class HealthTrendPoint(BaseModel):
    date: str
    overall: float
    academic: float
    physical: float
    mental: float
    social: float


class HealthTrendResponse(BaseModel):
    data: List[HealthTrendPoint]


class GradeRadarCourse(BaseModel):
    course_name: str
    score: float


class GradeRadarResponse(BaseModel):
    courses: List[GradeRadarCourse]
    dimensions: List[str]


class KnowledgeHeatmapCell(BaseModel):
    course_name: str
    kp_name: str
    mastery: float


class KnowledgeHeatmapResponse(BaseModel):
    courses: List[str]
    kps: List[str]
    data: List[KnowledgeHeatmapCell]
