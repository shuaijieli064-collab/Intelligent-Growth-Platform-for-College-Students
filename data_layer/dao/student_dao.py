"""学生数据访问对象."""
from typing import Optional
from data_layer.database import DatabaseManager
from data_layer.models import Student


class StudentDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_by_id(self, student_id: int) -> Optional[Student]:
        rows = self._db.execute_query(
            "SELECT * FROM student WHERE student_id = %s", (student_id,)
        )
        return Student(**rows[0]) if rows else None

    def get_by_student_no(self, student_no: str) -> Optional[Student]:
        rows = self._db.execute_query(
            "SELECT * FROM student WHERE student_no = %s", (student_no,)
        )
        return Student(**rows[0]) if rows else None

    def get_all(self) -> list[Student]:
        rows = self._db.execute_query("SELECT * FROM student ORDER BY student_id")
        return [Student(**r) for r in rows]

    def create(self, s: Student) -> int:
        return self._db.execute_insert(
            "INSERT INTO student (student_no, name, gender, grade_level, major, enrollment_year) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (s.student_no, s.name, s.gender, s.grade_level, s.major, s.enrollment_year),
        )

    def update(self, s: Student) -> bool:
        return self._db.execute_update(
            "UPDATE student SET student_no=%s, name=%s, gender=%s, grade_level=%s, major=%s, enrollment_year=%s "
            "WHERE student_id=%s",
            (s.student_no, s.name, s.gender, s.grade_level, s.major, s.enrollment_year, s.student_id),
        ) > 0

    def delete(self, student_id: int) -> bool:
        return self._db.execute_update(
            "DELETE FROM student WHERE student_id = %s", (student_id,)
        ) > 0
