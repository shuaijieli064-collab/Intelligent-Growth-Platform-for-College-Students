import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.grade_predict import (
    CourseWithScores,
    TrainRequest,
    TrainResponse,
    PredictRequest,
    PredictResponse,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_student_course_dao, get_current_student_id
from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import StudentCourseDAO
from business_layer.grade_predictor_v2 import GradePredictorV2


router = APIRouter(prefix="/api/grade-predict", tags=["grade-predict"])

_predictor_cache: dict[str, GradePredictorV2] = {}


def _get_predictor_key(student_id: int, course_id: int | None) -> str:
    return f"{student_id}_{course_id or 'all'}"


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
):
    predictor = GradePredictorV2(db)
    use_xgboost = req.algorithm == "xgboost"
    result = predictor.train(req.course_id, use_xgboost)

    key = _get_predictor_key(student_id, req.course_id)
    _predictor_cache[key] = predictor

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
):
    key = _get_predictor_key(student_id, req.course_id)
    predictor = _predictor_cache.get(key)

    if predictor is None:
        predictor = GradePredictorV2(db)
        predictor.train(req.course_id, False)
        _predictor_cache[key] = predictor

    try:
        result = predictor.predict(req.usual_score, req.midterm_score)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
