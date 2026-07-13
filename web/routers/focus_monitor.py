import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends

from web.schemas.focus_monitor import FocusMonitorResponse, FocusDailyData
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_current_student_id
from data_layer.database import DatabaseManager
from business_layer.focus_monitor import FocusMonitor


router = APIRouter(prefix="/api/focus-monitor", tags=["focus_monitor"])


@router.get("", response_model=ApiResponse[FocusMonitorResponse])
def get_focus_data(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    monitor = FocusMonitor(db, student_id)

    realtime_score = monitor.get_current_focus()
    level = monitor.get_focus_level()
    trend_data = monitor.get_focus_trend(days=14)
    daily_14 = monitor.get_daily_focus(days=14)
    daily_30 = monitor.get_daily_focus(days=30)

    trend_map = {"improving": "改善中", "declining": "下降中", "stable": "稳定"}
    trend_text = trend_map.get(trend_data.get("trend", "stable"), "稳定")

    return ApiResponse(
        data=FocusMonitorResponse(
            realtime_score=realtime_score,
            level=level,
            trend=trend_text,
            last_14_days=[
                FocusDailyData(date=d["date"], focus_score=d["avg_focus"], total_minutes=int(d["hours"] * 60))
                for d in daily_14
            ],
            last_30_days=[
                FocusDailyData(date=d["date"], focus_score=d["avg_focus"], total_minutes=int(d["hours"] * 60))
                for d in daily_30
            ],
        )
    )
