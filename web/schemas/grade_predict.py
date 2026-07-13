from typing import Optional
from pydantic import BaseModel


class CourseWithScores(BaseModel):
    course_id: int
    course_name: str
    usual_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None


class TrainRequest(BaseModel):
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    algorithm: str = "linear"


class TrainResponse(BaseModel):
    samples: int = 0
    cv_mae: float = 0
    residual_std: float = 0
    algorithm: str = ""
    error: Optional[str] = None


class PredictRequest(BaseModel):
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    usual_score: float
    midterm_score: float


class PredictResponse(BaseModel):
    predicted_score: float
    confidence_interval_low: float
    confidence_interval_high: float
    pass_probability: float
    risk_level: str
