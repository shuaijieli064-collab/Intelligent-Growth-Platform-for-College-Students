"""AI教练对话日志数据访问对象."""
from data_layer.database import DatabaseManager


class CoachDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def save_message(self, student_id: int, session_id: str,
                     role: str, message: str, tokens_used: int = 0) -> int:
        sql = ("INSERT INTO ai_coach_log (student_id, session_id, role, message, tokens_used) "
               "VALUES (%s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING log_id"
        return self._db.execute_insert(
            sql,
            (student_id, session_id, role, message, tokens_used),
        )

    def get_session_history(self, student_id: int,
                            session_id: str) -> list[dict]:
        return self._db.execute_query(
            "SELECT * FROM ai_coach_log WHERE student_id = %s AND session_id = %s "
            "ORDER BY created_at ASC",
            (student_id, session_id),
        )

    def get_all_sessions(self, student_id: int) -> list[dict]:
        return self._db.execute_query(
            "SELECT session_id, COUNT(*) AS msg_count, MIN(created_at) AS started_at "
            "FROM ai_coach_log WHERE student_id = %s "
            "GROUP BY session_id ORDER BY started_at DESC",
            (student_id,),
        )
