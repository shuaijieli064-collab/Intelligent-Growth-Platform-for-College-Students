"""
一键启动器：自动启动 MySQL + 初始化数据库 + 启动应用.

对方只需双击此文件，或在终端中执行：
    python 启动.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# ── MySQL 配置 ────────────────────────────────────────────────
MYSQL_PORT = 3306
MYSQL_DATADIR = Path(os.environ.get("MYSQL_DATADIR", Path.home() / "mysql_data"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "lsjhappy123..")
MYSQL_DATABASE = "student_growth_platform"


def find_mysqld() -> Path | None:
    """自动查找 mysqld.exe 路径."""
    # 1) 环境变量
    env_path = os.environ.get("MYSQL_HOME")
    if env_path:
        candidate = Path(env_path) / "bin" / "mysqld.exe"
        if candidate.exists():
            return candidate

    # 2) PATH 中查找
    import shutil
    found = shutil.which("mysqld")
    if found:
        return Path(found)

    # 3) 常见安装路径（按版本号搜索）
    common_roots = [
        Path("C:/Program Files/MySQL"),
        Path("C:/Program Files (x86)/MySQL"),
        Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "MySQL",
    ]
    for root in common_roots:
        if not root.exists():
            continue
        for child in sorted(root.iterdir(), reverse=True):  # 取最新版本
            candidate = child / "bin" / "mysqld.exe"
            if candidate.exists():
                return candidate

    return None


def is_mysql_running() -> bool:
    """检查 3306 端口是否在监听."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", MYSQL_PORT))
        s.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


def start_mysql(mysqld: Path) -> bool:
    """后台启动 MySQL，等待就绪（最多 30 秒）."""
    if is_mysql_running():
        print("  MySQL 已在运行 (端口 3306)")
        return True

    print(f"  启动 MySQL: {mysqld}")
    MYSQL_DATADIR.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.Popen(
            [
                str(mysqld),
                f"--datadir={MYSQL_DATADIR}",
                f"--port={MYSQL_PORT}",
                "--bind-address=127.0.0.1",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except FileNotFoundError:
        print(f"  错误: 找不到 mysqld.exe，请安装 MySQL 8.4")
        return False

    # 等待就绪（最多 30s）
    for i in range(30):
        time.sleep(1)
        if is_mysql_running():
            print(f"  MySQL 启动成功 ({i + 1}s)")
            return True
        if i % 5 == 0:
            print(f"  等待 MySQL 启动... ({i + 1}s)")

    print("  警告: MySQL 启动超时，尝试继续...")
    return True


def ensure_database() -> bool:
    """确保数据库和表存在，首次运行自动初始化."""
    import pymysql

    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset="utf8mb4",
        )
        cursor = conn.cursor()

        # 检查数据库是否存在
        cursor.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
            "WHERE SCHEMA_NAME = %s",
            (MYSQL_DATABASE,),
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            print("  数据库已就绪")
            return True

        # 数据库不存在 → 自动初始化
        print("  首次运行，自动初始化数据库...")
        cursor.close()
        conn.close()

        # 调用 init_database.py + generate_mock_data.py
        init_script = PROJECT_DIR / "init_database.py"
        mock_script = PROJECT_DIR / "generate_mock_data.py"

        if init_script.exists():
            result = subprocess.run(
                [sys.executable, str(init_script)],
                capture_output=True, text=True, cwd=str(PROJECT_DIR),
            )
            if result.returncode != 0:
                print(f"  数据库初始化失败:\n{result.stderr}")
                return False
            print(result.stdout.strip() or "  数据库表创建完成")

        if mock_script.exists():
            print("  生成演示数据...")
            result = subprocess.run(
                [sys.executable, str(mock_script)],
                capture_output=True, text=True, cwd=str(PROJECT_DIR),
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            if result.returncode != 0:
                print(f"  演示数据生成失败（可忽略）:\n{result.stderr[:200]}")
            else:
                print("  演示数据生成完成")

        return True

    except pymysql.Error as e:
        print(f"  数据库连接失败: {e}")
        return False


def main() -> int:
    print("=" * 50)
    print("  大学生智能成长平台 v2.0")
    print("  一键启动中...")
    print("=" * 50)

    # 1. 找 MySQL
    mysqld = find_mysqld()
    if mysqld is None:
        print()
        print("错误: 未找到 MySQL 安装！")
        print("请安装 MySQL 8.4 或设置环境变量 MYSQL_HOME")
        print("下载: https://dev.mysql.com/downloads/mysql/8.4.html")
        input("按回车退出...")
        return 1
    print(f"  MySQL: {mysqld}")

    # 2. 启动 MySQL
    print()
    if not start_mysql(mysqld):
        input("按回车退出...")
        return 1

    # 3. 确保数据库就绪
    print()
    if not ensure_database():
        print()
        print("数据库初始化失败，请检查：")
        print("  1. MySQL 是否正常运行")
        print("  2. 是否有权限创建数据库")
        input("按回车退出...")
        return 1

    # 4. 启动应用
    print()
    print("  启动应用...")
    print("=" * 50)

    # 设置环境变量避免重复初始化
    os.chdir(str(PROJECT_DIR))

    # 直接运行主程序
    main_file = PROJECT_DIR / "main.py"
    if not main_file.exists():
        print(f"错误: 找不到 main.py")
        input("按回车退出...")
        return 1

    result = subprocess.run([sys.executable, str(main_file)])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
