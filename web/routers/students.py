from fastapi import APIRouter, Depends, HTTPException
from typing import List

from web.schemas.student import StudentResponse, StudentUpdate
from web.schemas.common import ApiResponse
from web.dependencies import get_student_dao, get_current_user, get_current_student_id
from data_layer.dao.student_dao import StudentDAO
from data_layer.models import User

router = APIRouter(prefix="/api", tags=["students"])


@router.get("/students", response_model=ApiResponse[List[StudentResponse]])
def get_my_students(
    current_user: User = Depends(get_current_user),
    dao: StudentDAO = Depends(get_student_dao),
):
    """返回当前用户关联的学生信息（单条）."""
    if current_user.student_id is None:
        raise HTTPException(status_code=400, detail="尚未关联学生信息")
    student = dao.get_by_id(current_user.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return ApiResponse(data=[StudentResponse.model_validate(student)])


@router.get("/students/me", response_model=ApiResponse[StudentResponse])
def get_my_student(
    student_id: int = Depends(get_current_student_id),
    dao: StudentDAO = Depends(get_student_dao),
):
    student = dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return ApiResponse(data=StudentResponse.model_validate(student))


@router.put("/students/me", response_model=ApiResponse[StudentResponse])
def update_my_student(
    student_in: StudentUpdate,
    student_id: int = Depends(get_current_student_id),
    dao: StudentDAO = Depends(get_student_dao),
):
    existing = dao.get_by_id(student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="学生不存在")
    update_data = student_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    dao.update(existing)
    updated = dao.get_by_id(student_id)
    return ApiResponse(data=StudentResponse.model_validate(updated), message="更新成功")


@router.get("/me", response_model=ApiResponse[dict])
def get_me(
    current_user: User = Depends(get_current_user),
    dao: StudentDAO = Depends(get_student_dao),
):
    """快捷接口：返回当前 user + student 信息."""
    data = {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "student_id": current_user.student_id,
    }
    if current_user.student_id is not None:
        student = dao.get_by_id(current_user.student_id)
        if student is not None:
            data["student"] = StudentResponse.model_validate(student).model_dump()
    return ApiResponse(data=data)
