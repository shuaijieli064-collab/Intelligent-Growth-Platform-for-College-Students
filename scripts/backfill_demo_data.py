"""一次性回填脚本：为存量账号补演示数据（幂等，已有数据的项跳过）.

用法：
    $env:PYTHONPATH="D:\A_Items\ChengZhang"; $env:PYTHONIOENCODING="utf-8"
    py -3.12 scripts/backfill_demo_data.py            # 回填所有学生
    py -3.12 scripts/backfill_demo_data.py 42         # 只回填 student_id=42
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from business_layer.seed_data import seed_default_courses, seed_demo_data


def main() -> None:
    db_kwargs = {k: v for k, v in DB_CONFIG.items() if k != "db_type"}
    db = DatabaseManager(**db_kwargs)

    if len(sys.argv) > 1:
        student_ids = [int(sys.argv[1])]
    else:
        rows = db.execute_query("SELECT student_id FROM student ORDER BY student_id")
        student_ids = [r["student_id"] for r in rows]

    print(f"回填 {len(student_ids)} 个学生 ...")
    for sid in student_ids:
        seed_default_courses(sid, db)
        seed_demo_data(sid, db)
        print(f"  student_id={sid} done")

    print("全部完成（幂等：已有数据的项自动跳过）")


if __name__ == "__main__":
    main()
