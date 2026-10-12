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

    # 字段校验（避免撞库约束变成 500）
    if "student_no" in update_data:
        sno = (update_data["student_no"] or "").strip()
        if not sno:
            raise HTTPException(status_code=422, detail="学号不能为空")
        if len(sno) > 20:
            raise HTTPException(status_code=422, detail="学号长度不能超过 20 个字符")
        conflict = dao.get_by_student_no(sno)
        if conflict is not None and conflict.student_id != student_id:
            raise HTTPException(status_code=409, detail="学号已被其他同学使用，请更换")
        update_data["student_no"] = sno
    if "name" in update_data:
        name = (update_data["name"] or "").strip()
        if not name:
            raise HTTPException(status_code=422, detail="姓名不能为空")
        if len(name) > 50:
            raise HTTPException(status_code=422, detail="姓名长度不能超过 50 个字符")
        update_data["name"] = name
    if "gender" in update_data and update_data["gender"] not in ("M", "F"):
        raise HTTPException(status_code=422, detail="性别只能是男(M)或女(F)")
    if "grade_level" in update_data and len(update_data["grade_level"] or "") > 10:
        raise HTTPException(status_code=422, detail="年级描述不能超过 10 个字符")
    if "major" in update_data and len(update_data["major"] or "") > 100:
        raise HTTPException(status_code=422, detail="专业名称不能超过 100 个字符")
    if "enrollment_year" in update_data:
        year = update_data["enrollment_year"]
        if year is None or not (2000 <= int(year) <= 2099):
            raise HTTPException(status_code=422, detail="入学年份需在 2000-2099 之间")
        update_data["enrollment_year"] = int(year)

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
