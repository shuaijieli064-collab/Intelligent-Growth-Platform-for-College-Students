"""数据库连接管理器（单例 + 线程本地连接）.

支持 MySQL (pymysql) 和 PostgreSQL (psycopg2) 双后端。
通过 db_type 参数切换，桌面版继续用 MySQL，Web 部署用 Postgres (Supabase)。
"""
import threading
from decimal import Decimal
from typing import Any


def _convert_decimals(obj: Any) -> Any:
    """递归将 Decimal 转换为 float."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_decimals(v) for v in obj]
    return obj


class DatabaseManager:
    """统一数据库管理器，支持 MySQL 和 PostgreSQL."""

    _instance: "DatabaseManager | None" = None

    def __init__(self, host: str, port: int, user: str,
                 password: str, database: str, charset: str = "utf8mb4",
                 db_type: str = "mysql"):
        """
        初始化数据库管理器.

        Args:
            db_type: "mysql" 或 "postgres"
            charset: MySQL 用 utf8mb4，Postgres 忽略此参数
        """
        self._db_type = db_type.lower()
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._charset = charset
        self._local = threading.local()
        DatabaseManager._instance = self

    @classmethod
    def get_instance(cls) -> "DatabaseManager":
        if cls._instance is None:
            raise RuntimeError("DatabaseManager 尚未初始化，请先调用构造函数")
        return cls._instance

    def _create_connection(self):
        """创建新的数据库连接."""
        if self._db_type == "postgres":
            import psycopg2
            from psycopg2.extras import RealDictCursor
            return psycopg2.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                dbname=self._database,
                cursor_factory=RealDictCursor,
            )
        else:
            import pymysql
            from pymysql.cursors import DictCursor
            return pymysql.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                database=self._database,
                charset=self._charset,
                cursorclass=DictCursor,
                autocommit=True,
            )

    def _get_conn(self):
        """获取当前线程的连接，断开时自动重连."""
        conn = getattr(self._local, 'conn', None)
        if conn is None:
            conn = self._create_connection()
            self._local.conn = conn
            return conn

        # 检查连接是否仍然有效
        try:
            if self._db_type == "postgres":
                # psycopg2: 检查 closed 状态
                if conn.closed:
                    conn = self._create_connection()
                    self._local.conn = conn
            else:
                # pymysql: 检查 open 状态
                if not conn.open:
                    conn = self._create_connection()
                    self._local.conn = conn
        except Exception:
            conn = self._create_connection()
            self._local.conn = conn

        return conn

    def execute_query(self, sql: str, params: tuple = None) -> list[dict]:
        """执行查询，返回字典列表."""
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                rows = cursor.fetchall()
                # psycopg2 RealDictCursor 返回 RealDictRow，转换为普通 dict
                if self._db_type == "postgres":
                    rows = [dict(r) for r in rows]
                return _convert_decimals(rows)
        except Exception:
            if self._db_type == "postgres":
                conn.rollback()
            raise

    def execute_update(self, sql: str, params: tuple = None) -> int:
        """执行更新/删除，返回受影响行数."""
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params or ())
                if self._db_type == "postgres":
                    conn.commit()
                return affected
        except Exception:
            if self._db_type == "postgres":
                conn.rollback()
            raise

    def execute_insert(self, sql: str, params: tuple = None) -> int:
        """
        执行插入，返回新记录主键 ID.

        注意：PostgreSQL 模式下，SQL 必须包含 RETURNING 子句。
        例如：INSERT INTO student (...) VALUES (...) RETURNING student_id
        """
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                if self._db_type == "postgres":
                    # PostgreSQL: 通过 RETURNING 子句获取 ID
                    row = cursor.fetchone()
                    conn.commit()
                    if row:
                        # RealDictRow 或 dict
                        if isinstance(row, dict):
                            # 返回第一个字段的值
                            return list(row.values())[0]
                        return row[0]
                    return 0
                else:
                    # MySQL: 通过 lastrowid 获取
                    conn.commit()
                    return cursor.lastrowid
        except Exception:
            if self._db_type == "postgres":
                conn.rollback()
            raise

    def close(self) -> None:
        """关闭当前线程的连接."""
        conn = getattr(self._local, 'conn', None)
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        self._local.conn = None
