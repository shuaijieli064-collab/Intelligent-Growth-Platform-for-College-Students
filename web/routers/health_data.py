from fastapi import APIRouter, Depends, HTTPException
from typing import List

from web.schemas.health_data import (
    PhysicalHealthResponse, PhysicalHealthCreate,
    MentalHealthResponse, MentalHealthCreate,
    SocialHealthResponse, SocialHealthCreate,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_health_dao, get_student_dao, get_db, get_current_student_id
from data_layer.dao.health_dao import HealthDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.database import DatabaseManager
from data_layer.models import PhysicalHealthRecord, MentalHealthRecord, SocialHealthRecord
from business_layer.digital_twin import DigitalTwin

router = APIRouter(prefix="/api", tags=["health-data"])


# ── 身体健康 ──────────────────────────────────────────────────────

@router.get("/physical-health", response_model=ApiResponse[List[PhysicalHealthResponse]])
def get_physical_health(
    student_id: int = Depends(get_current_student_id),
    dao: HealthDAO = Depends(get_health_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    records = dao.get_physical_records(student_id, days=30)
    result = [PhysicalHealthResponse(
        id=r.get("id"),
        student_id=r.get("student_id", student_id),
        record_date=r.get("record_date"),
        exercise_type=r.get("exercise_type"),
        exercise_duration=r.get("exercise_duration", 0),
        sleep_hours=r.get("sleep_hours"),
        steps=r.get("steps", 0),
    ) for r in records]
    return ApiResponse(data=result)


@router.post("/physical-health", response_model=ApiResponse[PhysicalHealthResponse])
def create_physical_health(
    record_in: PhysicalHealthCreate,
    student_id: int = Depends(get_current_student_id),
    dao: HealthDAO = Depends(get_health_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    db: DatabaseManager = Depends(get_db),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    record = PhysicalHealthRecord(
        student_id=student_id,
        record_date=record_in.record_date,
        exercise_type=record_in.exercise_type,
        exercise_duration=record_in.exercise_duration,
        sleep_hours=record_in.sleep_hours,
        steps=record_in.steps,
    )
    record_id = dao.save_physical_record(record)
    records = dao.get_physical_records(student_id, days=30)
    created = next((r for r in records if r["id"] == record_id), None)
    if not created:
        raise HTTPException(status_code=500, detail="创建失败")
    twin = DigitalTwin(student_id, db)
    twin.save_assessment()
    return ApiResponse(
        data=PhysicalHealthResponse(
            id=created.get("id"),
            student_id=created.get("student_id", student_id),
            record_date=created.get("record_date"),
            exercise_type=created.get("exercise_type"),
            exercise_duration=created.get("exercise_duration", 0),
            sleep_hours=created.get("sleep_hours"),
            steps=created.get("steps", 0),
        ),
        message="创建成功"
    )


@router.delete("/physical-health/{record_id}", response_model=ApiResponse[dict])
def delete_physical_health(
    record_id: int,
    dao: HealthDAO = Depends(get_health_dao),
):
    success = dao.delete_physical(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(data={"id": record_id}, message="删除成功")


# ── 心理健康 ──────────────────────────────────────────────────────

@router.get("/mental-health", response_model=ApiResponse[List[MentalHealthResponse]])
def get_mental_health(
    student_id: int = Depends(get_current_student_id),
    dao: HealthDAO = Depends(get_health_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    records = dao.get_mental_records(student_id, days=30)
    result = [MentalHealthResponse(
        id=r.get("id"),
        student_id=r.get("student_id", student_id),
        record_date=r.get("record_date"),
        mood_score=r.get("mood_score"),
        stress_level=r.get("stress_level"),
        anxiety_level=r.get("anxiety_level"),
        notes=r.get("notes"),
    ) for r in records]
    return ApiResponse(data=result)


@router.post("/mental-health", response_model=ApiResponse[MentalHealthResponse])
def create_mental_health(
    record_in: MentalHealthCreate,
    student_id: int = Depends(get_current_student_id),
    dao: HealthDAO = Depends(get_health_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    db: DatabaseManager = Depends(get_db),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    record = MentalHealthRecord(
        student_id=student_id,
        record_date=record_in.record_date,
        mood_score=record_in.mood_score,
        stress_level=record_in.stress_level,
        anxiety_level=record_in.anxiety_level,
        notes=record_in.notes,
    )
    record_id = dao.save_mental_record(record)
    records = dao.get_mental_records(student_id, days=30)
    created = next((r for r in records if r["id"] == record_id), None)
    if not created:
        raise HTTPException(status_code=500, detail="创建失败")
    twin = DigitalTwin(student_id, db)
    twin.save_assessment()
    return ApiResponse(
        data=MentalHealthResponse(
            id=created.get("id"),
            student_id=created.get("student_id", student_id),
            record_date=created.get("record_date"),
            mood_score=created.get("mood_score"),
            stress_level=created.get("stress_level"),
            anxiety_level=created.get("anxiety_level"),
            notes=created.get("notes"),
        ),
        message="创建成功"
    )


@router.delete("/mental-health/{record_id}", response_model=ApiResponse[dict])
def delete_mental_health(
    record_id: int,
    dao: HealthDAO = Depends(get_health_dao),
):
    success = dao.delete_mental(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(data={"id": record_id}, message="删除成功")


# ── 社交健康 ──────────────────────────────────────────────────────

@router.get("/social-health", response_model=ApiResponse[List[SocialHealthResponse]])
def get_social_health(
    student_id: int = Depends(get_current_student_id),
    dao: HealthDAO = Depends(get_health_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    records = dao.get_social_records(student_id, days=30)
    result = [SocialHealthResponse(
        id=r.get("id"),
        student_id=r.get("student_id", student_id),
        record_date=r.get("record_date"),
        activity_type=r.get("activity_type"),
        duration_minutes=r.get("duration_minutes", 0),
        interaction_count=r.get("interaction_count", 0),
    ) for r in records]
    return ApiResponse(data=result)


@router.post("/social-health", response_model=ApiResponse[SocialHealthResponse])
def create_social_health(
    record_in: SocialHealthCreate,
    student_id: int = Depends(get_current_student_id),
    dao: HealthDAO = Depends(get_health_dao),
    student_dao: StudentDAO = Depends(get_student_dao),
    db: DatabaseManager = Depends(get_db),
):
    student = student_dao.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    record = SocialHealthRecord(
        student_id=student_id,
        record_date=record_in.record_date,
        activity_type=record_in.activity_type,
        duration_minutes=record_in.duration_minutes,
        interaction_count=record_in.interaction_count,
    )
    record_id = dao.save_social_record(record)
    records = dao.get_social_records(student_id, days=30)
    created = next((r for r in records if r["id"] == record_id), None)
    if not created:
        raise HTTPException(status_code=500, detail="创建失败")
    twin = DigitalTwin(student_id, db)
    twin.save_assessment()
    return ApiResponse(
        data=SocialHealthResponse(
            id=created.get("id"),
            student_id=created.get("student_id", student_id),
            record_date=created.get("record_date"),
            activity_type=created.get("activity_type"),
            duration_minutes=created.get("duration_minutes", 0),
            interaction_count=created.get("interaction_count", 0),
        ),
        message="创建成功"
    )


@router.delete("/social-health/{record_id}", response_model=ApiResponse[dict])
def delete_social_health(
    record_id: int,
    dao: HealthDAO = Depends(get_health_dao),
):
    success = dao.delete_social(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiResponse(data={"id": record_id}, message="删除成功")
