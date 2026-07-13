import sys
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


# JWT 密钥
SECRET_KEY = "student-growth-platform-secret-key-2024"
ALGORITHM = "HS256"

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
            charset=DB_CONFIG["charset"],
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
