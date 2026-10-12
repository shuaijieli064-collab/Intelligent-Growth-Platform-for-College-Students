"""认证路由."""
import os
import secrets
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request

from web.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from web.schemas.common import ApiResponse
from web.dependencies import (
    get_user_dao,
    get_student_dao,
    get_current_user,
    SECRET_KEY,
    get_db,
    check_rate_limit,
)
from data_layer.dao.user_dao import UserDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.models import User, Student
from data_layer.database import DatabaseManager
from business_layer.seed_data import seed_default_courses, seed_demo_data

router = APIRouter(prefix="/api/auth", tags=["auth"])

# token 有效期：默认 1 天（可通过环境变量覆盖）
_TOKEN_TTL_HOURS = int(os.environ.get("TOKEN_TTL_HOURS", "24"))


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _create_token(user_id: int, student_id: int | None) -> str:
    payload = {
        "user_id": user_id,
        "student_id": student_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=_TOKEN_TTL_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@router.post("/register", response_model=ApiResponse[AuthResponse])
def register(
    req: RegisterRequest,
    request: Request,
    user_dao: UserDAO = Depends(get_user_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    db: DatabaseManager = Depends(get_db),
):
    # 注册限流：每 IP 每 10 分钟最多 5 次
    check_rate_limit(f"register:{_client_ip(request)}", max_calls=5, window_seconds=600)

    # 检查用户名是否已存在
    if user_dao.get_by_username(req.username) is not None:
        raise HTTPException(status_code=409, detail="用户名已存在")

    # 创建 student 记录（时间戳 + 随机后缀避免碰撞）
    student_no = f"STU{int(time.time() * 1000)}{secrets.randbelow(1000):03d}"
    student = Student(student_no=student_no, name=req.username)
    student_id = student_dao.create(student)

    # 初始化预置课程和知识点
    seed_default_courses(student_id, db)

    # 新用户演示数据（成绩/学习/健康/掌握度，幂等且不阻断注册）
    seed_demo_data(student_id, db)

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
def login(
    req: LoginRequest,
    request: Request,
    user_dao: UserDAO = Depends(get_user_dao),
):
    # 撞库防护：每 IP 每分钟最多 10 次，每账号每分钟最多 5 次
    ip = _client_ip(request)
    check_rate_limit(f"login_ip:{ip}", max_calls=10, window_seconds=60)
    check_rate_limit(f"login_user:{req.username}", max_calls=5, window_seconds=60)

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


@router.put("/password", response_model=ApiResponse[dict])
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    user_dao: UserDAO = Depends(get_user_dao),
):
    if not bcrypt.checkpw(
        req.old_password.encode("utf-8"),
        current_user.password_hash.encode("utf-8"),
    ):
        raise HTTPException(status_code=400, detail="原密码不正确")

    if req.old_password == req.new_password:
        raise HTTPException(status_code=422, detail="新密码不能与原密码相同")

    new_hash = bcrypt.hashpw(
        req.new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    user_dao.update_password(current_user.user_id, new_hash)
    return ApiResponse(data={}, message="密码修改成功")
