"""模拟数据生成脚本：5学生 x 8课程 x 30天学习记录."""
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_CONFIG
from data_layer.database import DatabaseManager

# ── 初始化数据库连接 ──────────────────────────────────────────
db = DatabaseManager(
    host=DB_CONFIG["host"], port=DB_CONFIG["port"],
    user=DB_CONFIG["user"], password=DB_CONFIG["password"],
    database=DB_CONFIG["database"], charset=DB_CONFIG.get("charset", "utf8mb4"),
)


def seed_students() -> list[int]:
    """插入5个学生，返回 student_id 列表."""
    students = [
        ("2022001", "张三", "M", "大二", "计算机科学与技术", 2022),
        ("2022002", "李四", "F", "大二", "计算机科学与技术", 2022),
        ("2022003", "王五", "M", "大二", "软件工程", 2022),
        ("2022004", "赵六", "F", "大一", "数据科学与大数据", 2023),
        ("2022005", "钱七", "M", "大三", "人工智能", 2021),
    ]
    ids = []
    for sno, name, gender, grade, major, year in students:
        sid = db.execute_insert(
            "INSERT INTO student (student_no, name, gender, grade_level, major, enrollment_year) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (sno, name, gender, grade, major, year),
        )
        ids.append(sid)
    print(f"  ✓ 插入 {len(ids)} 个学生")
    return ids


def seed_courses() -> list[int]:
    """插入8门课程（与 PRESET_COURSES 名称/代码对齐，保证命中同一份知识树）."""
    from business_layer.seed_data import PRESET_COURSES
    demo_codes = ["CS101", "CS102", "CS201", "CS301", "CS302", "MATH101", "MATH201", "ENG101"]
    code_to_data = {c["course_code"]: c for c in PRESET_COURSES}

    ids = {}
    for code in demo_codes:
        data = code_to_data[code]
        cid = db.execute_insert(
            "INSERT INTO course (course_code, course_name, credit, semester, is_compulsory, "
            "prerequisite_course_id) VALUES (%s, %s, %s, %s, %s, NULL)",
            (code, data["course_name"], data["credit"], data["semester"],
             data["is_compulsory"]),
        )
        ids[code] = cid

    # 先修关系沿用 PRESET_COURSES
    for code in demo_codes:
        prereq = code_to_data[code]["prerequisite_code"]
        if prereq and prereq in ids:
            db.execute_update(
                "UPDATE course SET prerequisite_course_id=%s WHERE course_id=%s",
                (ids[prereq], ids[code]),
            )
    print(f"  ✓ 插入 {len(ids)} 门课程（含先修关系）")
    return list(ids.values())


def seed_enrollments(student_ids: list[int], course_ids: list[int]) -> None:
    """为每个学生随机选课并生成成绩."""
    count = 0
    for sid in student_ids:
        # 每个学生选 5-8 门课
        selected = random.sample(course_ids, random.randint(5, len(course_ids)))
        for cid in selected:
            usual = round(random.uniform(55, 98), 1)
            midterm = round(random.uniform(50, 97), 1)
            # final 与 usual、midterm 有相关性的正态噪声
            final = round(usual * 0.3 + midterm * 0.4 + random.uniform(10, 30), 1)
            final = min(100, max(0, final))
            db.execute_insert(
                "INSERT INTO student_course (student_id, course_id, usual_score, "
                "midterm_score, final_score) VALUES (%s, %s, %s, %s, %s)",
                (sid, cid, usual, midterm, final),
            )
            count += 1
    print(f"  ✓ 插入 {count} 条选课记录")


def seed_study_records(student_ids: list[int], course_ids: list[int]) -> None:
    """为每个学生生成30天学习记录."""
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    count = 0

    for sid in student_ids:
        # 每个学生有不同的学习习惯
        avg_hours = random.uniform(2.0, 6.0)
        avg_focus = random.randint(40, 85)
        for day_offset in range(30):
            d = start_date + timedelta(days=day_offset)
            if random.random() < 0.85:  # 85%的天数有记录
                hours = round(max(0.5, random.gauss(avg_hours, 1.5)), 1)
                focus = min(100, max(10, int(random.gauss(avg_focus, 15))))
                cid = random.choice(course_ids) if random.random() < 0.6 else None
                db.execute_insert(
                    "INSERT INTO study_record (student_id, course_id, study_date, "
                    "study_hours, task_completed, focus_score) VALUES (%s, %s, %s, %s, %s, %s)",
                    (sid, cid, d, hours, random.randint(0, 5), focus),
                )
                count += 1
    print(f"  ✓ 插入 {count} 条学习记录")


def seed_knowledge_points(course_ids: list[int]) -> dict:
    """按 PRESET_COURSE_TREE 生成三层知识结构，返回 {course_id: 叶子kp_id列表}."""
    from business_layer.seed_data import COURSE_NAME_TO_CODE, ensure_course_hierarchy
    result = {}
    for cid in course_ids:
        rows = db.execute_query(
            "SELECT course_name FROM course WHERE course_id = %s", (cid,))
        course_name = rows[0]["course_name"] if rows else ""
        code = COURSE_NAME_TO_CODE.get(course_name)
        if code:
            ensure_course_hierarchy(db, cid, code, course_name)
        leaves = db.execute_query(
            "SELECT kp_id FROM knowledge_point WHERE course_id = %s "
            "AND node_type = 'kp' ORDER BY kp_id", (cid,))
        result[cid] = [r["kp_id"] for r in leaves]

    print(f"  ✓ 插入 {sum(len(v) for v in result.values())} 个知识点")
    return result


def seed_knowledge_mastery(student_ids: list[int],
                           kp_map: dict) -> None:
    """为每个学生生成知识点掌握度."""
    count = 0
    for sid in student_ids:
        for cid, kp_ids in kp_map.items():
            for kp_id in kp_ids:
                # 掌握度呈正态分布，均值取决于学生
                base = random.uniform(40, 95)
                mastery = round(max(5, min(100, random.gauss(base, 18))), 1)
                db.execute_insert(
                    "INSERT INTO knowledge_mastery (student_id, kp_id, mastery_level, "
                    "last_assessed) VALUES (%s, %s, %s, %s)",
                    (sid, kp_id, mastery, date.today() - timedelta(days=random.randint(0, 14))),
                )
                count += 1
    print(f"  ✓ 插入 {count} 条知识点掌握度记录")


def seed_physical_health(student_ids: list[int]) -> None:
    """为每个学生生成14天身体健康记录."""
    count = 0
    exercise_types = ["跑步", "球类", "健身", "瑜伽", "游泳", "骑行", "其他"]
    end_date = date.today()
    for sid in student_ids:
        for day_offset in range(14):
            d = end_date - timedelta(days=day_offset)
            if random.random() < 0.6:
                etype = random.choice(exercise_types)
                dur = random.randint(0, 90)
                sleep = round(random.uniform(5, 9), 1)
                steps = random.randint(1000, 15000)
                db.execute_insert(
                    "INSERT INTO physical_health_record (student_id, record_date, "
                    "exercise_type, exercise_duration, sleep_hours, steps) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (sid, d, etype, dur, sleep, steps),
                )
                count += 1
    print(f"  ✓ 插入 {count} 条身体健康记录")


def seed_mental_health(student_ids: list[int]) -> None:
    """为每个学生生成14天心理健康记录."""
    count = 0
    end_date = date.today()
    for sid in student_ids:
        base_mood = random.randint(5, 8)
        base_stress = random.randint(1, 3)
        base_anxiety = random.randint(1, 3)
        for day_offset in range(14):
            d = end_date - timedelta(days=day_offset)
            if random.random() < 0.55:
                mood = max(1, min(10, int(random.gauss(base_mood, 1.5))))
                stress = max(1, min(5, int(random.gauss(base_stress, 0.8))))
                anxiety = max(1, min(5, int(random.gauss(base_anxiety, 0.7))))
                notes = random.choice(["状态不错", "有点累", "充满干劲", "需要休息", None])
                db.execute_insert(
                    "INSERT INTO mental_health_record (student_id, record_date, "
                    "mood_score, stress_level, anxiety_level, notes) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (sid, d, mood, stress, anxiety, notes),
                )
                count += 1
    print(f"  ✓ 插入 {count} 条心理健康记录")


def seed_social_health(student_ids: list[int]) -> None:
    """为每个学生生成30天社交健康记录."""
    count = 0
    activity_types = ["社团活动", "朋友聚会", "团队项目", "志愿服务", "学术交流", "其他"]
    end_date = date.today()
    for sid in student_ids:
        for day_offset in range(30):
            d = end_date - timedelta(days=day_offset)
            if random.random() < 0.25:
                atype = random.choice(activity_types)
                dur = random.randint(30, 240)
                interactions = random.randint(1, 20)
                db.execute_insert(
                    "INSERT INTO social_health_record (student_id, record_date, "
                    "activity_type, duration_minutes, interaction_count) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (sid, d, atype, dur, interactions),
                )
                count += 1
    print(f"  ✓ 插入 {count} 条社交健康记录")


def seed_health_assessments(student_ids: list[int]) -> None:
    """为每个学生生成过去14天健康评估快照."""
    from business_layer.digital_twin import DigitalTwin, HealthAssessment
    from datetime import date, timedelta
    count = 0
    for sid in student_ids:
        dt = DigitalTwin(sid, db)
        for day_offset in range(14, -1, -1):
            d = date.today() - timedelta(days=day_offset)
            result = dt.assess_overall()
            try:
                db.execute_insert(
                    "INSERT INTO health_assessment (student_id, assessment_date, academic_score, "
                    "physical_score, mental_score, social_score, overall_health, risk_level) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (sid, d, result.academic, result.physical, result.mental,
                     result.social, result.overall, result.risk_level.value),
                )
                count += 1
            except Exception:
                pass  # skip if duplicate date
    print(f"  ✓ 插入 {count} 条健康评估快照（14天 x {len(student_ids)}人）")


def main() -> None:
    print("开始生成模拟数据...\n")

    print("[1/5] 学生数据")
    student_ids = seed_students()

    print("\n[2/5] 课程数据")
    course_ids = seed_courses()

    print("\n[3/5] 选课与成绩")
    seed_enrollments(student_ids, course_ids)

    print("\n[4/5] 学习记录 (30天)")
    seed_study_records(student_ids, course_ids)

    print("\n[5/5] 知识图谱与掌握度")
    kp_map = seed_knowledge_points(course_ids)
    seed_knowledge_mastery(student_ids, kp_map)

    print("\n[6/8] 身体健康记录 (14天)")
    seed_physical_health(student_ids)
    print("[7/8] 心理健康记录 (14天)")
    seed_mental_health(student_ids)
    print("[8/8] 社交健康记录 (30天)")
    seed_social_health(student_ids)

    print("\n[9/9] 健康评估快照（数字孪生）")
    seed_health_assessments(student_ids)

    print(f"\n{'='*50}")
    print("模拟数据生成完成！")
    print(f"  学生: {len(student_ids)} 人")
    print(f"  课程: {len(course_ids)} 门")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
