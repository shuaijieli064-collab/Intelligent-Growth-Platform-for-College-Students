"""测试数据层连接与基本 CRUD."""
import sys
sys.path.insert(0, ".")

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from data_layer.models import Student
from data_layer.dao.student_dao import StudentDAO


def test_connection() -> None:
    db = DatabaseManager(**{k: v for k, v in DB_CONFIG.items() if k != "charset"},
                         charset=DB_CONFIG.get("charset", "utf8mb4"))
    result = db.execute_query("SELECT 1 AS test")
    assert result[0]["test"] == 1, "数据库连接测试失败"
    print("  ✓ 数据库连接正常")


def test_student_crud() -> None:
    db = DatabaseManager.get_instance()
    dao = StudentDAO(db)

    # Create
    s = Student(student_no="TEST001", name="测试学生", gender="M",
                grade_level="大一", major="测试专业", enrollment_year=2024)
    sid = dao.create(s)
    assert sid > 0, "创建学生失败"
    print(f"  ✓ 创建学生 (id={sid})")

    # Read
    s2 = dao.get_by_id(sid)
    assert s2 is not None and s2.name == "测试学生", "查询学生失败"
    print("  ✓ 查询学生")

    # Update
    s2.name = "测试学生(已修改)"
    assert dao.update(s2), "更新学生失败"
    print("  ✓ 更新学生")

    # Verify
    s3 = dao.get_by_id(sid)
    assert s3.name == "测试学生(已修改)", "更新验证失败"

    # Delete
    assert dao.delete(sid), "删除学生失败"
    print("  ✓ 删除学生")


def main() -> None:
    print("数据层测试:")
    test_connection()
    test_student_crud()
    print("\n✅ 所有数据层测试通过")


if __name__ == "__main__":
    main()
