"""用户数据访问对象."""
from typing import Optional
from data_layer.database import DatabaseManager
from data_layer.models import User


class UserDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create_user(self, username: str, email: str,
                    password_hash: str, student_id: Optional[int] = None) -> int:
        return self._db.execute_insert(
            "INSERT INTO user (username, email, password_hash, student_id) "
            "VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, student_id),
        )

    def get_by_username(self, username: str) -> Optional[User]:
        rows = self._db.execute_query(
            "SELECT * FROM user WHERE username = %s", (username,)
        )
        return User(**rows[0]) if rows else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        rows = self._db.execute_query(
            "SELECT * FROM user WHERE user_id = %s", (user_id,)
        )
        return User(**rows[0]) if rows else None

    def get_by_student_id(self, student_id: int) -> Optional[User]:
        rows = self._db.execute_query(
            "SELECT * FROM user WHERE student_id = %s", (student_id,)
        )
        return User(**rows[0]) if rows else None

    def update_student_id(self, user_id: int, student_id: Optional[int]) -> bool:
        return self._db.execute_update(
            "UPDATE user SET student_id=%s WHERE user_id=%s",
            (student_id, user_id),
        ) > 0
