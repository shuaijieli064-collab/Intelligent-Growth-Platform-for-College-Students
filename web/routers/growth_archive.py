import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.growth_archive import (
    GrowthReportListItem,
    GenerateReportRequest,
    GrowthReportDetail,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_current_student_id
from data_layer.database import DatabaseManager
from business_layer.growth_archiver import GrowthArchiver


router = APIRouter(prefix="/api/growth-archive", tags=["growth_archive"])


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

    return ApiResponse(
        data=GrowthReportDetail(
            id=report.get("id", 0),
            report_type=report.get("report_type", req.report_type),
            title=report.get("summary", report.get("title", "")),
            period_start=str(report.get("period_start", "")),
            period_end=str(report.get("period_end", "")),
            academic_score=float(report.get("detail", {}).get("health", {}).get("academic", 0)),
            physical_score=float(report.get("detail", {}).get("health", {}).get("physical", 0)),
            mental_score=float(report.get("detail", {}).get("health", {}).get("mental", 0)),
            social_score=float(report.get("detail", {}).get("health", {}).get("social", 0)),
            overall_score=float(report.get("detail", {}).get("health", {}).get("overall", 0)),
            total_study_hours=float(report.get("detail", {}).get("study", {}).get("total_hours", 0)),
            task_completion_rate=0.0,
            avg_focus_score=float(report.get("detail", {}).get("study", {}).get("avg_focus", 0)),
            active_days=int(report.get("detail", {}).get("study", {}).get("active_days", 0)),
            highlights=[],
            suggestions=[],
            created_at=report.get("created_at"),
        )
    )


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

    return ApiResponse(
        data=GrowthReportDetail(
            id=report.get("id", report_id),
            report_type=report.get("report_type", "weekly"),
            title=report.get("summary", report.get("title", "")),
            period_start=str(report.get("period_start", "")),
            period_end=str(report.get("period_end", "")),
            academic_score=float(report.get("detail", {}).get("health", {}).get("academic", 0)),
            physical_score=float(report.get("detail", {}).get("health", {}).get("physical", 0)),
            mental_score=float(report.get("detail", {}).get("health", {}).get("mental", 0)),
            social_score=float(report.get("detail", {}).get("health", {}).get("social", 0)),
            overall_score=float(report.get("detail", {}).get("health", {}).get("overall", 0)),
            total_study_hours=float(report.get("detail", {}).get("study", {}).get("total_hours", 0)),
            task_completion_rate=0.0,
            avg_focus_score=float(report.get("detail", {}).get("study", {}).get("avg_focus", 0)),
            active_days=int(report.get("detail", {}).get("study", {}).get("active_days", 0)),
            highlights=[],
            suggestions=[],
            created_at=report.get("created_at"),
        )
    )
