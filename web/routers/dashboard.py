import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.dashboard import (
    DashboardResponse,
    StudentInfo,
    HealthDimensions,
    RiskAlertItem,
    CourseDistributionItem,
    GradeTrendItem,
    TodayTask,
)
from web.schemas.common import ApiResponse
from web.dependencies import (
    get_student_dao, get_risk_dao, get_db, get_current_student_id,
    get_course_dao, get_student_course_dao, get_study_record_dao, get_health_dao,
)
from data_layer.dao.student_dao import StudentDAO
from data_layer.dao.risk_dao import RiskDAO
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.health_dao import HealthDAO
from data_layer.database import DatabaseManager
from business_layer.digital_twin import DigitalTwin
from datetime import date


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/me", response_model=ApiResponse[DashboardResponse])
def get_dashboard(
    student_id: int = Depends(get_current_student_id),
    student_dao: StudentDAO = Depends(get_student_dao),
    risk_dao: RiskDAO = Depends(get_risk_dao),
    db: DatabaseManager = Depends(get_db),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    twin = DigitalTwin(student_id, db)
    health_result = twin.assess_overall()
    twin.save_assessment()

    all_alerts = risk_dao.get_by_student(student_id)
    active_alerts = [a for a in all_alerts if not a.is_resolved]
    recent_alerts = all_alerts[:10]

    return ApiResponse(
        data=DashboardResponse(
            student=StudentInfo.model_validate(student),
            overall_health=health_result.overall,
            risk_level=health_result.risk_level.value,
            active_alert_count=len(active_alerts),
            dimensions=HealthDimensions(
                academic=health_result.academic,
                physical=health_result.physical,
                mental=health_result.mental,
                social=health_result.social,
            ),
            recent_alerts=[RiskAlertItem.model_validate(a) for a in recent_alerts],
        )
    )


@router.get("/courses/distribution", response_model=ApiResponse[list[CourseDistributionItem]])
def get_course_distribution(
    student_id: int = Depends(get_current_student_id),
    course_dao: CourseDAO = Depends(get_course_dao),
):
    courses = course_dao.get_by_student(student_id)
    result = [CourseDistributionItem(course_name=c.course_name, count=1) for c in courses]
    return ApiResponse(data=result)


@router.get("/grades/trend", response_model=ApiResponse[list[GradeTrendItem]])
def get_grade_trend(
    student_id: int = Depends(get_current_student_id),
    health_dao: HealthDAO = Depends(get_health_dao),
):
    assessments = health_dao.get_history(student_id)
    result = [
        GradeTrendItem(
            date=str(a.assessment_date) if a.assessment_date else "",
            score=a.overall_health,
        )
        for a in assessments
    ]
    return ApiResponse(data=result)


@router.get("/tasks/today", response_model=ApiResponse[list[TodayTask]])
def get_today_tasks(
    student_id: int = Depends(get_current_student_id),
    study_record_dao: StudyRecordDAO = Depends(get_study_record_dao),
):
    today = date.today()
    records = study_record_dao.get_by_student(student_id, days=1)
    result = [
        TodayTask(
            task_id=r.get("record_id", 0),
            title=r.get("notes", "学习记录") or "学习记录",
            due_time=str(r.get("study_date", today)),
            completed=(r.get("task_completed", 0) or 0) > 0,
        )
        for r in records
    ]
    return ApiResponse(data=result)
