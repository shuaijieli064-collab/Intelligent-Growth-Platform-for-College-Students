"""测试风险预警模块."""
import sys
sys.path.insert(0, ".")

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from business_layer.risk_warning import RiskWarningSystem, Rule


def _get_db() -> DatabaseManager:
    return DatabaseManager.get_instance()

def _get_first_student_id() -> int:
    rows = _get_db().execute_query("SELECT student_id FROM student ORDER BY student_id LIMIT 1")
    return rows[0]["student_id"] if rows else 1


def test_evaluate() -> None:
    db = _get_db()
    rws = RiskWarningSystem(db)
    sid = _get_first_student_id()
    alerts = rws.evaluate(student_id=sid)
    print(f"  ✓ 风险评估: 触发 {len(alerts)} 条规则")
    for a in alerts:
        print(f"    - [{a.alert_type}] {a.alert_message} (规则: {a.rule_triggered})")


def test_custom_rule() -> None:
    db = _get_db()
    rws = RiskWarningSystem(db)
    initial_count = len(rws._rules)

    rws.add_rule(Rule(
        name="TEST_RULE",
        alert_type="综合",
        risk_level="LOW",
        condition=lambda sid: True,
        message_template="测试规则 - 始终触发",
    ))
    assert len(rws._rules) == initial_count + 1, "添加规则失败"
    print("  ✓ 自定义规则添加成功")


def test_save_alerts() -> None:
    db = _get_db()
    rws = RiskWarningSystem(db)
    sid = _get_first_student_id()
    alerts = rws.evaluate_and_save(student_id=sid)
    print(f"  ✓ 评估并保存告警: {len(alerts)} 条")


def main() -> None:
    print("风险预警模块测试:")
    test_custom_rule()
    test_evaluate()
    test_save_alerts()
    print("\n✅ 风险预警模块测试通过")


if __name__ == "__main__":
    DatabaseManager(
        host=DB_CONFIG["host"], port=DB_CONFIG["port"],
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        database=DB_CONFIG["database"], charset=DB_CONFIG.get("charset", "utf8mb4"),
    )
    main()
