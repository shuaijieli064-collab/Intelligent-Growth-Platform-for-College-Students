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
    """插入8门课程，含先修关系，返回 course_id 列表."""
    courses = [
        ("CS101", "程序设计基础", 4.0, "2025-春", True, None),
        ("CS102", "数据结构与算法", 4.0, "2025-春", True, None),
        ("CS201", "面向对象程序设计", 3.0, "2025-春", True, None),
        ("CS202", "数据库原理", 3.0, "2025-春", True, None),
        ("CS301", "人工智能导论", 3.0, "2025-春", False, None),
        ("MATH101", "高等数学(上)", 5.0, "2025-春", True, None),
        ("MATH102", "线性代数", 3.0, "2025-春", True, None),
        ("ENG101", "大学英语(4)", 2.0, "2025-春", True, None),
    ]
    # 设置先修关系（需要在插入后更新）
    prereq_map = {
        "CS102": "CS101",   # 数据结构 -> 程序设计基础
        "CS201": "CS101",   # OOP -> 程序设计基础
        "CS301": "MATH101", # AI -> 高等数学
    }

    ids = {}
    for code, name, credit, sem, comp, prereq in courses:
        cid = db.execute_insert(
            "INSERT INTO course (course_code, course_name, credit, semester, is_compulsory, "
            "prerequisite_course_id) VALUES (%s, %s, %s, %s, %s, NULL)",
            (code, name, credit, sem, comp),
        )
        ids[code] = cid

    # 更新先修关系
    for code, prereq_code in prereq_map.items():
        if code in ids and prereq_code in ids:
            db.execute_update(
                "UPDATE course SET prerequisite_course_id=%s WHERE course_id=%s",
                (ids[prereq_code], ids[code]),
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
    """为每门课生成知识点，返回 {course_id: [kp_id, ...]} 映射."""
    # 课程知识点定义
    course_kps = {
        0: [  # 程序设计基础 (index 0 = first course)
            ("变量与数据类型", None, 1), ("运算符与表达式", "变量与数据类型", 1),
            ("条件语句与分支", "运算符与表达式", 2), ("循环结构", "条件语句与分支", 2),
            ("函数定义与调用", "循环结构", 2), ("面向对象编程", "函数定义与调用", 3),
            ("文件读写", "面向对象编程", 3), ("程序调试与优化", "文件读写", 4),
        ],
        1: [  # 数据结构与算法
            ("线性表与链表", None, 1), ("栈与队列", "线性表与链表", 2),
            ("二叉树与遍历", "栈与队列", 3), ("图的存储与遍历", "二叉树与遍历", 3),
            ("排序算法", "图的存储与遍历", 3), ("查找算法", "排序算法", 2),
            ("动态规划入门", "查找算法", 4), ("贪心算法与回溯", "动态规划入门", 4),
        ],
        2: [  # 面向对象程序设计
            ("面向对象基本概念", None, 1), ("类与对象设计", "面向对象基本概念", 2),
            ("继承与多态", "类与对象设计", 2), ("接口与抽象类", "继承与多态", 3),
            ("设计模式入门", "接口与抽象类", 3), ("面向对象案例分析", "设计模式入门", 4),
        ],
        3: [  # 数据库原理
            ("数据库系统概念", None, 1), ("关系模型与代数", "数据库系统概念", 2),
            ("SQL查询语言", "关系模型与代数", 2), ("数据库设计范式", "SQL查询语言", 3),
            ("事务与并发控制", "数据库设计范式", 3), ("索引与查询优化", "事务与并发控制", 4),
        ],
        4: [  # 人工智能导论
            ("人工智能概述", None, 1), ("搜索算法", "人工智能概述", 2),
            ("机器学习基础", "搜索算法", 2), ("神经网络入门", "机器学习基础", 3),
            ("深度学习实践", "神经网络入门", 4), ("AI伦理与前沿", "深度学习实践", 3),
        ],
        5: [  # 高等数学(上)
            ("函数与极限", None, 1), ("导数与微分", "函数与极限", 2),
            ("微分中值定理", "导数与微分", 2), ("不定积分", "微分中值定理", 3),
            ("定积分及其应用", "不定积分", 3), ("常微分方程", "定积分及其应用", 4),
        ],
        6: [  # 线性代数
            ("行列式计算", None, 1), ("矩阵运算", "行列式计算", 2),
            ("向量空间", "矩阵运算", 2), ("线性方程组", "向量空间", 3),
            ("特征值与特征向量", "线性方程组", 3), ("二次型与应用", "特征值与特征向量", 4),
        ],
        7: [  # 大学英语(4)
            ("学术词汇积累", None, 1), ("阅读理解策略", "学术词汇积累", 1),
            ("英语写作技巧", "阅读理解策略", 2), ("听力与口语训练", "英语写作技巧", 2),
            ("翻译方法与实践", "听力与口语训练", 3), ("英语演讲与表达", "翻译方法与实践", 3),
        ],
    }

    result = {}
    all_kps = {}  # {kp_name: kp_id} for parent linking

    for idx, cid in enumerate(course_ids):
        if idx in course_kps:
            templates = course_kps[idx]
        else:
            # Fallback for any extra courses
            templates = [
                (f"{idx+1}-基本概念", None, 1), (f"{idx+1}-核心方法", f"{idx+1}-基本概念", 2),
                (f"{idx+1}-实践应用", f"{idx+1}-核心方法", 3), (f"{idx+1}-案例分析", f"{idx+1}-实践应用", 4),
            ]

        kp_ids = []
        for name, parent_name, diff in templates:
            parent_id = all_kps.get(parent_name) if parent_name else None
            kp_id = db.execute_insert(
                "INSERT INTO knowledge_point (kp_name, course_id, parent_kp_id, "
                "difficulty, weight) VALUES (%s, %s, %s, %s, %s)",
                (name, cid, parent_id, diff, round(random.uniform(0.8, 1.2), 2)),
            )
            all_kps[name] = kp_id
            kp_ids.append(kp_id)
        result[cid] = kp_ids

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
