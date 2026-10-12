"""成长档案系统 - 自动生成周/月/学期报告."""
from datetime import date, timedelta
from data_layer.database import DatabaseManager
from data_layer.dao.growth_report_dao import GrowthReportDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.course_dao import StudentCourseDAO
from business_layer.digital_twin import DigitalTwin
from business_layer.focus_monitor import FocusMonitor
from business_layer.risk_warning import RiskWarningSystem
from business_layer.knowledge_graph import KnowledgeGraph


class GrowthArchiver:
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEMESTER = "semester"

    DIMENSION_NAMES = {
        "academic": "学业", "physical": "身体",
        "mental": "心理", "social": "社交",
    }

    def __init__(self, db: DatabaseManager, student_id: int) -> None:
        self._db = db
        self._student_id = student_id
        self._dao = GrowthReportDAO(db)
        self._twin = DigitalTwin(student_id, db)
        self._focus = FocusMonitor(db, student_id)
        self._study_dao = StudyRecordDAO(db)
        self._sc_dao = StudentCourseDAO(db)

    def generate_weekly(self, end_date: date = None) -> int:
        if end_date is None:
            end_date = date.today()
        start = end_date - timedelta(days=7)
        return self._generate(self.WEEKLY, start, end_date)

    def generate_monthly(self, end_date: date = None) -> int:
        if end_date is None:
            end_date = date.today()
        start = end_date - timedelta(days=30)
        return self._generate(self.MONTHLY, start, end_date)

    def generate_semester(self, end_date: date = None) -> int:
        if end_date is None:
            end_date = date.today()
        start = end_date - timedelta(days=120)
        return self._generate(self.SEMESTER, start, end_date)

    def _build_highlights_suggestions(
        self, health, total_hours, active_days, focus_avg,
        graded, weak_top, alerts, days_span,
    ) -> tuple[list[str], list[str]]:
        highlights: list[str] = []
        suggestions: list[str] = []
        overall = health.overall

        # ---------- 亮点 ----------
        if overall >= 80:
            highlights.append(f"综合健康度 {overall:.1f} 分，整体状态非常优秀，请继续保持！")
        elif overall >= 70:
            highlights.append(f"综合健康度 {overall:.1f} 分，整体状态良好。")
        elif overall >= 60:
            highlights.append(f"综合健康度 {overall:.1f} 分，处于中等水平，仍有提升空间。")

        for dim_key, dim_name in self.DIMENSION_NAMES.items():
            score = getattr(health, dim_key, 0)
            if score >= 75:
                highlights.append(f"「{dim_name}」维度表现突出（{score:.1f} 分）。")

        if total_hours > 0:
            if total_hours >= days_span * 2:
                highlights.append(f"本期累计学习 {total_hours:.1f} 小时，学习投入非常充足。")
            elif total_hours >= days_span:
                highlights.append(f"本期累计学习 {total_hours:.1f} 小时，保持了稳定的学习节奏。")

        if active_days >= max(3, days_span * 0.6):
            highlights.append(f"本期活跃 {active_days} 天，学习习惯稳定。")

        if focus_avg >= 70:
            highlights.append(f"平均专注度 {focus_avg:.0f} 分，学习效率很高。")

        for s in graded:
            if s.get("final_score") is not None and float(s["final_score"]) >= 85:
                highlights.append(f"「{s['course_name']}」期末成绩 {float(s['final_score']):.0f} 分，表现优秀。")

        # 没有亮点时给出引导性文案
        if not highlights:
            if total_hours == 0 and not graded:
                highlights.append("本期待开启成长记录之旅——先录入学习记录和成绩，系统将为你绘制成长曲线。")
            else:
                highlights.append("本期处于蓄力期，坚持记录学习数据，亮点将在积累中浮现。")

        # ---------- 建议 ----------
        if overall < 40:
            suggestions.append("健康度处于临界水平，建议立即调整作息与学习安排，必要时寻求老师或辅导员帮助。")
        elif overall < 60:
            suggestions.append(f"综合健康度仅 {overall:.1f} 分，建议优先关注「{self._worst_dimension(health)}」维度，合理安排学习与休息。")

        for dim_key, dim_name in self.DIMENSION_NAMES.items():
            score = getattr(health, dim_key, 0)
            if 0 < score < 60:
                suggestions.append(f"「{dim_name}」维度仅 {score:.1f} 分，建议每周设定小目标逐步改善。")

        if total_hours > 0 and total_hours / max(1, days_span) < 1:
            suggestions.append(f"日均学习仅 {total_hours / max(1, days_span):.1f} 小时，建议提升至每天 2 小时以上。")
        elif total_hours == 0:
            suggestions.append("本期暂无学习记录，建议从今天开始每日打卡学习，哪怕 30 分钟也能积累数据。")

        if 0 < active_days < max(3, days_span * 0.4):
            suggestions.append(f"本期仅活跃 {active_days} 天，建议养成每日学习打卡的习惯。")

        if 0 < focus_avg < 50:
            suggestions.append(f"平均专注度 {focus_avg:.0f} 分偏低，建议使用番茄工作法（25 分钟专注 + 5 分钟休息）。")

        for s in graded:
            fs = s.get("final_score")
            if fs is not None and float(fs) < 60:
                suggestions.append(f"「{s['course_name']}」期末成绩 {float(fs):.0f} 分未及格，建议尽快制定补考复习计划，重点攻克薄弱知识点。")
            elif fs is not None and float(fs) < 75:
                suggestions.append(f"「{s['course_name']}」期末成绩 {float(fs):.0f} 分，建议针对错题进行专项强化。")

        for w in weak_top[:2]:
            suggestions.append(f"知识点「{w['kp_name']}」掌握度仅 {w['mastery']}%，建议优先补强。")

        for a in alerts[:3]:
            suggestions.append(f"存在{self._risk_label(a.risk_level)}风险：{a.alert_message}")

        if not suggestions:
            suggestions.append("本期各项指标均衡，建议保持现有节奏，并尝试挑战更高目标。")

        return highlights, suggestions

    @staticmethod
    def _worst_dimension(health) -> str:
        dims = [("学业", health.academic), ("身体", health.physical),
                ("心理", health.mental), ("社交", health.social)]
        return min(dims, key=lambda x: x[1])[0]

    @staticmethod
    def _risk_label(level: str) -> str:
        return {"LOW": "低", "MEDIUM": "中", "HIGH": "高", "CRITICAL": "严重"}.get(level.upper(), level)

    def _generate(self, report_type: str, start: date, end: date) -> int:
        # 健康评估
        health = self._twin.assess_overall()
        history = self._twin.get_history()
        prev_health = history[1].overall_health if len(history) > 1 else health.overall

        # 学习数据
        records = self._study_dao.get_by_student(self._student_id, days=(end - start).days)
        total_hours = sum(float(r["study_hours"] or 0) for r in records)
        total_tasks = sum(r["task_completed"] or 0 for r in records)
        active_days = len(set(str(r["study_date"]) for r in records))
        focus_values = [r["focus_score"] for r in records if r.get("focus_score")]
        focus_avg = round(sum(focus_values) / len(focus_values), 1) if focus_values else 0

        # 每日学习序列（趋势图用）
        daily_map: dict[str, float] = {}
        for r in records:
            d = str(r["study_date"])
            daily_map[d] = daily_map.get(d, 0) + float(r["study_hours"] or 0)
        daily_study = [{"date": d, "hours": round(h, 1)} for d, h in sorted(daily_map.items())]

        # 专注趋势
        focus_trend = self._focus.get_focus_trend()

        # 课程成绩概览
        scores = self._sc_dao.get_student_scores(self._student_id)
        graded = [
            {
                "course_name": s.get("course_name", ""),
                "usual_score": s.get("usual_score"),
                "midterm_score": s.get("midterm_score"),
                "final_score": s.get("final_score"),
            }
            for s in scores if s.get("final_score") is not None
        ]
        avg_final = round(
            sum(float(s["final_score"]) for s in graded) / len(graded), 1
        ) if graded else None

        # 薄弱知识点（覆盖学生所选课程）
        weak_top: list[dict] = []
        try:
            kg = KnowledgeGraph(self._db)
            all_weak: list[dict] = []
            for s in scores:
                cid = s.get("course_id")
                if not cid:
                    continue
                kg.build_graph(cid, self._student_id)
                all_weak.extend(kg.get_weak_nodes(self._student_id))
            seen: set = set()
            for w in sorted(all_weak, key=lambda x: x.get("mastery", 100)):
                k = w.get("kp_name")
                if k and k not in seen:
                    seen.add(k)
                    weak_top.append(w)
                if len(weak_top) >= 3:
                    break
        except Exception:
            weak_top = []

        # 风险告警
        try:
            alerts = RiskWarningSystem(self._db).get_active_alerts(self._student_id)
        except Exception:
            alerts = []

        # 亮点与建议
        days_span = max(1, (end - start).days)
        highlights, suggestions = self._build_highlights_suggestions(
            health, total_hours, active_days, focus_avg,
            graded, weak_top, alerts, days_span,
        )

        # 摘要
        health_change = round(health.overall - prev_health, 1)
        change_sign = "↑" if health_change > 0 else "↓" if health_change < 0 else "→"
        summary = (
            f"健康度: {health.overall}/100 ({change_sign}{abs(health_change)}), "
            f"风险: {health.risk_level.value}, "
            f"总学习: {total_hours:.0f}h, "
            f"活跃: {active_days}天, "
            f"专注: {focus_avg}/100"
        )

        # 详细数据
        detail = {
            "health": {
                "overall": health.overall, "academic": health.academic,
                "physical": health.physical, "mental": health.mental,
                "social": health.social, "risk_level": health.risk_level.value,
                "change": health_change,
            },
            "study": {
                "total_hours": round(total_hours, 1), "total_tasks": total_tasks,
                "active_days": active_days, "avg_focus": focus_avg,
                "focus_trend": focus_trend.get("trend", []),
                "daily_study": daily_study,
            },
            "courses": graded,
            "avg_final_score": avg_final,
            "weak_points": [
                {"kp_name": w.get("kp_name"), "mastery": w.get("mastery")} for w in weak_top
            ],
            "alerts": [
                {"type": a.alert_type, "level": a.risk_level, "message": a.alert_message}
                for a in alerts[:5]
            ],
            "highlights": highlights,
            "suggestions": suggestions,
            "period": f"{start} ~ {end}",
        }

        return self._dao.create(
            self._student_id, report_type, end, start, end,
            summary, detail, health.overall, health.risk_level.value,
        )

    def get_reports(self) -> list[dict]:
        return self._dao.get_by_student(self._student_id)

    def get_report(self, report_id: int) -> dict | None:
        return self._dao.get_by_id(report_id)

    def generate_report(self, report_type: str) -> dict | None:
        if report_type == self.WEEKLY:
            report_id = self.generate_weekly()
        elif report_type == self.MONTHLY:
            report_id = self.generate_monthly()
        elif report_type == self.SEMESTER:
            report_id = self.generate_semester()
        else:
            return None
        return self._dao.get_by_id(report_id)

    def get_latest_weekly(self) -> dict | None:
        return self._dao.get_latest(self._student_id, self.WEEKLY)

    def get_latest_monthly(self) -> dict | None:
        return self._dao.get_latest(self._student_id, self.MONTHLY)
