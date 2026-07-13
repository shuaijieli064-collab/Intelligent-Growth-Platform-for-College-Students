from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StudentResponse(BaseModel):
    student_id: Optional[int] = None
    student_no: str = ""
    name: str = ""
    gender: str = "M"
    grade_level: str = ""
    major: str = ""
    enrollment_year: int = 2024
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    student_no: str
    name: str
    gender: str = "M"
    grade_level: str = ""
    major: str = ""
    enrollment_year: int = 2024


class StudentUpdate(BaseModel):
    student_no: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    grade_level: Optional[str] = None
    major: Optional[str] = None
    enrollment_year: Optional[int] = None
