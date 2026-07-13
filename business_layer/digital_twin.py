"""数字孪生模块 - 学生健康度四维度评估."""
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

from config import HEALTH_WEIGHTS, RISK_THRESHOLDS
from data_layer.database import DatabaseManager
from data_layer.dao.health_dao import HealthDAO
from data_layer.dao.course_dao import StudentCourseDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.models import HealthAssessment
from utils.helpers import clamp


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class HealthResult:
    academic: float
    physical: float
    mental: float
    social: float
    overall: float
    risk_level: RiskLevel


class DigitalTwin:
    ACADEMIC_WEIGHT = HEALTH_WEIGHTS["academic"]
    PHYSICAL_WEIGHT = HEALTH_WEIGHTS["physical"]
    MENTAL_WEIGHT = HEALTH_WEIGHTS["mental"]
    SOCIAL_WEIGHT = HEALTH_WEIGHTS["social"]

    def __init__(self, student_id: int, db: DatabaseManager) -> None:
        self._student_id = student_id
        self._health_dao = HealthDAO(db)
        self._score_dao = StudentCourseDAO(db)
        self._study_dao = StudyRecordDAO(db)

    def calculate_academic_health(self) -> float:
        scores = self._score_dao.get_student_scores(self._student_id)
        if not scores:
            return 50.0
        total = 0.0
        for s in scores:
            parts = []
            us = float(s["usual_score"]) if s.get("usual_score") is not None else None
            ms = float(s["midterm_score"]) if s.get("midterm_score") is not None else None
            fs = float(s["final_score"]) if s.get("final_score") is not None else None
            if us is not None:
                parts.append(us * 0.3)
            if ms is not None:
                parts.append(ms * 0.3)
            if fs is not None:
                parts.append(fs * 0.4)
            elif parts:
                remaining = 1.0 - 0.3 - 0.3
                parts.append(parts[-1] * (remaining / 0.3) if parts else 0)
            if parts:
                total += sum(parts)
        avg = total / len(scores) if scores else 50.0
        return round(clamp(avg), 1)

    def calculate_physical_health(self, records: list = None) -> float:
        # 优先使用真实运动/睡眠数据
        physical_records = self._health_dao.get_physical_records(self._student_id, days=14)
        if physical_records:
            durations = [r["exercise_duration"] for r in physical_records if r["exercise_duration"]]
            sleeps = [float(r["sleep_hours"]) for r in physical_records if r["sleep_hours"] is not None]
            steps_list = [r["steps"] for r in physical_records if r["steps"]]

            exercise_score = min(100, (sum(durations) / max(1, len(durations))) / 60 * 100) if durations else 0
            sleep_score = 0
            if sleeps:
                avg_sleep = sum(sleeps) / len(sleeps)
                sleep_score = 100 - min(40, abs(avg_sleep - 7) * 15)
            step_score = min(100, (sum(steps_list) / max(1, len(steps_list))) / 8000 * 100) if steps_list else 0
            return round(clamp(exercise_score * 0.4 + sleep_score * 0.4 + step_score * 0.2), 1)

        # 回退：从学习记录推算
        if records is None:
            records = self._study_dao.get_by_student(self._student_id, days=14)
        if not records:
            return 50.0
        hours = [r["study_hours"] for r in records]
        tasks = [r["task_completed"] for r in records]
        focus_vals = [r["focus_score"] for r in records if r["focus_score"] is not None]

        consistency = 100 - min(100, max(0, (max(hours) - min(hours)) / max(1, sum(hours) / len(hours)) * 40))
        hour_score = min(100, (sum(hours) / len(hours)) / 8 * 100)
        task_score = min(100, (sum(tasks) / len(tasks)) / 5 * 100)
        focus_avg = sum(focus_vals) / len(focus_vals) if focus_vals else 50

        return round(clamp(consistency * 0.2 + hour_score * 0.3 + task_score * 0.2 + focus_avg * 0.3), 1)

    def calculate_mental_health(self, records: list = None) -> float:
        # 优先使用真实心情/压力数据
        mental_records = self._health_dao.get_mental_records(self._student_id, days=14)
        if mental_records:
            moods = [r["mood_score"] for r in mental_records if r["mood_score"] is not None]
            stresses = [r["stress_level"] for r in mental_records if r["stress_level"] is not None]
            anxieties = [r["anxiety_level"] for r in mental_records if r["anxiety_level"] is not None]

            mood_score = (sum(moods) / len(moods)) * 10 if moods else 50
            stress_score = 100 - ((sum(stresses) / len(stresses)) / 5 * 100) if stresses else 50
            anxiety_score = 100 - ((sum(anxieties) / len(anxieties)) / 5 * 100) if anxieties else 50
            return round(clamp(mood_score * 0.5 + stress_score * 0.25 + anxiety_score * 0.25), 1)

        # 回退：从专注度推算
        if records is None:
            records = self._study_dao.get_by_student(self._student_id, days=14)
        if not records:
            return 50.0
        focus_vals = [r["focus_score"] for r in records if r["focus_score"] is not None]
        if len(focus_vals) < 3:
            return 55.0

        avg_focus = sum(focus_vals) / len(focus_vals)
        variance = sum((f - avg_focus) ** 2 for f in focus_vals) / len(focus_vals)
        stability = 100 - min(60, variance / 4)

        hours = [float(r["study_hours"]) for r in records]
        overload_days = sum(1 for h in hours if h > 8)
        overload_penalty = min(30, overload_days * 8)

        return round(clamp(avg_focus * 0.5 + stability * 0.5 - overload_penalty), 1)

    def calculate_social_health(self, records: list = None) -> float:
        # 优先使用真实社交活动数据
        social_records = self._health_dao.get_social_records(self._student_id, days=30)
        if social_records:
            durations = [r["duration_minutes"] for r in social_records if r["duration_minutes"]]
            interactions = [r["interaction_count"] for r in social_records if r["interaction_count"]]

            days_active = len(set(str(r["record_date"]) for r in social_records))
            activity_freq = min(100, (days_active / 30) * 100)
            duration_score = min(100, (sum(durations) / max(1, len(durations))) / 120 * 100) if durations else 0
            interaction_score = min(100, (sum(interactions) / max(1, len(interactions))) / 10 * 100) if interactions else 0
            return round(clamp(activity_freq * 0.3 + duration_score * 0.3 + interaction_score * 0.4), 1)

        # 回退：从学习活跃度推算
        if records is None:
            records = self._study_dao.get_by_student(self._student_id, days=30)
        if not records:
            return 50.0
        days_active = len(set(str(r["study_date"]) for r in records))
        consistency = min(100, (days_active / 30) * 100)
        task_rate = min(100, (sum(r["task_completed"] for r in records) / max(1, len(records))) * 20)
        return round(clamp(consistency * 0.6 + task_rate * 0.4), 1)

    def assess_overall(self) -> HealthResult:
        # 一次查询，多维度复用，消除重复 DB 请求
        records_14d = self._study_dao.get_by_student(self._student_id, days=14)
        records_30d = self._study_dao.get_by_student(self._student_id, days=30)
        academic = self.calculate_academic_health()
        physical = self.calculate_physical_health(records_14d)
        mental = self.calculate_mental_health(records_14d)
        social = self.calculate_social_health(records_30d)
        overall = round(
            academic * self.ACADEMIC_WEIGHT
            + physical * self.PHYSICAL_WEIGHT
            + mental * self.MENTAL_WEIGHT
            + social * self.SOCIAL_WEIGHT,
            1,
        )
        risk = self.determine_risk(overall)
        return HealthResult(
            academic=academic, physical=physical, mental=mental,
            social=social, overall=overall, risk_level=risk,
        )

    @staticmethod
    def determine_risk(overall: float) -> RiskLevel:
        if overall >= RISK_THRESHOLDS["low"]:
            return RiskLevel.LOW
        elif overall >= RISK_THRESHOLDS["medium"]:
            return RiskLevel.MEDIUM
        elif overall >= RISK_THRESHOLDS["high"]:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    def save_assessment(self) -> int:
        result = self.assess_overall()
        assessment = HealthAssessment(
            student_id=self._student_id,
            assessment_date=date.today(),
            academic_score=result.academic,
            physical_score=result.physical,
            mental_score=result.mental,
            social_score=result.social,
            overall_health=result.overall,
            risk_level=result.risk_level.value,
        )
        return self._health_dao.save_assessment(assessment)

    def get_history(self) -> list[HealthAssessment]:
        return self._health_dao.get_history(self._student_id)
