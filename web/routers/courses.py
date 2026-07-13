from fastapi import APIRouter, Depends, HTTPException
from typing import List

from web.schemas.course import CourseResponse, CourseCreate, StudentCourseResponse
from web.schemas.common import ApiResponse
from web.dependencies import get_course_dao, get_student_course_dao, get_student_dao, get_current_student_id
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.models import Course

router = APIRouter(prefix="/api", tags=["courses"])


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
def get_course(course_id: int, dao: CourseDAO = Depends(get_course_dao)):
    course = dao.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return ApiResponse(data=CourseResponse.model_validate(course))


@router.post("/courses", response_model=ApiResponse[CourseResponse])
def create_course(course_in: CourseCreate, dao: CourseDAO = Depends(get_course_dao)):
    course = Course(**course_in.model_dump())
    course_id = dao.create(course)
    created = dao.get_by_id(course_id)
    return ApiResponse(data=CourseResponse.model_validate(created), message="创建成功")


@router.delete("/courses/{course_id}", response_model=ApiResponse[dict])
def delete_course(course_id: int, dao: CourseDAO = Depends(get_course_dao)):
    existing = dao.get_by_id(course_id)
    if not existing:
        raise HTTPException(status_code=404, detail="课程不存在")
    success = dao.delete(course_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除失败")
    return ApiResponse(data={"course_id": course_id}, message="删除成功")
