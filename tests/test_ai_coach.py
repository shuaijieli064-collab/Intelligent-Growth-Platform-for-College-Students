"""测试AI学习教练模块（不实际调用API）."""
import sys
sys.path.insert(0, ".")

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from business_layer.ai_coach import AICoach


def _get_db() -> DatabaseManager:
    return DatabaseManager.get_instance()

def _get_first_student_id() -> int:
    rows = _get_db().execute_query("SELECT student_id FROM student ORDER BY student_id LIMIT 1")
    return rows[0]["student_id"] if rows else 1


def test_coach_init() -> None:
    db = _get_db()
    coach = AICoach(db, student_id=_get_first_student_id())
    assert coach.session_id, "会话ID为空"
    assert len(coach.get_history()) == 0, "历史应为空"
    print(f"  ✓ AI教练初始化 (session={coach.session_id})")


def test_clear_history() -> None:
    db = _get_db()
    coach = AICoach(db, student_id=_get_first_student_id())
    old_session = coach.session_id
    coach.clear_history()
    assert coach.session_id != old_session, "清空后会话ID应更新"
    print("  ✓ 清空历史")


def test_system_prompt() -> None:
    db = _get_db()
    coach = AICoach(db, student_id=_get_first_student_id())
    assert "大学生成长教练" in coach.SYSTEM_PROMPT
    print("  ✓ 系统提示词正确")


def main() -> None:
    print("AI学习教练模块测试:")
    test_coach_init()
    test_clear_history()
    test_system_prompt()
    print("\n✅ AI学习教练模块测试通过")
    print("\n💡 注: 实际API调用测试需要有效的LLM API Key")
    print("   请在 config.py 中配置 LLM_CONFIG 后运行应用测试")


if __name__ == "__main__":
    DatabaseManager(
        host=DB_CONFIG["host"], port=DB_CONFIG["port"],
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        database=DB_CONFIG["database"], charset=DB_CONFIG.get("charset", "utf8mb4"),
    )
    main()
