"""智能学习计划生成器."""
from datetime import date, timedelta
from data_layer.database import DatabaseManager
from data_layer.dao.study_plan_dao import StudyPlanDAO
from business_layer.knowledge_graph import KnowledgeGraph


class StudyPlanGenerator:
    def __init__(self, db: DatabaseManager, student_id: int) -> None:
        self._db = db
        self._student_id = student_id
        self._dao = StudyPlanDAO(db)
        self._kg = KnowledgeGraph(db)

    def generate(self, subject: str, course_id: int, goal_score: float,
                 exam_date: date) -> int:
        days_left = (exam_date - date.today()).days
        if days_left <= 0:
            days_left = 30

        # 获取薄弱知识点
        self._kg.build_graph(course_id)
        weak_nodes = self._kg.get_weak_nodes(self._student_id)
        weak_names = [w["kp_name"] for w in weak_nodes]

        tasks = []
        used_days: set[int] = set()
        phases = max(1, days_left // 7)

        def alloc_day(preferred: int) -> int:
            """Find nearest unused day to avoid collisions."""
            d = max(1, min(preferred, days_left))
            while d in used_days and d <= days_left:
                d += 1
            if d > days_left:
                d = preferred
                while d in used_days and d >= 1:
                    d -= 1
            used_days.add(d)
            return d

        # 阶段1：基础知识补强
        base_tasks = min(len(weak_names), max(3, phases))
        for i, name in enumerate(weak_names[:base_tasks]):
            day = alloc_day(1 + i * max(1, days_left // (base_tasks + 1)))
            tasks.append({
                "day": day,
                "task": f"强化「{name}」",
                "type": "review",
                "duration_min": 60,
                "priority": "high" if i < 3 else "medium",
                "done": False,
            })

        # 阶段2：综合练习
        for phase_idx in range(phases):
            week_start = 1 + phase_idx * max(1, days_left // phases)
            day = alloc_day(week_start + 2)
            tasks.append({
                "day": day,
                "task": f"第{phase_idx+1}阶段综合练习",
                "type": "practice",
                "duration_min": 90,
                "priority": "high",
                "done": False,
            })

        # 阶段3：模拟考试
        day = alloc_day(days_left - 3)
        tasks.append({
            "day": day,
            "task": "模拟考试（限时完成）",
            "type": "mock_exam",
            "duration_min": 120,
            "priority": "high",
            "done": False,
        })

        # 最后复习
        day = alloc_day(days_left - 1)
        tasks.append({
            "day": day,
            "task": "最终复习与查漏补缺",
            "type": "review",
            "duration_min": 60,
            "priority": "high",
            "done": False,
        })

        # 排序
        tasks.sort(key=lambda t: t["day"])

        plan_id = self._dao.create(
            self._student_id, subject, goal_score, exam_date, tasks,
        )
        return plan_id

    def get_plans(self) -> list[dict]:
        return self._dao.get_by_student(self._student_id)

    def get_active_plans(self) -> list[dict]:
        return self._dao.get_active(self._student_id)

    def update_progress(self, plan_id: int, progress: float) -> bool:
        return self._dao.update_progress(plan_id, progress)

    def complete_plan(self, plan_id: int) -> bool:
        return self._dao.complete(plan_id)
