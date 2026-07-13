"""风险预警模块 - 规则引擎驱动的学生风险检测."""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Callable

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import StudentCourseDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.health_dao import HealthDAO
from data_layer.dao.risk_dao import RiskDAO
from data_layer.models import RiskAlert


@dataclass
class Rule:
    name: str
    alert_type: str
    condition: Callable[..., bool]
    message_template: str
    risk_level: str = "MEDIUM"


class RiskWarningSystem:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._risk_dao = RiskDAO(db)
        self._score_dao = StudentCourseDAO(db)
        self._study_dao = StudyRecordDAO(db)
        self._health_dao = HealthDAO(db)
        self._rules: list[Rule] = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        self.add_rule(Rule(
            name="ACADEMIC_FAILING",
            alert_type="学业",
            risk_level="HIGH",
            condition=lambda sid: any(
                s.get("final_score") is not None and s["final_score"] < 60
                for s in self._score_dao.get_student_scores(sid)
            ),
            message_template="存在不及格课程，请立即制定补课计划",
        ))

        self.add_rule(Rule(
            name="ACADEMIC_DECLINING",
            alert_type="学业",
            risk_level="MEDIUM",
            condition=lambda sid: self._check_declining(sid),
            message_template="近期学习时长持续下降，注意保持学习节奏",
        ))

        self.add_rule(Rule(
            name="HEALTH_CRITICAL",
            alert_type="健康",
            risk_level="HIGH",
            condition=lambda sid: self._check_health_critical(sid),
            message_template="综合健康度低于40分，需重点关注身心状态",
        ))

        self.add_rule(Rule(
            name="HEALTH_DECLINING",
            alert_type="健康",
            risk_level="MEDIUM",
            condition=lambda sid: self._check_health_declining(sid),
            message_template="近两周健康度下降超过15分，请关注变化趋势",
        ))

        self.add_rule(Rule(
            name="MENTAL_BURNOUT",
            alert_type="心理",
            risk_level="HIGH",
            condition=lambda sid: self._study_dao.get_daily_focus_avg(sid, 7) < 30,
            message_template="近7天专注度均值低于30，可能存在倦怠风险",
        ))

        self.add_rule(Rule(
            name="LOW_STUDY_HOURS",
            alert_type="学业",
            risk_level="MEDIUM",
            condition=lambda sid: self._check_low_hours(sid),
            message_template="近7天日均学习时长不足2小时，需增加学习投入",
        ))

        self.add_rule(Rule(
            name="TASK_COMPLETION_LOW",
            alert_type="学业",
            risk_level="LOW",
            condition=lambda sid: self._check_low_tasks(sid),
            message_template="任务完成率偏低，建议分解任务逐步完成",
        ))

    def add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)

    def evaluate(self, student_id: int) -> list[RiskAlert]:
        alerts = []
        for rule in self._rules:
            try:
                if rule.condition(student_id):
                    alert = RiskAlert(
                        student_id=student_id,
                        alert_type=rule.alert_type,
                        risk_level=rule.risk_level,
                        alert_message=rule.message_template,
                        rule_triggered=rule.name,
                    )
                    alerts.append(alert)
            except Exception:
                pass
        return alerts

    def save_alerts(self, alerts: list[RiskAlert]) -> None:
        for alert in alerts:
            self._risk_dao.save_alert(alert)

    def evaluate_and_save(self, student_id: int) -> list[RiskAlert]:
        alerts = self.evaluate(student_id)
        self.save_alerts(alerts)
        return alerts

    def resolve_alert(self, alert_id: int) -> bool:
        return self._risk_dao.resolve(alert_id)

    def get_active_alerts(self, student_id: int) -> list[RiskAlert]:
        return self._risk_dao.get_by_student(student_id, unresolved_only=True)

    # ── 私有检测方法 ──────────────────────────────────────────

    def _check_declining(self, student_id: int) -> bool:
        weekly = self._study_dao.get_weekly_hours(student_id)
        if len(weekly) < 3:
            return False
        hours = [w["total_hours"] for w in weekly[-3:]]
        return hours[-1] < hours[-2] < hours[-3]

    def _check_health_critical(self, student_id: int) -> bool:
        latest = self._health_dao.get_latest(student_id)
        return latest is not None and latest.overall_health < 40

    def _check_health_declining(self, student_id: int) -> bool:
        history = self._health_dao.get_history(student_id)
        if len(history) < 2:
            return False
        recent = history[0].overall_health
        earlier = history[-1].overall_health
        return earlier - recent > 15

    def _check_low_hours(self, student_id: int) -> bool:
        records = self._study_dao.get_by_student(student_id, days=7)
        if not records:
            return True
        avg = sum(float(r["study_hours"]) for r in records) / len(records)
        return avg < 2.0

    def _check_low_tasks(self, student_id: int) -> bool:
        records = self._study_dao.get_by_student(student_id, days=7)
        if not records:
            return False
        total = sum(r["task_completed"] for r in records)
        return total / len(records) < 1.5
