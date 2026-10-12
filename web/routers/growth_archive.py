import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.growth_archive import (
    GrowthReportListItem,
    GenerateReportRequest,
    GrowthReportDetail,
    CourseScoreItem,
    DailyStudyItem,
    WeakPointItem,
    AlertItem,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_current_student_id
from data_layer.database import DatabaseManager
from business_layer.growth_archiver import GrowthArchiver


router = APIRouter(prefix="/api/growth-archive", tags=["growth_archive"])


def _to_detail(report: dict, report_type: str) -> GrowthReportDetail:
    detail = report.get("detail", {}) or {}
    health = detail.get("health", {}) or {}
    study = detail.get("study", {}) or {}
    # 与 digital_twin 口径一致：每天按 5 个任务计完成率
    total_tasks = int(study.get("total_tasks", 0) or 0)
    active_days = int(study.get("active_days", 0) or 0)
    completion_rate = min(100.0, total_tasks / max(1, active_days * 5) * 100)
    return GrowthReportDetail(
        id=report.get("id", 0),
        report_type=report.get("report_type", report_type),
        title=report.get("summary", report.get("title", "")),
        period_start=str(report.get("period_start", "")),
        period_end=str(report.get("period_end", "")),
        academic_score=float(health.get("academic", 0)),
        physical_score=float(health.get("physical", 0)),
        mental_score=float(health.get("mental", 0)),
        social_score=float(health.get("social", 0)),
        overall_score=float(health.get("overall", 0)),
        total_study_hours=float(study.get("total_hours", 0)),
        task_completion_rate=round(completion_rate, 1),
        avg_focus_score=float(study.get("avg_focus", 0)),
        active_days=int(study.get("active_days", 0)),
        highlights=list(detail.get("highlights", [])),
        suggestions=list(detail.get("suggestions", [])),
        daily_study=[
            DailyStudyItem(date=item.get("date", ""), hours=float(item.get("hours", 0)))
            for item in detail.get("daily_study", [])
        ],
        courses=[
            CourseScoreItem(
                course_name=item.get("course_name", ""),
                usual_score=item.get("usual_score"),
                midterm_score=item.get("midterm_score"),
                final_score=item.get("final_score"),
            )
            for item in detail.get("courses", [])
        ],
        avg_final_score=detail.get("avg_final_score"),
        weak_points=[
            WeakPointItem(kp_name=item.get("kp_name", ""), mastery=float(item.get("mastery", 0)))
            for item in detail.get("weak_points", [])
        ],
        alerts=[
            AlertItem(
                type=item.get("type", ""),
                level=item.get("level", ""),
                message=item.get("message", ""),
            )
            for item in detail.get("alerts", [])
        ],
        created_at=report.get("created_at"),
    )


@router.get("/reports", response_model=ApiResponse[list[GrowthReportListItem]])
def get_reports(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    archiver = GrowthArchiver(db, student_id)
    reports = archiver.get_reports()

    return ApiResponse(
        data=[
            GrowthReportListItem(
                id=r["id"],
                student_id=student_id,
                report_type=r.get("report_type", "weekly"),
                period_start=str(r.get("period_start", "")),
                period_end=str(r.get("period_end", "")),
                title=r.get("summary", r.get("title", "")),
                created_at=r.get("created_at"),
            )
            for r in reports
        ]
    )


@router.post("/generate", response_model=ApiResponse[GrowthReportDetail])
def generate_report(
    req: GenerateReportRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    archiver = GrowthArchiver(db, student_id)
    report = archiver.generate_report(req.report_type)

    if not report:
        raise HTTPException(status_code=400, detail="生成报告失败")

    return ApiResponse(data=_to_detail(report, req.report_type))


@router.get("/{report_id}", response_model=ApiResponse[GrowthReportDetail])
def get_report_detail(
    report_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    archiver = GrowthArchiver(db, student_id)
    report = archiver.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    if report.get("student_id") != student_id:
        raise HTTPException(status_code=403, detail="无权查看该报告")

    return ApiResponse(data=_to_detail(report, report.get("report_type", "weekly")))
