"""学习计划 DAO."""
import json
from datetime import date
from data_layer.database import DatabaseManager


class StudyPlanDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, student_id: int, subject: str, goal_score: float,
               exam_date: date, plan_content: list[dict]) -> int:
        return self._db.execute_insert(
            "INSERT INTO study_plan (student_id, subject, goal_score, exam_date, plan_content) "
            "VALUES (%s, %s, %s, %s, %s)",
            (student_id, subject, goal_score, exam_date, json.dumps(plan_content, ensure_ascii=False)),
        )

    def _parse_plan_content(self, r: dict) -> dict:
        if isinstance(r.get("plan_content"), str):
            try:
                r["plan_content"] = json.loads(r["plan_content"])
            except json.JSONDecodeError:
                r["plan_content"] = []
        if not isinstance(r.get("plan_content"), list):
            r["plan_content"] = []
        return r

    def get_by_student(self, student_id: int) -> list[dict]:
        rows = self._db.execute_query(
            "SELECT * FROM study_plan WHERE student_id = %s ORDER BY created_at DESC",
            (student_id,),
        )
        return [self._parse_plan_content(r) for r in rows]

    def get_active(self, student_id: int) -> list[dict]:
        return [r for r in self.get_by_student(student_id) if r.get("status") == "active"]

    def update_progress(self, plan_id: int, progress: float) -> bool:
        return self._db.execute_update(
            "UPDATE study_plan SET progress = %s WHERE id = %s", (progress, plan_id),
        ) > 0

    def complete(self, plan_id: int) -> bool:
        return self._db.execute_update(
            "UPDATE study_plan SET status='completed', progress=100 WHERE id=%s",
            (plan_id,),
        ) > 0

    def delete(self, plan_id: int) -> bool:
        return self._db.execute_update(
            "DELETE FROM study_plan WHERE id = %s", (plan_id,),
        ) > 0

    def cancel(self, plan_id: int) -> bool:
        return self._db.execute_update(
            "UPDATE study_plan SET status='cancelled' WHERE id=%s", (plan_id,),
        ) > 0

    def delete_all_for_student(self, student_id: int) -> int:
        """Batch delete all plans for a student."""
        return self._db.execute_update(
            "DELETE FROM study_plan WHERE student_id = %s", (student_id,),
        )
