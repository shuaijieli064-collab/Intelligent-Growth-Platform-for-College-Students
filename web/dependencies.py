import os
import secrets
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from data_layer.database import DatabaseManager
from data_layer.dao.student_dao import StudentDAO
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.risk_dao import RiskDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.health_dao import HealthDAO
from data_layer.dao.user_dao import UserDAO
from data_layer.models import User
from config import DB_CONFIG


# JWT 密钥（必须通过环境变量配置；生产环境缺失时拒绝启动）
ALGORITHM = "HS256"


def _load_secret_key() -> str:
    env_key = os.environ.get("JWT_SECRET_KEY")
    if env_key:
        return env_key
    is_production = (
        os.environ.get("ENV", "").lower() == "production"
        or os.environ.get("RENDER", "").lower() in ("true", "1")
    )
    if is_production:
        raise RuntimeError(
            "生产环境必须设置 JWT_SECRET_KEY 环境变量，拒绝使用默认密钥启动"
        )
    # 开发环境：生成随机密钥并持久化到本地（已 gitignore），
    # 避免使用仓库中公开的固定密钥，同时保证重启后已有 token 不失效
    secret_file = Path(__file__).resolve().parent.parent / ".jwt_secret"
    try:
        if secret_file.exists():
            saved = secret_file.read_text(encoding="utf-8").strip()
            if saved:
                return saved
        new_secret = secrets.token_urlsafe(48)
        secret_file.write_text(new_secret, encoding="utf-8")
        return new_secret
    except OSError:
        # 无法写文件时退回进程内随机密钥（重启后旧 token 失效，可接受）
        return secrets.token_urlsafe(48)


SECRET_KEY = _load_secret_key()

_db_manager: DatabaseManager | None = None


def get_db() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG.get("charset", "utf8mb4"),
            db_type=DB_CONFIG.get("db_type", "mysql"),
        )
    return _db_manager


def get_student_dao() -> StudentDAO:
    return StudentDAO(get_db())


def get_course_dao() -> CourseDAO:
    return CourseDAO(get_db())


def get_student_course_dao() -> StudentCourseDAO:
    return StudentCourseDAO(get_db())


def get_risk_dao() -> RiskDAO:
    return RiskDAO(get_db())


def get_study_record_dao() -> StudyRecordDAO:
    return StudyRecordDAO(get_db())


def get_health_dao() -> HealthDAO:
    return HealthDAO(get_db())


def get_user_dao() -> UserDAO:
    return UserDAO(get_db())


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    user_dao: UserDAO = Depends(get_user_dao),
) -> User:
    """验证 JWT token，返回当前用户."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = user_dao.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="认证已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的认证信息")


def get_current_student_id(current_user: User = Depends(get_current_user)) -> int:
    """获取当前用户的 student_id."""
    if current_user.student_id is None:
        raise HTTPException(status_code=400, detail="尚未关联学生信息")
    return current_user.student_id


def get_admin_usernames() -> set[str]:
    """从环境变量读取管理员用户名名单（逗号分隔）.

    未配置时不限制（仅要求登录），配置后严格校验。
    """
    raw = os.environ.get("ADMIN_USERNAMES", "")
    return {u.strip() for u in raw.split(",") if u.strip()}


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """管理级操作依赖：配置了 ADMIN_USERNAMES 时校验管理员身份."""
    admins = get_admin_usernames()
    if admins and current_user.username not in admins:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


# ── 简单内存滑动窗口限流 ──────────────────────────────────────

_rate_buckets: dict[str, list[float]] = {}
_rate_lock = threading.Lock()
_RATE_MAX_KEYS = 10_000


def check_rate_limit(bucket_key: str, max_calls: int, window_seconds: int) -> None:
    """固定窗口内超过 max_calls 次则抛 429."""
    now = time.monotonic()
    with _rate_lock:
        if len(_rate_buckets) > _RATE_MAX_KEYS:
            _rate_buckets.clear()
        bucket = _rate_buckets.setdefault(bucket_key, [])
        bucket[:] = [t for t in bucket if now - t < window_seconds]
        if len(bucket) >= max_calls:
            raise HTTPException(
                status_code=429, detail="请求过于频繁，请稍后再试"
            )
        bucket.append(now)
