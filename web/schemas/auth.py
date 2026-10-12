from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    email: str = Field(max_length=128)

    @field_validator("username")
    @classmethod
    def _username_charset(cls, v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"[A-Za-z0-9_\u4e00-\u9fa5.-]{3,32}", v):
            raise ValueError("用户名仅支持字母、数字、中文、_ . -（3-32位）")
        return v

    @field_validator("email")
    @classmethod
    def _email_format(cls, v: str) -> str:
        v = v.strip()
        if not _EMAIL_RE.fullmatch(v):
            raise ValueError("邮箱格式不正确")
        return v


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)


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
