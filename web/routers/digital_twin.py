import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, Query

from web.schemas.digital_twin import (
    DigitalTwinResponse,
    HealthDimensions,
    HealthAssessmentItem,
)
from web.schemas.common import ApiResponse, PaginatedResponse, PaginatedData
from web.dependencies import get_db, get_current_student_id
from data_layer.database import DatabaseManager
from business_layer.digital_twin import DigitalTwin


router = APIRouter(prefix="/api/digital-twin", tags=["digital-twin"])


@router.get("/me", response_model=ApiResponse[DigitalTwinResponse])
def get_digital_twin(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    twin = DigitalTwin(student_id, db)
    result = twin.assess_overall()
    twin.save_assessment()

    return ApiResponse(
        data=DigitalTwinResponse(
            overall_health=result.overall,
            risk_level=result.risk_level.value,
            dimensions=HealthDimensions(
                academic=result.academic,
                physical=result.physical,
                mental=result.mental,
                social=result.social,
            ),
        )
    )


@router.get("/me/history", response_model=PaginatedResponse[HealthAssessmentItem])
def get_history(
    student_id: int = Depends(get_current_student_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DatabaseManager = Depends(get_db),
):
    twin = DigitalTwin(student_id, db)
    all_history = twin.get_history()
    total = len(all_history)

    start = (page - 1) * page_size
    end = start + page_size
    items = all_history[start:end]

    return PaginatedResponse(
        data=PaginatedData(
            items=[HealthAssessmentItem.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )
