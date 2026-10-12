import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.study_plan import (
    StudyPlan,
    StudyPlanTask,
    GeneratePlanRequest,
    UpdateTaskRequest,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_current_student_id
from data_layer.database import DatabaseManager
from data_layer.dao.study_plan_dao import StudyPlanDAO
from business_layer.study_plan_generator import StudyPlanGenerator


router = APIRouter(prefix="/api/study-plan", tags=["study-plan"])


@router.get("", response_model=ApiResponse[StudyPlan | None])
def get_study_plan(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    dao = StudyPlanDAO(db)
    plans = dao.get_active(student_id)

    if not plans:
        all_plans = dao.get_by_student(student_id)
        if all_plans:
            plan = all_plans[0]
            tasks = [StudyPlanTask(**t) for t in (plan.get("plan_content") or [])]
            return ApiResponse(data=StudyPlan(
                id=plan.get("id"),
                student_id=plan.get("student_id", student_id),
                subject=plan.get("subject", ""),
                goal_score=float(plan.get("goal_score", 0)),
                exam_date=plan.get("exam_date"),
                plan_content=tasks,
                status=plan.get("status", "active"),
                progress=float(plan.get("progress", 0)),
                created_at=plan.get("created_at"),
            ))
        return ApiResponse(data=None)

    plan = plans[0]
    tasks = [StudyPlanTask(**t) for t in (plan.get("plan_content") or [])]

    return ApiResponse(data=StudyPlan(
        id=plan.get("id"),
        student_id=plan.get("student_id", student_id),
        subject=plan.get("subject", ""),
        goal_score=float(plan.get("goal_score", 0)),
        exam_date=plan.get("exam_date"),
        plan_content=tasks,
        status=plan.get("status", "active"),
        progress=float(plan.get("progress", 0)),
        created_at=plan.get("created_at"),
    ))


@router.post("/generate", response_model=ApiResponse[StudyPlan])
def generate_plan(
    req: GeneratePlanRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    generator = StudyPlanGenerator(db, student_id)
    plan_id = generator.generate(
        req.subject, req.course_id, req.goal_score, req.exam_date,
        daily_minutes=req.daily_minutes,
    )

    dao = StudyPlanDAO(db)
    plans = dao.get_by_student(student_id)
    plan = next((p for p in plans if p.get("id") == plan_id), None)

    if not plan:
        raise HTTPException(status_code=500, detail="生成计划失败")

    tasks = [StudyPlanTask(**t) for t in (plan.get("plan_content") or [])]

    return ApiResponse(
        data=StudyPlan(
            id=plan.get("id"),
            student_id=plan.get("student_id", student_id),
            subject=plan.get("subject", ""),
            goal_score=float(plan.get("goal_score", 0)),
            exam_date=plan.get("exam_date"),
            plan_content=tasks,
            status=plan.get("status", "active"),
            progress=float(plan.get("progress", 0)),
            created_at=plan.get("created_at"),
        ),
        message="生成成功",
    )


@router.put("/task/{task_index}", response_model=ApiResponse[dict])
def update_task(
    task_index: int,
    req: UpdateTaskRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    dao = StudyPlanDAO(db)
    plans = dao.get_active(student_id)
    if not plans:
        all_plans = dao.get_by_student(student_id)
        if not all_plans:
            raise HTTPException(status_code=404, detail="没有学习计划")
        plans = [all_plans[0]]

    plan = plans[0]
    plan_id = plan.get("id")
    tasks = plan.get("plan_content") or []

    if task_index < 0 or task_index >= len(tasks):
        raise HTTPException(status_code=400, detail="任务索引无效")

    tasks[task_index]["done"] = req.done

    completed = sum(1 for t in tasks if t.get("done"))
    progress = round((completed / len(tasks)) * 100, 1) if tasks else 0

    import json
    db.execute_update(
        "UPDATE study_plan SET plan_content = %s, progress = %s WHERE id = %s",
        (json.dumps(tasks, ensure_ascii=False), progress, plan_id),
    )

    return ApiResponse(
        data={"task_index": task_index, "done": req.done, "progress": progress},
        message="更新成功",
    )


@router.post("/next-task", response_model=ApiResponse[dict])
def complete_next_task(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    dao = StudyPlanDAO(db)
    plans = dao.get_active(student_id)
    if not plans:
        all_plans = dao.get_by_student(student_id)
        if not all_plans:
            raise HTTPException(status_code=404, detail="没有学习计划")
        plans = [all_plans[0]]

    plan = plans[0]
    plan_id = plan.get("id")
    tasks = plan.get("plan_content") or []

    next_index = next((i for i, t in enumerate(tasks) if not t.get("done")), -1)

    if next_index == -1:
        completed = sum(1 for t in tasks if t.get("done"))
        progress = round((completed / len(tasks)) * 100, 1) if tasks else 0
        return ApiResponse(
            data={
                "completed_all": True,
                "task_index": -1,
                "progress": progress,
            },
            message="所有任务已完成",
        )

    tasks[next_index]["done"] = True

    completed = sum(1 for t in tasks if t.get("done"))
    progress = round((completed / len(tasks)) * 100, 1) if tasks else 0

    import json
    db.execute_update(
        "UPDATE study_plan SET plan_content = %s, progress = %s WHERE id = %s",
        (json.dumps(tasks, ensure_ascii=False), progress, plan_id),
    )

    return ApiResponse(
        data={
            "task_index": next_index,
            "task": tasks[next_index]["task"],
            "progress": progress,
            "completed_all": completed == len(tasks),
        },
        message="任务已完成",
    )
