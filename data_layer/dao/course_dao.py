"""课程与选课数据访问对象."""
from typing import Optional
import pandas as pd
from data_layer.database import DatabaseManager
from data_layer.models import Course


class CourseDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_by_id(self, course_id: int) -> Optional[Course]:
        rows = self._db.execute_query(
            "SELECT * FROM course WHERE course_id = %s", (course_id,)
        )
        return Course(**rows[0]) if rows else None

    def get_by_code(self, course_code: str) -> Optional[Course]:
        rows = self._db.execute_query(
            "SELECT * FROM course WHERE course_code = %s", (course_code,)
        )
        return Course(**rows[0]) if rows else None

    def get_by_name(self, course_name: str) -> Optional[Course]:
        rows = self._db.execute_query(
            "SELECT * FROM course WHERE course_name = %s ORDER BY course_id LIMIT 1",
            (course_name,),
        )
        return Course(**rows[0]) if rows else None

    def get_all(self) -> list[Course]:
        rows = self._db.execute_query("SELECT * FROM course ORDER BY course_id")
        return [Course(**r) for r in rows]

    def get_by_student(self, student_id: int) -> list[Course]:
        rows = self._db.execute_query(
            "SELECT c.* FROM course c JOIN student_course sc ON c.course_id = sc.course_id "
            "WHERE sc.student_id = %s", (student_id,)
        )
        return [Course(**r) for r in rows]

    def get_prerequisites(self, course_id: int) -> list[Course]:
        result = []
        rows = self._db.execute_query(
            "SELECT * FROM course WHERE course_id = %s", (course_id,)
        )
        if not rows:
            return result
        course = rows[0]
        if course["prerequisite_course_id"]:
            prereq = self.get_by_id(course["prerequisite_course_id"])
            if prereq:
                result.extend(self.get_prerequisites(prereq.course_id))
                result.append(prereq)
        return result

    def create(self, c: Course) -> int:
        sql = ("INSERT INTO course (course_code, course_name, credit, semester, is_compulsory, "
               "prerequisite_course_id, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING course_id"
        return self._db.execute_insert(
            sql,
            (c.course_code, c.course_name, c.credit, c.semester,
             c.is_compulsory, c.prerequisite_course_id, c.created_by),
        )

    def create_with_defaults(self, code: str, name: str, credit: float,
                             semester: str, is_compulsory: bool,
                             created_by: Optional[int] = None) -> int:
        sql = ("INSERT INTO course (course_code, course_name, credit, semester, is_compulsory, "
               "created_by) VALUES (%s, %s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING course_id"
        return self._db.execute_insert(
            sql,
            (code, name, credit, semester, is_compulsory, created_by),
        )

    def delete(self, course_id: int) -> bool:
        return self._db.execute_update(
            "DELETE FROM course WHERE course_id = %s", (course_id,),
        ) > 0


class StudentCourseDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def enroll(self, student_id: int, course_id: int) -> int:
        sql = "INSERT INTO student_course (student_id, course_id) VALUES (%s, %s)"
        if self._db._db_type == "postgres":
            sql += " RETURNING id"
        return self._db.execute_insert(
            sql,
            (student_id, course_id),
        )

    def unenroll(self, student_id: int, course_id: int) -> bool:
        """移除自己的选课记录（连带该课程的成绩行），不影响课程本身."""
        return self._db.execute_update(
            "DELETE FROM student_course WHERE student_id = %s AND course_id = %s",
            (student_id, course_id),
        ) > 0

    def update_scores(self, student_id: int, course_id: int,
                      usual: Optional[float] = None, midterm: Optional[float] = None,
                      final: Optional[float] = None) -> bool:
        sets = []
        params = []
        if usual is not None:
            sets.append("usual_score=%s"); params.append(usual)
        if midterm is not None:
            sets.append("midterm_score=%s"); params.append(midterm)
        if final is not None:
            sets.append("final_score=%s"); params.append(final)
        if not sets:
            return False
        params.extend([student_id, course_id])
        return self._db.execute_update(
            f"UPDATE student_course SET {', '.join(sets)} "
            "WHERE student_id=%s AND course_id=%s", tuple(params)
        ) > 0

    def update_predicted(self, student_id: int, course_id: int,
                         predicted: float) -> bool:
        return self._db.execute_update(
            "UPDATE student_course SET predicted_final=%s "
            "WHERE student_id=%s AND course_id=%s",
            (predicted, student_id, course_id),
        ) > 0

    def get_student_scores(self, student_id: int) -> list[dict]:
        return self._db.execute_query(
            "SELECT sc.*, c.course_name FROM student_course sc "
            "JOIN course c ON sc.course_id = c.course_id "
            "WHERE sc.student_id = %s", (student_id,)
        )

    def delete_score(self, sc_id: int) -> bool:
        """清空成绩分数（保留选课行，课程不从“我的课程”中消失）."""
        return self._db.execute_update(
            "UPDATE student_course SET usual_score=NULL, midterm_score=NULL, "
            "final_score=NULL, predicted_final=NULL WHERE id = %s", (sc_id,),
        ) > 0

    def get_training_data(self, course_id: Optional[int] = None) -> pd.DataFrame:
        if course_id:
            rows = self._db.execute_query(
                "SELECT usual_score, midterm_score, final_score FROM student_course "
                "WHERE usual_score IS NOT NULL AND midterm_score IS NOT NULL "
                "AND final_score IS NOT NULL AND course_id = %s", (course_id,)
            )
        else:
            rows = self._db.execute_query(
                "SELECT usual_score, midterm_score, final_score FROM student_course "
                "WHERE usual_score IS NOT NULL AND midterm_score IS NOT NULL "
                "AND final_score IS NOT NULL"
            )
        return pd.DataFrame(rows) if rows else pd.DataFrame(
            columns=["usual_score", "midterm_score", "final_score"]
        )
