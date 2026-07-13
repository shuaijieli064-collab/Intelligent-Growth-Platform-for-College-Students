"""数据库初始化脚本 — 自动执行所有 SQL 文件，无需 MySQL CLI."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pymysql

# ── 配置 ──────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "lsjhappy123..",
    "charset": "utf8mb4",
}

SQL_DIR = Path(__file__).resolve().parent / "sql"
SQL_FILES = ["schema.sql", "v2_extend.sql", "v3_health_extend.sql"]


def _parse_sql(content: str) -> list[str]:
    """分割 SQL 文件为独立语句，跳过注释和空行."""
    # 去掉行注释和块注释
    content = re.sub(r"--[^\n]*", "", content)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    statements = []
    for stmt in content.split(";"):
        stmt = stmt.strip()
        if stmt and not stmt.upper().startswith("USE "):
            statements.append(stmt)
    return statements


def init_database() -> int:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 先创建数据库
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS student_growth_platform "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.execute("USE student_growth_platform")
    conn.commit()

    total_ok = 0
    total_fail = 0

    for filename in SQL_FILES:
        sql_path = SQL_DIR / filename
        if not sql_path.exists():
            print(f"  [跳过] {filename} — 文件不存在")
            continue

        print(f"  [执行] {filename} ...", end=" ")
        content = sql_path.read_text(encoding="utf-8")
        statements = _parse_sql(content)
        ok, fail = 0, 0

        for stmt in statements:
            try:
                cursor.execute(stmt)
                ok += 1
            except pymysql.Error as e:
                fail += 1
                err_msg = str(e).split("\n")[0]
                print(f"\n    警告: {err_msg[:80]}")

        conn.commit()
        print(f"OK ({ok} 条成功" + (f", {fail} 条跳过)" if fail else ")"))
        total_ok += ok
        total_fail += fail

    cursor.close()
    conn.close()

    if total_fail > 0:
        print(f"\n完成: {total_ok} 条成功, {total_fail} 条跳过（可能是表已存在，可忽略）")
    else:
        print(f"\n全部完成: {total_ok} 条语句执行成功")
    return 0


def main() -> int:
    print("=" * 60)
    print("  大学生智能成长平台 — 数据库初始化")
    print("=" * 60)
    print(f"  主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print()

    try:
        return init_database()
    except pymysql.Error as e:
        print(f"\n数据库连接失败: {e}")
        print("\n请确认：")
        print("  1. MySQL 服务已启动（端口 3306）")
        print("  2. 用户名/密码正确")
        print("  3. 可手动执行: mysqld --initialize-insecure 初始化数据目录")
        return 1


if __name__ == "__main__":
    sys.exit(main())
