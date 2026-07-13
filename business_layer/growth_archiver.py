"""成长档案系统 - 自动生成周/月/学期报告."""
from datetime import date, timedelta
from data_layer.database import DatabaseManager
from data_layer.dao.growth_report_dao import GrowthReportDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from business_layer.digital_twin import DigitalTwin
from business_layer.focus_monitor import FocusMonitor


class GrowthArchiver:
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEMESTER = "semester"

    def __init__(self, db: DatabaseManager, student_id: int) -> None:
        self._db = db
        self._student_id = student_id
        self._dao = GrowthReportDAO(db)
        self._twin = DigitalTwin(student_id, db)
        self._focus = FocusMonitor(db, student_id)
        self._study_dao = StudyRecordDAO(db)

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

    def _generate(self, report_type: str, start: date, end: date) -> int:
        # 健康评估
        health = self._twin.assess_overall()
        health_dao = self._twin._health_dao
        history = health_dao.get_history(self._student_id)
        prev_health = history[1].overall_health if len(history) > 1 else health.overall

        # 学习数据
        records = self._study_dao.get_by_student(self._student_id, days=(end - start).days)
        total_hours = sum(float(r["study_hours"]) for r in records)
        total_tasks = sum(r["task_completed"] for r in records)
        active_days = len(set(str(r["study_date"]) for r in records))
        focus_avg = round(
            sum(r["focus_score"] for r in records if r["focus_score"]) / max(1, len([r for r in records if r["focus_score"]])),
            1,
        ) if records else 0

        # 专注趋势
        focus_trend = self._focus.get_focus_trend()

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
                "focus_trend": focus_trend["trend"],
            },
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
