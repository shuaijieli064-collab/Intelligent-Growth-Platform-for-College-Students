from fastapi import APIRouter, Depends, HTTPException
from typing import List

from web.schemas.study_record import StudyRecordResponse, StudyRecordCreate
from web.schemas.common import ApiResponse
from web.dependencies import get_study_record_dao, get_student_dao, get_course_dao, get_db, get_current_student_id
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.dao.course_dao import CourseDAO
from data_layer.database import DatabaseManager
from business_layer.digital_twin import DigitalTwin

router = APIRouter(prefix="/api/study-records", tags=["study-records"])


@router.get("", response_model=ApiResponse[List[StudyRecordResponse]])
def get_study_records(
    student_id: int = Depends(get_current_student_id),
    dao: StudyRecordDAO = Depends(get_study_record_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    course_dao: CourseDAO = Depends(get_course_dao),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    records = dao.get_by_student(student_id, days=30)
    result = []
    for r in records:
        course_name = None
        if r.get("course_id"):
            course = course_dao.get_by_id(r["course_id"])
            course_name = course.course_name if course else None
        result.append(StudyRecordResponse(
            record_id=r.get("record_id"),
            student_id=r.get("student_id", student_id),
            course_id=r.get("course_id"),
            study_date=r.get("study_date"),
            study_hours=r.get("study_hours", 0.0),
            task_completed=r.get("task_completed", 0),
            focus_score=r.get("focus_score"),
            notes=r.get("notes"),
            course_name=course_name,
        ))
    return ApiResponse(data=result)


@router.post("", response_model=ApiResponse[StudyRecordResponse])
def create_study_record(
    record_in: StudyRecordCreate,
    student_id: int = Depends(get_current_student_id),
    dao: StudyRecordDAO = Depends(get_study_record_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    course_dao: CourseDAO = Depends(get_course_dao),
    db: DatabaseManager = Depends(get_db),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if record_in.course_id:
        course = course_dao.get_by_id(record_in.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
    record_id = dao.add_record(
        student_id=student_id,
        study_date=record_in.study_date,
        study_hours=record_in.study_hours,
        course_id=record_in.course_id,
        task_completed=record_in.task_completed,
        focus_score=record_in.focus_score,
        notes=record_in.notes,
    )
    created = dao.get_by_id(record_id)
    if not created:
        raise HTTPException(status_code=500, detail="创建失败")
    course_name = None
    if created.get("course_id"):
        course = course_dao.get_by_id(created["course_id"])
        course_name = course.course_name if course else None
    twin = DigitalTwin(student_id, db)
    twin.save_assessment()
    return ApiResponse(
        data=StudyRecordResponse(
            record_id=created.get("record_id"),
            student_id=created.get("student_id", student_id),
            course_id=created.get("course_id"),
            study_date=created.get("study_date"),
            study_hours=created.get("study_hours", 0.0),
            task_completed=created.get("task_completed", 0),
            focus_score=created.get("focus_score"),
            notes=created.get("notes"),
            course_name=course_name,
        ),
        message="创建成功"
    )


@router.delete("/{record_id}", response_model=ApiResponse[dict])
def delete_study_record(
    record_id: int,
    student_id: int = Depends(get_current_student_id),
    dao: StudyRecordDAO = Depends(get_study_record_dao),
    db: DatabaseManager = Depends(get_db),
):
    # 验证记录属于当前用户
    records = dao.get_all_by_student(student_id)
    if not any(r.get("record_id") == record_id for r in records):
        raise HTTPException(status_code=404, detail="记录不存在或无权访问")
    success = dao.delete(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(data={"record_id": record_id}, message="删除成功")


@router.delete("", response_model=ApiResponse[dict])
def delete_all_study_records(
    student_id: int = Depends(get_current_student_id),
    dao: StudyRecordDAO = Depends(get_study_record_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    db: DatabaseManager = Depends(get_db),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    dao.delete_all_by_student(student_id)
    twin = DigitalTwin(student_id, db)
    twin.save_assessment()
    return ApiResponse(data={"student_id": student_id}, message="已清空全部学习记录")
