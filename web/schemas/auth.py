from typing import Optional
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: int
    username: str
    email: str
    student_id: Optional[int] = None


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    student_id: Optional[int] = None
    # student 信息（如果已关联）
    name: Optional[str] = None
    student_no: Optional[str] = None
    grade_level: Optional[str] = None
    major: Optional[str] = None
