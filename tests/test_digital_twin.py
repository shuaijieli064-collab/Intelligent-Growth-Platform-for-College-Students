"""测试数字孪生模块."""
import sys
sys.path.insert(0, ".")

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from business_layer.digital_twin import DigitalTwin, RiskLevel


def _get_db() -> DatabaseManager:
    return DatabaseManager.get_instance()

def _get_first_student_id() -> int:
    rows = _get_db().execute_query("SELECT student_id FROM student ORDER BY student_id LIMIT 1")
    return rows[0]["student_id"] if rows else 1


def test_health_calculation() -> None:
    db = _get_db()
    sid = _get_first_student_id()
    twin = DigitalTwin(student_id=sid, db=db)
    result = twin.assess_overall()

    assert 0 <= result.academic <= 100, f"学术健康分数异常: {result.academic}"
    assert 0 <= result.physical <= 100, f"身体健康分数异常: {result.physical}"
    assert 0 <= result.mental <= 100, f"心理健康分数异常: {result.mental}"
    assert 0 <= result.social <= 100, f"社交健康分数异常: {result.social}"
    assert 0 <= result.overall <= 100, f"综合健康分数异常: {result.overall}"
    print(f"  ✓ 健康度计算: 综合={result.overall}, 学术={result.academic}, "
          f"身体={result.physical}, 心理={result.mental}, 社交={result.social}")


def test_risk_level() -> None:
    assert DigitalTwin.determine_risk(85) == RiskLevel.LOW
    assert DigitalTwin.determine_risk(70) == RiskLevel.MEDIUM
    assert DigitalTwin.determine_risk(50) == RiskLevel.HIGH
    assert DigitalTwin.determine_risk(30) == RiskLevel.CRITICAL
    print("  ✓ 风险等级判定正确")


def test_save_assessment() -> None:
    db = _get_db()
    sid = _get_first_student_id()
    twin = DigitalTwin(student_id=sid, db=db)
    assessment_id = twin.save_assessment()
    assert assessment_id > 0, "保存健康评估失败"
    print(f"  ✓ 保存健康评估 (id={assessment_id})")


def main() -> None:
    print("数字孪生模块测试:")
    test_risk_level()
    test_health_calculation()
    test_save_assessment()
    print("\n✅ 数字孪生模块测试通过")


if __name__ == "__main__":
    # 初始化数据库
    DatabaseManager(
        host=DB_CONFIG["host"], port=DB_CONFIG["port"],
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        database=DB_CONFIG["database"], charset=DB_CONFIG.get("charset", "utf8mb4"),
    )
    main()
