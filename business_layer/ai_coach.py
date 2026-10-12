"""AI学习教练模块 - LLM 对话管理与上下文注入."""
import uuid
from typing import Optional

from config import reload_llm_config
from data_layer.database import DatabaseManager
from data_layer.dao.coach_dao import CoachDAO
from utils.llm_client import LLMClient


class AICoach:
    SYSTEM_PROMPT = (
        "你是一位专业的大学生成长教练。你的职责是：\n"
        "1. 根据学生的学习数据提供个性化学习建议\n"
        "2. 帮助学生制定学习计划\n"
        "3. 提供情绪疏导和心理支持\n"
        "4. 进行生涯规划指导\n"
        "请用温暖、鼓励的语气回复，每次回复控制在300字以内。"
    )

    def __init__(self, db: DatabaseManager, student_id: int,
                 api_key: str = None, api_url: str = None,
                 model_name: str = None) -> None:
        self._db = db
        self._dao = CoachDAO(db)
        self._student_id = student_id
        self._session_id = uuid.uuid4().hex[:12]
        self._history: list[dict] = []

        # Re-read config at construction time to pick up saved settings
        llm_cfg = reload_llm_config()
        self._client = LLMClient(
            api_key=api_key or llm_cfg["api_key"],
            api_url=api_url or llm_cfg["api_url"],
            model=model_name or llm_cfg["model"],
        )

    def _load_history_from_db(self) -> None:
        """Restore conversation context from DB when in-memory history is empty."""
        rows = self._dao.get_session_history(self._student_id, self._session_id)
        self._history = [
            {"role": r["role"], "content": r["message"]}
            for r in rows
            if r.get("role") in ("user", "assistant") and r.get("message")
        ]

    def chat(self, message: str) -> str:
        if not self._history:
            self._load_history_from_db()

        self._dao.save_message(
            self._student_id, self._session_id, "user", message,
        )

        self._history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}] + self._history

        try:
            result = self._client.chat_completion(messages)
            reply = result.get("content", "抱歉，我暂时无法回复，请稍后再试。")
            tokens = result.get("tokens_used", 0)
        except Exception:
            reply = "抱歉，AI服务暂时不可用，请稍后再试。"
            tokens = 0

        self._history.append({"role": "assistant", "content": reply})
        self._dao.save_message(
            self._student_id, self._session_id, "assistant", reply, tokens,
        )
        return reply

    def get_study_advice(self, health_data: dict, weak_kps: list[dict]) -> str:
        prompt = (
            f"以下是该学生的学习数据：\n"
            f"- 综合健康度：{health_data.get('overall', 'N/A')}/100\n"
            f"- 学业健康：{health_data.get('academic', 'N/A')}/100\n"
            f"- 风险等级：{health_data.get('risk_level', 'N/A')}\n"
            f"- 薄弱知识点：{[w['kp_name'] for w in weak_kps] if weak_kps else '无'}\n\n"
            f"请基于以上数据，给该学生3条具体的学习建议。"
        )
        return self.chat(prompt)

    def get_risk_advice(self, alerts: list) -> str:
        if not alerts:
            return self.chat("请给我一些保持良好学习状态的一般性建议。")
        alert_descriptions = "\n".join(
            f"- [{a.alert_type}] {a.alert_message}" for a in alerts[:5]
        )
        prompt = (
            f"该学生当前有以下风险告警：\n{alert_descriptions}\n\n"
            f"请针对以上告警，给出应对建议和鼓励。"
        )
        return self.chat(prompt)

    def clear_history(self) -> None:
        self._session_id = uuid.uuid4().hex[:12]
        self._history.clear()

    def get_history(self) -> list[dict]:
        return list(self._history)

    @property
    def session_id(self) -> str:
        return self._session_id
