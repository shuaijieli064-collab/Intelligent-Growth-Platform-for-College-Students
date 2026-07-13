import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, Query

from web.schemas.risk_warning import RiskAlertItem, BatchDeleteRequest
from web.schemas.common import ApiResponse
from web.dependencies import get_risk_dao, get_db, get_current_student_id
from data_layer.dao.risk_dao import RiskDAO
from data_layer.database import DatabaseManager
from business_layer.risk_warning import RiskWarningSystem


router = APIRouter(prefix="/api/risk-warning", tags=["risk-warning"])


@router.get("", response_model=ApiResponse[list[RiskAlertItem]])
def get_alerts(
    filter: str = Query("all", pattern="^(all|unresolved|resolved)$"),
    student_id: int = Depends(get_current_student_id),
    dao: RiskDAO = Depends(get_risk_dao),
    db: DatabaseManager = Depends(get_db),
):
    system = RiskWarningSystem(db)
    system.evaluate_and_save(student_id)

    if filter == "unresolved":
        alerts = dao.get_by_student(student_id, unresolved_only=True)
    elif filter == "resolved":
        all_alerts = dao.get_by_student(student_id)
        alerts = [a for a in all_alerts if a.is_resolved]
    else:
        alerts = dao.get_by_student(student_id)

    return ApiResponse(data=[RiskAlertItem.model_validate(a) for a in alerts])


@router.put("/{alert_id}/resolve", response_model=ApiResponse[dict])
def resolve_alert(
    alert_id: int,
    dao: RiskDAO = Depends(get_risk_dao),
):
    success = dao.resolve(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="告警不存在")
    return ApiResponse(data={"alert_id": alert_id}, message="标记已处理成功")


@router.delete("/{alert_id}", response_model=ApiResponse[dict])
def delete_alert(
    alert_id: int,
    dao: RiskDAO = Depends(get_risk_dao),
):
    success = dao.delete(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="告警不存在")
    return ApiResponse(data={"alert_id": alert_id}, message="删除成功")


@router.delete("/batch", response_model=ApiResponse[dict])
def batch_delete_alerts(
    req: BatchDeleteRequest,
    student_id: int = Depends(get_current_student_id),
    dao: RiskDAO = Depends(get_risk_dao),
):
    deleted = 0
    for alert_id in req.alert_ids:
        if dao.delete(alert_id):
            deleted += 1
    return ApiResponse(
        data={"deleted_count": deleted},
        message=f"成功删除 {deleted} 条告警",
    )
