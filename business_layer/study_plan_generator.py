"""智能学习计划生成器 - 个性化备考计划（每日多任务）."""
from datetime import date, timedelta
from data_layer.database import DatabaseManager
from data_layer.dao.study_plan_dao import StudyPlanDAO
from business_layer.knowledge_graph import KnowledgeGraph

# 任务类型 → 说明
TASK_TYPE_LABELS = {
    "review": "基础学习",
    "practice": "专项练习",
    "mock_exam": "模拟考试",
    "summarize": "总结归纳",
    "memorize": "背诵记忆",
}


class StudyPlanGenerator:
    def __init__(self, db: DatabaseManager, student_id: int) -> None:
        self._db = db
        self._student_id = student_id
        self._dao = StudyPlanDAO(db)
        self._kg = KnowledgeGraph(db)

    def generate(self, subject: str, course_id: int, goal_score: float,
                 exam_date: date, daily_minutes: int = 90) -> int:
        days_left = (exam_date - date.today()).days
        if days_left <= 0:
            days_left = 30
        daily_minutes = max(30, min(int(daily_minutes), 480))

        # 获取薄弱知识点
        self._kg.build_graph(course_id, self._student_id)
        weak_nodes = self._kg.get_weak_nodes(self._student_id)
        weak_names = [w["kp_name"] for w in weak_nodes][:5]

        tasks = []
        used_days: set[int] = set()

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

        def split_daily(parts: list[tuple[float, str]]) -> list[int]:
            """按比例拆分每日时长，保证每任务 >= 15 分钟且总和 <= daily_minutes."""
            total_ratio = sum(p[0] for p in parts)
            durations = [max(15, int(daily_minutes * p[0] / total_ratio)) for p in parts]
            # 若超出预算，依次削减
            overflow = sum(durations) - daily_minutes
            i = 0
            while overflow > 0 and i < len(durations):
                cut = min(overflow, durations[i] - 15)
                durations[i] -= cut
                overflow -= cut
                i += 1
            return durations

        # ========== 阶段1：基础知识补强（每个薄弱知识点 1 天，含学习/练习/背诵） ==========
        weak_span = max(1, days_left // 2)
        step = max(1, weak_span // max(1, len(weak_names)))
        for i, name in enumerate(weak_names):
            day = alloc_day(1 + i * step)
            durs = split_daily([(0.4, "learn"), (0.3, "practice"), (0.2, "memorize")])
            tasks.append({
                "day": day,
                "task": f"系统学习「{name}」核心概念与定义",
                "type": "review",
                "duration_min": durs[0],
                "priority": "high" if i < 2 else "medium",
                "done": False,
            })
            tasks.append({
                "day": day,
                "task": f"「{name}」典型例题精练",
                "type": "practice",
                "duration_min": durs[1],
                "priority": "high" if i < 2 else "medium",
                "done": False,
            })
            tasks.append({
                "day": day,
                "task": f"「{name}」要点背诵与当日总结",
                "type": "memorize",
                "duration_min": durs[2],
                "priority": "medium",
                "done": False,
            })

        # ========== 阶段2：综合练习（每阶段 1 天，含练习 + 错题归纳） ==========
        phases = max(2, min(days_left // 7, 4))
        for phase_idx in range(phases):
            week_start = weak_span + 2 + phase_idx * max(1, (days_left - weak_span) // max(1, phases + 1))
            day = alloc_day(week_start)
            durs = split_daily([(0.5, "practice"), (0.3, "summarize")])
            tasks.append({
                "day": day,
                "task": f"第{phase_idx + 1}阶段综合练习（限时完成成套题目）",
                "type": "practice",
                "duration_min": durs[0],
                "priority": "medium",
                "done": False,
            })
            tasks.append({
                "day": day,
                "task": "错题整理与题型归纳（记录错因与解法）",
                "type": "summarize",
                "duration_min": durs[1],
                "priority": "medium",
                "done": False,
            })

        # ========== 阶段3：模拟考试（含考试 + 试卷分析） ==========
        day = alloc_day(max(weak_span + 2, days_left - 4))
        durs = split_daily([(0.6, "exam"), (0.3, "analysis")])
        tasks.append({
            "day": day,
            "task": "模拟考试（限时完成，检验复习效果）",
            "type": "mock_exam",
            "duration_min": durs[0],
            "priority": "high",
            "done": False,
        })
        tasks.append({
            "day": day,
            "task": "试卷分析查漏（统计失分点，定位薄弱环节）",
            "type": "summarize",
            "duration_min": durs[1],
            "priority": "high",
            "done": False,
        })

        # ========== 阶段4：最终复习（含回顾 + 错题重做 + 速记） ==========
        day = alloc_day(max(1, days_left - 1))
        durs = split_daily([(0.4, "review"), (0.3, "redo"), (0.2, "quick")])
        tasks.append({
            "day": day,
            "task": "核心概念与公式快速回顾",
            "type": "review",
            "duration_min": durs[0],
            "priority": "high",
            "done": False,
        })
        tasks.append({
            "day": day,
            "task": "错题本重做（巩固易错点）",
            "type": "practice",
            "duration_min": durs[1],
            "priority": "high",
            "done": False,
        })
        tasks.append({
            "day": day,
            "task": "考前要点速记",
            "type": "memorize",
            "duration_min": durs[2],
            "priority": "medium",
            "done": False,
        })

        # 排序
        tasks.sort(key=lambda t: (t["day"], -len(t["task"])))

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
