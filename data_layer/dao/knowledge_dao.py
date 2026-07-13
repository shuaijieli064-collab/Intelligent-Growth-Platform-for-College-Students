"""知识点与掌握度数据访问对象."""
from datetime import date
from typing import Optional
from data_layer.database import DatabaseManager
from data_layer.models import KnowledgePoint, KnowledgeMastery


class KnowledgeDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_knowledge_points(self, course_id: int) -> list[dict]:
        return self._db.execute_query(
            "SELECT * FROM knowledge_point WHERE course_id = %s ORDER BY kp_id",
            (course_id,)
        )

    def get_all_knowledge_points(self) -> list[dict]:
        return self._db.execute_query(
            "SELECT kp.*, c.course_name FROM knowledge_point kp "
            "JOIN course c ON kp.course_id = c.course_id ORDER BY kp.course_id, kp.kp_id"
        )

    def get_edges(self, course_id: int) -> list[tuple]:
        rows = self._db.execute_query(
            "SELECT kp_id, parent_kp_id FROM knowledge_point "
            "WHERE course_id = %s AND parent_kp_id IS NOT NULL", (course_id,)
        )
        return [(r["parent_kp_id"], r["kp_id"]) for r in rows]

    def get_mastery(self, student_id: int) -> list[dict]:
        return self._db.execute_query(
            "SELECT * FROM knowledge_mastery WHERE student_id = %s", (student_id,)
        )

    def get_mastery_for_course(self, student_id: int, course_id: int) -> list[dict]:
        return self._db.execute_query(
            "SELECT km.* FROM knowledge_mastery km "
            "JOIN knowledge_point kp ON km.kp_id = kp.kp_id "
            "WHERE km.student_id = %s AND kp.course_id = %s",
            (student_id, course_id),
        )

    def update_mastery(self, student_id: int, kp_id: int,
                       mastery_level: float) -> bool:
        existing = self._db.execute_query(
            "SELECT mastery_id FROM knowledge_mastery "
            "WHERE student_id = %s AND kp_id = %s", (student_id, kp_id)
        )
        if existing:
            return self._db.execute_update(
                "UPDATE knowledge_mastery SET mastery_level=%s, last_assessed=%s "
                "WHERE student_id=%s AND kp_id=%s",
                (mastery_level, date.today(), student_id, kp_id),
            ) > 0
        else:
            return self._db.execute_insert(
                "INSERT INTO knowledge_mastery (student_id, kp_id, mastery_level, last_assessed) "
                "VALUES (%s, %s, %s, %s)",
                (student_id, kp_id, mastery_level, date.today()),
            ) > 0

    def create_knowledge_point(self, kp: KnowledgePoint) -> int:
        return self._db.execute_insert(
            "INSERT INTO knowledge_point (kp_name, course_id, parent_kp_id, difficulty, weight) "
            "VALUES (%s, %s, %s, %s, %s)",
            (kp.kp_name, kp.course_id, kp.parent_kp_id, kp.difficulty, kp.weight),
        )

    def get_kp_by_id(self, kp_id: int) -> Optional[dict]:
        rows = self._db.execute_query(
            "SELECT * FROM knowledge_point WHERE kp_id = %s",
            (kp_id,),
        )
        return rows[0] if rows else None

    def delete_knowledge_point(self, kp_id: int) -> bool:
        self._db.execute_update(
            "UPDATE knowledge_point SET parent_kp_id = NULL WHERE parent_kp_id = %s",
            (kp_id,),
        )
        self._db.execute_update(
            "DELETE FROM knowledge_mastery WHERE kp_id = %s",
            (kp_id,),
        )
        return self._db.execute_update(
            "DELETE FROM knowledge_point WHERE kp_id = %s",
            (kp_id,),
        ) > 0

    def update_parent_kp(self, kp_id: int, parent_kp_id: int) -> bool:
        return self._db.execute_update(
            "UPDATE knowledge_point SET parent_kp_id = %s WHERE kp_id = %s",
            (parent_kp_id, kp_id),
        ) > 0

    def remove_parent_kp(self, kp_id: int) -> bool:
        return self._db.execute_update(
            "UPDATE knowledge_point SET parent_kp_id = NULL WHERE kp_id = %s",
            (kp_id,),
        ) > 0
