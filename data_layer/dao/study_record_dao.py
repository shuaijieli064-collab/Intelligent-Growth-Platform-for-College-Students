"""学习记录数据访问对象."""
from datetime import date, timedelta
from typing import Optional
from data_layer.database import DatabaseManager


class StudyRecordDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def add_record(self, student_id: int, study_date: date,
                   study_hours: float, course_id: Optional[int] = None,
                   task_completed: int = 0, focus_score: Optional[int] = None,
                   notes: Optional[str] = None) -> int:
        sql = ("INSERT INTO study_record (student_id, course_id, study_date, study_hours, "
               "task_completed, focus_score, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING record_id"
        return self._db.execute_insert(
            sql,
            (student_id, course_id, study_date, study_hours,
             task_completed, focus_score, notes),
        )

    def get_by_student(self, student_id: int, days: int = 30) -> list[dict]:
        cutoff = date.today() - timedelta(days=days)
        return self._db.execute_query(
            "SELECT * FROM study_record WHERE student_id = %s AND study_date >= %s "
            "ORDER BY study_date DESC", (student_id, cutoff)
        )

    def get_all_by_student(self, student_id: int) -> list[dict]:
        return self._db.execute_query(
            "SELECT * FROM study_record WHERE student_id = %s ORDER BY study_date DESC",
            (student_id,)
        )

    def get_weekly_hours(self, student_id: int) -> list[dict]:
        if self._db._db_type == "postgres":
            sql = ("SELECT to_char(study_date, 'IYYYIW') AS yw, SUM(study_hours) AS total_hours "
                   "FROM study_record WHERE student_id = %s "
                   "GROUP BY to_char(study_date, 'IYYYIW') ORDER BY yw")
        else:
            sql = ("SELECT YEARWEEK(study_date, 1) AS yw, SUM(study_hours) AS total_hours "
                   "FROM study_record WHERE student_id = %s "
                   "GROUP BY YEARWEEK(study_date, 1) ORDER BY yw")
        return self._db.execute_query(sql, (student_id,))

    def get_daily_focus_avg(self, student_id: int, days: int = 7) -> float:
        rows = self._db.execute_query(
            "SELECT AVG(focus_score) AS avg_focus FROM study_record "
            "WHERE student_id = %s AND study_date >= %s AND focus_score IS NOT NULL",
            (student_id, date.today() - timedelta(days=days))
        )
        return rows[0]["avg_focus"] if rows and rows[0]["avg_focus"] else 0.0

    def delete(self, record_id: int) -> bool:
        return self._db.execute_update(
            "DELETE FROM study_record WHERE record_id = %s", (record_id,),
        ) > 0

    def delete_all_by_student(self, student_id: int) -> bool:
        return self._db.execute_update(
            "DELETE FROM study_record WHERE student_id = %s", (student_id,),
        ) > 0

    def update(self, record_id: int, study_hours: Optional[float] = None,
               focus_score: Optional[int] = None, task_completed: Optional[int] = None,
               notes: Optional[str] = None) -> bool:
        sets = []; params = []
        if study_hours is not None: sets.append("study_hours=%s"); params.append(study_hours)
        if focus_score is not None: sets.append("focus_score=%s"); params.append(focus_score)
        if task_completed is not None: sets.append("task_completed=%s"); params.append(task_completed)
        if notes is not None: sets.append("notes=%s"); params.append(notes)
        if not sets: return False
        params.append(record_id)
        return self._db.execute_update(
            f"UPDATE study_record SET {', '.join(sets)} WHERE record_id=%s", tuple(params),
        ) > 0
