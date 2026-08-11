"""资源推荐 DAO."""
from typing import Optional

from data_layer.database import DatabaseManager


class ResourceDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, student_id: int, kp_id: Optional[int], resource_type: str,
               title: str, url: str = "", reason: str = "") -> int:
        sql = ("INSERT INTO resource_recommendation (student_id, kp_id, resource_type, "
               "title, url, reason) VALUES (%s, %s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING id"
        return self._db.execute_insert(
            sql,
            (student_id, kp_id, resource_type, title, url, reason),
        )

    def get_by_student(self, student_id: int) -> list[dict]:
        return self._db.execute_query(
            "SELECT r.*, kp.kp_name FROM resource_recommendation r "
            "LEFT JOIN knowledge_point kp ON r.kp_id = kp.kp_id "
            "WHERE r.student_id = %s ORDER BY r.created_at DESC",
            (student_id,),
        )

    def get_uncompleted(self, student_id: int, course_id: Optional[int] = None) -> list[dict]:
        if course_id:
            return self._db.execute_query(
                "SELECT r.*, kp.kp_name FROM resource_recommendation r "
                "LEFT JOIN knowledge_point kp ON r.kp_id = kp.kp_id "
                "WHERE r.student_id = %s AND r.is_completed = FALSE "
                "AND (r.kp_id IS NULL OR kp.course_id = %s) "
                "ORDER BY r.created_at DESC",
                (student_id, course_id),
            )
        return self._db.execute_query(
            "SELECT r.*, kp.kp_name FROM resource_recommendation r "
            "LEFT JOIN knowledge_point kp ON r.kp_id = kp.kp_id "
            "WHERE r.student_id = %s AND r.is_completed = FALSE ORDER BY r.created_at DESC",
            (student_id,),
        )

    def mark_completed(self, rec_id: int) -> bool:
        return self._db.execute_update(
            "UPDATE resource_recommendation SET is_completed=TRUE WHERE id=%s",
            (rec_id,),
        ) > 0

    def delete(self, rec_id: int) -> bool:
        return self._db.execute_update(
            "DELETE FROM resource_recommendation WHERE id = %s", (rec_id,),
        ) > 0

    def delete_all_for_student(self, student_id: int) -> int:
        """Batch delete all recommendations for a student."""
        return self._db.execute_update(
            "DELETE FROM resource_recommendation WHERE student_id = %s", (student_id,),
        )
