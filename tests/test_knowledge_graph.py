"""测试知识图谱模块."""
import sys
sys.path.insert(0, ".")

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from business_layer.knowledge_graph import KnowledgeGraph


def _get_db() -> DatabaseManager:
    return DatabaseManager.get_instance()

def _get_first_student_id() -> int:
    rows = _get_db().execute_query("SELECT student_id FROM student ORDER BY student_id LIMIT 1")
    return rows[0]["student_id"] if rows else 1

def _get_first_course_id() -> int:
    rows = _get_db().execute_query("SELECT course_id FROM course ORDER BY course_id LIMIT 1")
    return rows[0]["course_id"] if rows else 1


def test_build_graph() -> None:
    db = _get_db()
    kg = KnowledgeGraph(db)
    course_id = _get_first_course_id()
    kg.build_graph(course_id=course_id)
    nodes, edges = kg.get_graph_data()

    print(f"  ✓ 构建图谱: {len(nodes)} 个节点, {len(edges)} 条边")
    assert len(nodes) > 0, "知识图谱节点为空"


def test_mark_mastery() -> None:
    db = _get_db()
    kg = KnowledgeGraph(db)
    course_id = _get_first_course_id()
    kg.build_graph(course_id=course_id)
    colors = kg.mark_mastery(student_id=_get_first_student_id())

    mastered = sum(1 for v in colors.values() if v == "mastered")
    weak = sum(1 for v in colors.values() if v == "weak")
    print(f"  ✓ 掌握度标记: 已掌握={mastered}, 薄弱={weak}")


def test_weak_nodes() -> None:
    db = _get_db()
    kg = KnowledgeGraph(db)
    course_id = _get_first_course_id()
    kg.build_graph(course_id=course_id)
    weak = kg.get_weak_nodes(student_id=_get_first_student_id())
    print(f"  ✓ 薄弱节点: {len(weak)} 个")
    if weak:
        print(f"    - {weak[0]['kp_name']}: {weak[0]['mastery']}%")

    order = kg.suggest_study_order(student_id=_get_first_student_id())
    print(f"  ✓ 建议学习顺序: {len(order)} 步")


def main() -> None:
    print("知识图谱模块测试:")
    test_build_graph()
    test_mark_mastery()
    test_weak_nodes()
    print("\n✅ 知识图谱模块测试通过")


if __name__ == "__main__":
    DatabaseManager(
        host=DB_CONFIG["host"], port=DB_CONFIG["port"],
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        database=DB_CONFIG["database"], charset=DB_CONFIG.get("charset", "utf8mb4"),
    )
    main()
