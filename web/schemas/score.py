from typing import Optional
from pydantic import BaseModel


class ScoreResponse(BaseModel):
    id: Optional[int] = None
    student_id: int
    course_id: int
    course_name: str = ""
    usual_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    predicted_final: Optional[float] = None
    has_final_exam: bool = False


class ScoreCreate(BaseModel):
    course_id: int
    usual_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    has_final_exam: bool = False
