from typing import Optional
from pydantic import BaseModel


class CourseResponse(BaseModel):
    course_id: Optional[int] = None
    course_code: str = ""
    course_name: str = ""
    credit: float = 0.0
    semester: str = ""
    is_compulsory: bool = True
    prerequisite_course_id: Optional[int] = None

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    credit: float = 0.0
    semester: str = ""
    is_compulsory: bool = True
    prerequisite_course_id: Optional[int] = None


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    credit: Optional[float] = None
    semester: Optional[str] = None
    is_compulsory: Optional[bool] = None
    prerequisite_course_id: Optional[int] = None


class StudentCourseResponse(BaseModel):
    id: Optional[int] = None
    student_id: int
    course_id: int
    course_name: str = ""
    usual_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    predicted_final: Optional[float] = None
