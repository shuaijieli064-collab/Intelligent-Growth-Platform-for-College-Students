from fastapi import APIRouter, Depends, HTTPException
from typing import List

from web.schemas.score import ScoreResponse, ScoreCreate
from web.schemas.common import ApiResponse
from web.dependencies import get_student_course_dao, get_student_dao, get_course_dao, get_db, get_current_student_id
from data_layer.dao.course_dao import StudentCourseDAO, CourseDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.database import DatabaseManager
from business_layer.digital_twin import DigitalTwin

router = APIRouter(prefix="/api/scores", tags=["scores"])


@router.get("", response_model=ApiResponse[List[ScoreResponse]])
def get_student_scores(
    student_id: int = Depends(get_current_student_id),
    sc_dao: StudentCourseDAO = Depends(get_student_course_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    scores = sc_dao.get_student_scores(student_id)
    result = []
    for s in scores:
        has_final = s.get("final_score") is not None
        result.append(ScoreResponse(
            id=s.get("id"),
            student_id=s.get("student_id", student_id),
            course_id=s.get("course_id"),
            course_name=s.get("course_name", ""),
            usual_score=s.get("usual_score"),
            midterm_score=s.get("midterm_score"),
            final_score=s.get("final_score"),
            predicted_final=s.get("predicted_final"),
            has_final_exam=has_final,
        ))
    return ApiResponse(data=result)


@router.post("", response_model=ApiResponse[ScoreResponse])
def create_or_update_score(
    score_in: ScoreCreate,
    student_id: int = Depends(get_current_student_id),
    sc_dao: StudentCourseDAO = Depends(get_student_course_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    course_dao: CourseDAO = Depends(get_course_dao),
    db: DatabaseManager = Depends(get_db),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    course = course_dao.get_by_id(score_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    scores = sc_dao.get_student_scores(student_id)
    existing = next((s for s in scores if s.get("course_id") == score_in.course_id), None)
    if existing:
        sc_dao.update_scores(
            student_id=student_id,
            course_id=score_in.course_id,
            usual=score_in.usual_score,
            midterm=score_in.midterm_score,
            final=score_in.final_score if score_in.has_final_exam else None,
        )
    else:
        sc_dao.enroll(student_id, score_in.course_id)
        sc_dao.update_scores(
            student_id=student_id,
            course_id=score_in.course_id,
            usual=score_in.usual_score,
            midterm=score_in.midterm_score,
            final=score_in.final_score if score_in.has_final_exam else None,
        )
    scores = sc_dao.get_student_scores(student_id)
    updated = next((s for s in scores if s.get("course_id") == score_in.course_id), None)
    if not updated:
        raise HTTPException(status_code=500, detail="保存失败")
    has_final = updated.get("final_score") is not None
    twin = DigitalTwin(student_id, db)
    twin.save_assessment()
    return ApiResponse(
        data=ScoreResponse(
            id=updated.get("id"),
            student_id=updated.get("student_id", student_id),
            course_id=updated.get("course_id"),
            course_name=updated.get("course_name", ""),
            usual_score=updated.get("usual_score"),
            midterm_score=updated.get("midterm_score"),
            final_score=updated.get("final_score"),
            predicted_final=updated.get("predicted_final"),
            has_final_exam=has_final,
        ),
        message="保存成功"
    )


@router.delete("/{sc_id}", response_model=ApiResponse[dict])
def delete_score(
    sc_id: int,
    student_id: int = Depends(get_current_student_id),
    sc_dao: StudentCourseDAO = Depends(get_student_course_dao),
    db: DatabaseManager = Depends(get_db),
):
    # 验证该成绩记录属于当前用户
    scores = sc_dao.get_student_scores(student_id)
    if not any(s.get("id") == sc_id for s in scores):
        raise HTTPException(status_code=404, detail="记录不存在或无权访问")
    success = sc_dao.delete_score(sc_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(data={"id": sc_id}, message="删除成功")
