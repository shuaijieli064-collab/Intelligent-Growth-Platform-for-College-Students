"""MySQL 数据库连接管理器（单例 + 线程本地连接）."""
import pymysql
from pymysql.cursors import DictCursor
from decimal import Decimal
import threading


def _convert_decimals(obj):
    """递归将 Decimal 转换为 float."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals(v) for v in obj]
    return obj


class DatabaseManager:
    _instance = None

    def __init__(self, host: str, port: int, user: str,
                 password: str, database: str, charset: str = "utf8mb4"):
        self._config = {
            "host": host, "port": port, "user": user,
            "password": password, "database": database, "charset": charset,
            "cursorclass": DictCursor, "autocommit": True,
        }
        self._local = threading.local()
        DatabaseManager._instance = self

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        if cls._instance is None:
            raise RuntimeError("DatabaseManager 尚未初始化，请先调用构造函数")
        return cls._instance

    def _get_conn(self) -> pymysql.Connection:
        """获取当前线程的连接，断开时自动重连."""
        conn = getattr(self._local, 'conn', None)
        if conn is None or not conn.open:
            conn = pymysql.connect(**self._config)
            self._local.conn = conn
        return conn

    def execute_query(self, sql: str, params: tuple = None) -> list[dict]:
        conn = self._get_conn()
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return _convert_decimals(cursor.fetchall())

    def execute_update(self, sql: str, params: tuple = None) -> int:
        conn = self._get_conn()
        with conn.cursor() as cursor:
            affected = cursor.execute(sql, params or ())
            conn.commit()
            return affected

    def execute_insert(self, sql: str, params: tuple = None) -> int:
        conn = self._get_conn()
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.lastrowid

    def close(self) -> None:
        conn = getattr(self._local, 'conn', None)
        if conn and conn.open:
            conn.close()
        self._local.conn = None


