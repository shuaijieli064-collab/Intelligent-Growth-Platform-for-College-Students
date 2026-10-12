"""健康评估数据访问对象."""
from typing import Optional
from data_layer.database import DatabaseManager
from data_layer.models import (
    HealthAssessment, PhysicalHealthRecord, MentalHealthRecord, SocialHealthRecord,
)


class HealthDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # ── 健康评估 ──────────────────────────────────────────────

    def save_assessment(self, h: HealthAssessment) -> int:
        # 同一天只保留一条快照：先删旧记录，避免每次刷新页面都追加
        self._db.execute_update(
            "DELETE FROM health_assessment WHERE student_id = %s AND assessment_date = %s",
            (h.student_id, h.assessment_date),
        )
        sql = ("INSERT INTO health_assessment (student_id, assessment_date, academic_score, "
               "physical_score, mental_score, social_score, overall_health, risk_level) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING assessment_id"
        return self._db.execute_insert(
            sql,
            (h.student_id, h.assessment_date, h.academic_score, h.physical_score,
             h.mental_score, h.social_score, h.overall_health, h.risk_level),
        )

    def get_history(self, student_id: int) -> list[HealthAssessment]:
        rows = self._db.execute_query(
            "SELECT * FROM health_assessment WHERE student_id = %s "
            "ORDER BY assessment_date DESC", (student_id,)
        )
        return [HealthAssessment(**r) for r in rows]

    def get_latest(self, student_id: int) -> Optional[HealthAssessment]:
        rows = self._db.execute_query(
            "SELECT * FROM health_assessment WHERE student_id = %s "
            "ORDER BY assessment_date DESC LIMIT 1", (student_id,)
        )
        return HealthAssessment(**rows[0]) if rows else None

    # ── 身体健康 ──────────────────────────────────────────────

    def save_physical_record(self, r: PhysicalHealthRecord) -> int:
        sql = ("INSERT INTO physical_health_record (student_id, record_date, exercise_type, "
               "exercise_duration, sleep_hours, steps) VALUES (%s, %s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING id"
        return self._db.execute_insert(
            sql,
            (r.student_id, r.record_date, r.exercise_type,
             r.exercise_duration, r.sleep_hours, r.steps),
        )

    def delete_physical(self, record_id: int, student_id: Optional[int] = None) -> bool:
        if student_id is None:
            sql, params = "DELETE FROM physical_health_record WHERE id = %s", (record_id,)
        else:
            sql = "DELETE FROM physical_health_record WHERE id = %s AND student_id = %s"
            params = (record_id, student_id)
        return self._db.execute_update(sql, params) > 0

    def get_physical_records(self, student_id: int, days: int = 14) -> list[dict]:
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=days)
        return self._db.execute_query(
            "SELECT * FROM physical_health_record WHERE student_id = %s AND record_date >= %s "
            "ORDER BY record_date DESC", (student_id, cutoff),
        )

    def get_physical_by_id(self, record_id: int) -> Optional[dict]:
        rows = self._db.execute_query(
            "SELECT * FROM physical_health_record WHERE id = %s", (record_id,),
        )
        return rows[0] if rows else None

    # ── 心理健康 ──────────────────────────────────────────────

    def save_mental_record(self, r: MentalHealthRecord) -> int:
        sql = ("INSERT INTO mental_health_record (student_id, record_date, mood_score, "
               "stress_level, anxiety_level, notes) VALUES (%s, %s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING id"
        return self._db.execute_insert(
            sql,
            (r.student_id, r.record_date, r.mood_score,
             r.stress_level, r.anxiety_level, r.notes),
        )

    def delete_mental(self, record_id: int, student_id: Optional[int] = None) -> bool:
        if student_id is None:
            sql, params = "DELETE FROM mental_health_record WHERE id = %s", (record_id,)
        else:
            sql = "DELETE FROM mental_health_record WHERE id = %s AND student_id = %s"
            params = (record_id, student_id)
        return self._db.execute_update(sql, params) > 0

    def get_mental_records(self, student_id: int, days: int = 14) -> list[dict]:
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=days)
        return self._db.execute_query(
            "SELECT * FROM mental_health_record WHERE student_id = %s AND record_date >= %s "
            "ORDER BY record_date DESC", (student_id, cutoff),
        )

    def get_mental_by_id(self, record_id: int) -> Optional[dict]:
        rows = self._db.execute_query(
            "SELECT * FROM mental_health_record WHERE id = %s", (record_id,),
        )
        return rows[0] if rows else None

    # ── 社交健康 ──────────────────────────────────────────────

    def save_social_record(self, r: SocialHealthRecord) -> int:
        sql = ("INSERT INTO social_health_record (student_id, record_date, activity_type, "
               "duration_minutes, interaction_count) VALUES (%s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING id"
        return self._db.execute_insert(
            sql,
            (r.student_id, r.record_date, r.activity_type,
             r.duration_minutes, r.interaction_count),
        )

    def delete_social(self, record_id: int, student_id: Optional[int] = None) -> bool:
        if student_id is None:
            sql, params = "DELETE FROM social_health_record WHERE id = %s", (record_id,)
        else:
            sql = "DELETE FROM social_health_record WHERE id = %s AND student_id = %s"
            params = (record_id, student_id)
        return self._db.execute_update(sql, params) > 0

    def get_social_records(self, student_id: int, days: int = 30) -> list[dict]:
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=days)
        return self._db.execute_query(
            "SELECT * FROM social_health_record WHERE student_id = %s AND record_date >= %s "
            "ORDER BY record_date DESC", (student_id, cutoff),
        )

    def get_social_by_id(self, record_id: int) -> Optional[dict]:
        rows = self._db.execute_query(
            "SELECT * FROM social_health_record WHERE id = %s", (record_id,),
        )
        return rows[0] if rows else None
