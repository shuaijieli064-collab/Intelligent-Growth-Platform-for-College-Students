from fastapi import APIRouter, Depends, HTTPException
from typing import List

from web.schemas.course import CourseResponse, CourseCreate, StudentCourseResponse
from web.schemas.common import ApiResponse
from web.dependencies import (
    get_course_dao, get_student_course_dao, get_student_dao,
    get_current_user, get_current_student_id, get_admin_usernames,
    get_db,
)
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.database import DatabaseManager
from data_layer.models import Course, User
from business_layer.seed_data import PRESET_COURSES, seed_default_courses

router = APIRouter(prefix="/api", tags=["courses"])

_PRESET_NAMES = {p["course_name"] for p in PRESET_COURSES}
_PRESET_CODES = {p["course_code"] for p in PRESET_COURSES}


def _is_preset_course(c: Course) -> bool:
    """系统预置课程（种子数据），学生不可删除课程本体，仅可移出自己的课程列表."""
    return c.course_name in _PRESET_NAMES or c.course_code in _PRESET_CODES


@router.get("/courses", response_model=ApiResponse[List[CourseResponse]])
def get_my_courses(
    student_id: int = Depends(get_current_student_id),
    dao: CourseDAO = Depends(get_course_dao),
):
    """返回当前用户选修的课程."""
    courses = dao.get_by_student(student_id)
    return ApiResponse(data=[CourseResponse.model_validate(c) for c in courses])


@router.get("/courses/my", response_model=ApiResponse[List[StudentCourseResponse]])
def get_student_courses(
    student_id: int = Depends(get_current_student_id),
    student_dao: StudentDAO = Depends(get_student_dao),
    sc_dao: StudentCourseDAO = Depends(get_student_course_dao),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    scores = sc_dao.get_student_scores(student_id)
    result = []
    for s in scores:
        result.append(StudentCourseResponse(
            id=s.get("id"),
            student_id=s.get("student_id", student_id),
            course_id=s.get("course_id"),
            course_name=s.get("course_name", ""),
            usual_score=s.get("usual_score"),
            midterm_score=s.get("midterm_score"),
            final_score=s.get("final_score"),
            predicted_final=s.get("predicted_final"),
        ))
    return ApiResponse(data=result)


@router.get("/courses/{course_id}", response_model=ApiResponse[CourseResponse])
def get_course(
    course_id: int,
    _: User = Depends(get_current_user),
    dao: CourseDAO = Depends(get_course_dao),
):
    course = dao.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return ApiResponse(data=CourseResponse.model_validate(course))


@router.post("/courses", response_model=ApiResponse[CourseResponse])
def create_course(
    course_in: CourseCreate,
    current_user: User = Depends(get_current_user),
    dao: CourseDAO = Depends(get_course_dao),
    sc_dao: StudentCourseDAO = Depends(get_student_course_dao),
):
    owner_id = current_user.student_id
    course = Course(**course_in.model_dump(), created_by=owner_id)
    course_id = dao.create(course)

    # 创建者自动选修，保证新建课程立即在“我的课程”中可见
    if owner_id is not None:
        enrolled = {c.course_id for c in dao.get_by_student(owner_id)}
        if course_id not in enrolled:
            sc_dao.enroll(owner_id, course_id)

    created = dao.get_by_id(course_id)
    return ApiResponse(data=CourseResponse.model_validate(created), message="创建成功")


@router.delete("/courses/{course_id}", response_model=ApiResponse[dict])
def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    dao: CourseDAO = Depends(get_course_dao),
    sc_dao: StudentCourseDAO = Depends(get_student_course_dao),
):
    existing = dao.get_by_id(course_id)
    if not existing:
        raise HTTPException(status_code=404, detail="课程不存在")

    owner = current_user.student_id
    admins = get_admin_usernames()
    is_admin = bool(admins) and current_user.username in admins

    # 管理员或课程创建者：真正删除课程（级联移除所有选课与成绩）
    if is_admin or (owner is not None and existing.created_by == owner):
        if not dao.delete(course_id):
            raise HTTPException(status_code=500, detail="删除失败")
        return ApiResponse(data={"course_id": course_id}, message="课程删除成功")

    enrolled = owner is not None and any(
        c.course_id == course_id for c in dao.get_by_student(owner)
    )

    # 迁移前创建的自建课程（created_by 为 NULL 且非预置名）：选修者可删除课程本体
    legacy_custom = (
        existing.created_by is None
        and not _is_preset_course(existing)
        and not admins
    )
    if legacy_custom and owner is not None and enrolled:
        if not dao.delete(course_id):
            raise HTTPException(status_code=500, detail="删除失败")
        return ApiResponse(data={"course_id": course_id}, message="课程删除成功")

    # 其余情况（预置课程 / 他人创建的课程）：仅移除自己的选课记录，
    # 共享课程数据保留，避免级联清掉其他学生的选课与成绩
    if owner is None:
        raise HTTPException(status_code=403, detail="无权操作该课程")
    if not enrolled:
        raise HTTPException(status_code=403, detail="未选修该课程")
    if not sc_dao.unenroll(owner, course_id):
        raise HTTPException(status_code=500, detail="移除失败")
    return ApiResponse(data={"course_id": course_id}, message="已从我的课程移除")


@router.post("/courses/restore-defaults", response_model=ApiResponse[dict])
def restore_default_courses(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    """恢复系统默认课程（幂等：已选修的不会重复添加，无成绩数据）."""
    before = {c.course_id for c in CourseDAO(db).get_by_student(student_id)}
    seed_default_courses(student_id, db)
    after = {c.course_id for c in CourseDAO(db).get_by_student(student_id)}
    added = len(after - before)
    return ApiResponse(data={"added": added}, message=f"已恢复 {added} 门默认课程")
