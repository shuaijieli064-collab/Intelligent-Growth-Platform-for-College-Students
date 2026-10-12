import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.ai_coach import (
    CoachSession,
    CoachMessage,
    ChatRequest,
    QuickActionRequest,
    NewSessionResponse,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_current_student_id
from data_layer.database import DatabaseManager
from data_layer.dao.coach_dao import CoachDAO
from business_layer.ai_coach import AICoach


router = APIRouter(prefix="/api/ai-coach", tags=["ai-coach"])

# 限制缓存规模，避免无界增长造成内存耗尽
_MAX_CACHE_ENTRIES = 64
_coach_cache: dict[str, AICoach] = {}


def _cache_put(key: str, coach: AICoach) -> None:
    if key in _coach_cache:
        _coach_cache.pop(key)
    elif len(_coach_cache) >= _MAX_CACHE_ENTRIES:
        _coach_cache.pop(next(iter(_coach_cache)))
    _coach_cache[key] = coach


def _get_coach_key(student_id: int, session_id: str) -> str:
    return f"{student_id}_{session_id}"


@router.get("/sessions", response_model=ApiResponse[list[CoachSession]])
def get_sessions(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    dao = CoachDAO(db)
    sessions = dao.get_all_sessions(student_id)
    return ApiResponse(
        data=[
            CoachSession(
                session_id=s["session_id"],
                msg_count=s["msg_count"],
                started_at=s["started_at"],
            )
            for s in sessions
        ]
    )


@router.get("/messages/{session_id}", response_model=ApiResponse[list[CoachMessage]])
def get_messages(
    session_id: str,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    dao = CoachDAO(db)
    messages = dao.get_session_history(student_id, session_id)
    return ApiResponse(
        data=[
            CoachMessage(
                log_id=m.get("log_id"),
                session_id=m.get("session_id", session_id),
                role=m["role"],
                message=m["message"],
                tokens_used=m.get("tokens_used", 0),
                created_at=m.get("created_at"),
            )
            for m in messages
        ]
    )


@router.post("/chat", response_model=ApiResponse[CoachMessage])
def chat(
    req: ChatRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    session_id = req.session_id or uuid.uuid4().hex[:12]
    key = _get_coach_key(student_id, session_id)

    coach = _coach_cache.get(key)
    if coach is None:
        coach = AICoach(db, student_id)
        coach._session_id = session_id
        _cache_put(key, coach)

    reply = coach.chat(req.message)

    return ApiResponse(
        data=CoachMessage(
            session_id=session_id,
            role="assistant",
            message=reply,
        ),
        message="发送成功",
    )


@router.post("/quick-action", response_model=ApiResponse[CoachMessage])
def quick_action(
    req: QuickActionRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    # 复用当前会话（不传则新建），避免静默丢弃既有对话
    session_id = req.session_id or uuid.uuid4().hex[:12]
    key = _get_coach_key(student_id, session_id)
    coach = _coach_cache.get(key)
    if coach is None:
        coach = AICoach(db, student_id)
        coach._session_id = session_id

    reply = ""
    action_type = req.action_type

    if action_type == "study_advice":
        from business_layer.digital_twin import DigitalTwin
        from business_layer.knowledge_graph import KnowledgeGraph
        from data_layer.dao.course_dao import StudentCourseDAO

        twin = DigitalTwin(student_id, db)
        health = twin.assess_overall()

        sc_dao = StudentCourseDAO(db)
        courses = sc_dao.get_student_scores(student_id)
        weak_kps = []
        if courses:
            kg = KnowledgeGraph(db)
            kg.build_graph(courses[0]["course_id"], student_id)
            weak_kps = kg.get_weak_nodes(student_id)

        reply = coach.get_study_advice(
            {
                "overall": health.overall,
                "academic": health.academic,
                "risk_level": health.risk_level.value,
            },
            weak_kps,
        )

    elif action_type == "emotional_support":
        reply = coach.chat("我最近学习压力有点大，心情不太好，能给我一些情绪疏导和鼓励吗？")

    elif action_type == "career_planning":
        reply = coach.chat("我是计算机专业的大学生，能给我一些职业规划方面的建议吗？")

    elif action_type == "grade_analysis":
        from data_layer.dao.course_dao import StudentCourseDAO

        sc_dao = StudentCourseDAO(db)
        scored = [
            s for s in sc_dao.get_student_scores(student_id)
            if s.get("usual_score") is not None
            or s.get("midterm_score") is not None
            or s.get("final_score") is not None
        ]
        if scored:
            summary = [
                f"{s.get('course_name')}: 平时{s.get('usual_score')}/"
                f"期中{s.get('midterm_score')}/期末{s.get('final_score')}"
                for s in scored[:15]
            ]
            reply = coach.chat(
                "请根据我最近的成绩数据做一份成绩分析，指出薄弱科目并给出改进建议。"
                "成绩如下：" + "；".join(summary)
            )
        else:
            reply = coach.chat(
                "我还没有记录任何成绩，请给我一些开始记录成绩、规划本学期学习的建议。"
            )

    elif action_type == "daily_motivation":
        reply = coach.chat("请给我一段温暖的每日激励，鼓励我今天好好学习。")

    else:
        raise HTTPException(status_code=400, detail="不支持的操作类型")

    _cache_put(key, coach)

    return ApiResponse(
        data=CoachMessage(
            session_id=session_id,
            role="assistant",
            message=reply,
        ),
        message="操作成功",
    )


@router.post("/new-session", response_model=ApiResponse[NewSessionResponse])
def new_session(
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    session_id = uuid.uuid4().hex[:12]
    coach = AICoach(db, student_id)
    coach._session_id = session_id

    key = _get_coach_key(student_id, session_id)
    _cache_put(key, coach)

    return ApiResponse(
        data=NewSessionResponse(session_id=session_id),
        message="创建成功",
    )
