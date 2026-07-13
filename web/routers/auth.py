"""认证路由."""
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException

from web.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_user_dao, get_student_dao, get_current_user, SECRET_KEY, get_db
from data_layer.dao.user_dao import UserDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.models import User, Student
from data_layer.database import DatabaseManager
from business_layer.seed_data import seed_default_courses

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _create_token(user_id: int, student_id: int | None) -> str:
    payload = {
        "user_id": user_id,
        "student_id": student_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@router.post("/register", response_model=ApiResponse[AuthResponse])
def register(
    req: RegisterRequest,
    user_dao: UserDAO = Depends(get_user_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    db: DatabaseManager = Depends(get_db),
):
    # 检查用户名是否已存在
    if user_dao.get_by_username(req.username) is not None:
        raise HTTPException(status_code=409, detail="用户名已存在")

    # 创建 student 记录（用时间戳生成唯一学号）
    student_no = f"STU{int(time.time() * 1000)}"
    student = Student(student_no=student_no, name=req.username)
    student_id = student_dao.create(student)

    # 初始化预置课程和知识点
    seed_default_courses(student_id, db)

    # 使用 bcrypt 加密密码
    password_hash = bcrypt.hashpw(
        req.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    # 创建 user 记录，关联 student_id
    user_id = user_dao.create_user(
        username=req.username,
        email=req.email,
        password_hash=password_hash,
        student_id=student_id,
    )

    token = _create_token(user_id, student_id)
    return ApiResponse(
        data=AuthResponse(
            token=token,
            user_id=user_id,
            username=req.username,
            email=req.email,
            student_id=student_id,
        ),
        message="注册成功",
    )


@router.post("/login", response_model=ApiResponse[AuthResponse])
def login(req: LoginRequest, user_dao: UserDAO = Depends(get_user_dao)):
    user = user_dao.get_by_username(req.username)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not bcrypt.checkpw(
        req.password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = _create_token(user.user_id, user.student_id)
    return ApiResponse(
        data=AuthResponse(
            token=token,
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            student_id=user.student_id,
        ),
        message="登录成功",
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
def me(
    current_user: User = Depends(get_current_user),
    student_dao: StudentDAO = Depends(get_student_dao),
):
    resp = UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        student_id=current_user.student_id,
    )
    if current_user.student_id is not None:
        student = student_dao.get_by_id(current_user.student_id)
        if student is not None:
            resp.name = student.name
            resp.student_no = student.student_no
            resp.grade_level = student.grade_level
            resp.major = student.major
    return ApiResponse(data=resp)
