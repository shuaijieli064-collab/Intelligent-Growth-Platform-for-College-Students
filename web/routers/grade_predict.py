import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import logging

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.grade_predict import (
    CourseWithScores,
    TrainRequest,
    TrainResponse,
    PredictRequest,
    PredictResponse,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_student_course_dao, get_course_dao, get_current_student_id
from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from business_layer.grade_predictor_v2 import GradePredictorV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/grade-predict", tags=["grade-predict"])

# 限制缓存规模，避免无界增长造成内存耗尽
_MAX_CACHE_ENTRIES = 32
_predictor_cache: dict[str, GradePredictorV2] = {}


def _cache_put(key: str, predictor: GradePredictorV2) -> None:
    if key in _predictor_cache:
        _predictor_cache.pop(key)
    elif len(_predictor_cache) >= _MAX_CACHE_ENTRIES:
        _predictor_cache.pop(next(iter(_predictor_cache)))
    _predictor_cache[key] = predictor


def _get_predictor_key(student_id: int, course_id: int | None) -> str:
    return f"{student_id}_{course_id or 'all'}"


def _verify_course_access(
    course_id: int,
    student_id: int,
    course_dao: CourseDAO,
) -> None:
    enrolled = {c.course_id for c in course_dao.get_by_student(student_id)}
    if course_id not in enrolled:
        raise HTTPException(status_code=403, detail="无权访问该课程")


@router.get("/courses", response_model=ApiResponse[list[CourseWithScores]])
def get_courses_with_scores(
    student_id: int = Depends(get_current_student_id),
    sc_dao: StudentCourseDAO = Depends(get_student_course_dao),
):
    scores = sc_dao.get_student_scores(student_id)
    result = [
        CourseWithScores(
            course_id=s["course_id"],
            course_name=s.get("course_name", ""),
            usual_score=s.get("usual_score"),
            midterm_score=s.get("midterm_score"),
            final_score=s.get("final_score"),
        )
        for s in scores
    ]
    return ApiResponse(data=result)


@router.post("/train", response_model=ApiResponse[TrainResponse])
def train_model(
    req: TrainRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
    course_dao: CourseDAO = Depends(get_course_dao),
):
    if req.course_id is not None:
        _verify_course_access(req.course_id, student_id, course_dao)
    predictor = GradePredictorV2(db)
    use_xgboost = req.algorithm == "xgboost"
    result = predictor.train(req.course_id, use_xgboost)

    key = _get_predictor_key(student_id, req.course_id)
    _cache_put(key, predictor)

    if "error" in result:
        return ApiResponse(data=TrainResponse(error=result["error"]), message=result["error"])

    return ApiResponse(
        data=TrainResponse(
            samples=result["samples"],
            cv_mae=result["cv_mae"],
            residual_std=result["residual_std"],
            algorithm=result["algorithm"],
        ),
        message="训练成功",
    )


@router.post("/predict", response_model=ApiResponse[PredictResponse])
def predict_grade(
    req: PredictRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
    course_dao: CourseDAO = Depends(get_course_dao),
):
    if req.course_id is not None:
        _verify_course_access(req.course_id, student_id, course_dao)

    key = _get_predictor_key(student_id, req.course_id)
    predictor = _predictor_cache.get(key)

    if predictor is None:
        predictor = GradePredictorV2(db)
        predictor.train(req.course_id, False)
        _cache_put(key, predictor)

    try:
        result = predictor.predict(req.usual_score, req.midterm_score)
    except RuntimeError as e:
        logger.warning("grade predict failed: %s", e)
        raise HTTPException(status_code=400, detail="预测失败，请先完成成绩训练")

    return ApiResponse(
        data=PredictResponse(
            predicted_score=result["predicted"],
            confidence_interval_low=result["ci_lower"],
            confidence_interval_high=result["ci_upper"],
            pass_probability=result["pass_probability"],
            risk_level=result["risk"],
        ),
        message="预测成功",
    )
