import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends

from web.schemas.visualization import (
    StudyCurveResponse,
    StudyCurvePoint,
    HealthTrendResponse,
    HealthTrendPoint,
    GradeRadarResponse,
    GradeRadarCourse,
    KnowledgeHeatmapResponse,
    KnowledgeHeatmapCell,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_study_record_dao, get_course_dao, get_current_student_id
from data_layer.database import DatabaseManager
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.course_dao import CourseDAO
from business_layer.digital_twin import DigitalTwin
from business_layer.knowledge_graph import KnowledgeGraph


router = APIRouter(prefix="/api/visualization", tags=["visualization"])


@router.get("/study-curve", response_model=ApiResponse[StudyCurveResponse])
def get_study_curve(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
    study_record_dao: StudyRecordDAO = Depends(get_study_record_dao),
):
    records = study_record_dao.get_by_student(student_id, days=30)

    from collections import defaultdict
    daily_data = defaultdict(lambda: {"minutes": 0, "focus": []})

    for r in records:
        study_date = r.get("study_date")
        if study_date:
            date_str = str(study_date)[:10]
        else:
            continue
        hours = r.get("study_hours", 0) or 0
        minutes = int(float(hours) * 60)
        focus = r.get("focus_score", 0) or 0
        daily_data[date_str]["minutes"] += minutes
        if focus and focus > 0:
            daily_data[date_str]["focus"].append(focus)

    from datetime import datetime, timedelta
    dates = []
    today = datetime.now()
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        dates.append(d.strftime("%Y-%m-%d"))

    result = []
    for i, date in enumerate(dates):
        data = daily_data.get(date, {"minutes": 0, "focus": []})
        focus_avg = sum(data["focus"]) / len(data["focus"]) if data["focus"] else 0

        start = max(0, i - 6)
        window_minutes = []
        for j in range(start, i + 1):
            d = dates[j]
            window_minutes.append(daily_data.get(d, {"minutes": 0})["minutes"])
        avg_7day = sum(window_minutes) / len(window_minutes) if window_minutes else 0

        result.append(
            StudyCurvePoint(
                date=date,
                study_minutes=data["minutes"],
                focus_score=focus_avg,
                avg_7day=avg_7day,
            )
        )

    return ApiResponse(data=StudyCurveResponse(data=result))


@router.get("/health-trend", response_model=ApiResponse[HealthTrendResponse])
def get_health_trend(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    twin = DigitalTwin(student_id, db)
    history = twin.get_history()

    result = []
    for h in history:
        result.append(
            HealthTrendPoint(
                date=str(h.assessment_date)[:10] if h.assessment_date else "",
                overall=h.overall_health,
                academic=h.academic_score,
                physical=h.physical_score,
                mental=h.mental_score,
                social=h.social_score,
            )
        )

    return ApiResponse(data=HealthTrendResponse(data=result))


@router.get("/grade-radar", response_model=ApiResponse[GradeRadarResponse])
def get_grade_radar(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    from web.dependencies import get_student_course_dao
    sc_dao = get_student_course_dao()
    grades = sc_dao.get_student_scores(student_id)
    courses = []

    for g in grades:
        course_name = g.get("course_name", "")
        final_score = g.get("final_score")
        midterm = g.get("midterm_score")
        usual = g.get("usual_score")
        score = final_score or midterm or usual or 0
        if course_name and score:
            courses.append(GradeRadarCourse(course_name=course_name, score=float(score)))

    return ApiResponse(
        data=GradeRadarResponse(
            courses=courses,
            dimensions=[c.course_name for c in courses],
        )
    )


@router.get("/knowledge-heatmap", response_model=ApiResponse[KnowledgeHeatmapResponse])
def get_knowledge_heatmap(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
    course_dao: CourseDAO = Depends(get_course_dao),
):
    courses = course_dao.get_by_student(student_id)
    all_courses = []
    all_kps = []
    cells = []

    for course in courses:
        all_courses.append(course.course_name)
        try:
            kg = KnowledgeGraph(db)
            kg.build_graph(course.course_id)
            colors = kg.mark_mastery(student_id)
            node_labels = kg.get_node_labels()
            nodes, _ = kg.get_graph_data()

            from data_layer.dao.knowledge_dao import KnowledgeDAO
            all_mastery = KnowledgeDAO(db).get_mastery_for_course(student_id, course.course_id)
            mastery_map = {m["kp_id"]: m["mastery_level"] for m in all_mastery}

            for node_id in nodes:
                kp_name = node_labels.get(node_id, f"KP-{node_id}")
                mastery = mastery_map.get(node_id, 0)
                if kp_name not in all_kps:
                    all_kps.append(kp_name)
                cells.append(
                    KnowledgeHeatmapCell(
                        course_name=course.course_name,
                        kp_name=kp_name,
                        mastery=float(mastery),
                    )
                )
        except Exception:
            continue

    return ApiResponse(
        data=KnowledgeHeatmapResponse(
            courses=all_courses,
            kps=all_kps,
            data=cells,
        )
    )
