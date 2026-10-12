"""数据模型（dataclass）."""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Student:
    student_id: Optional[int] = None
    student_no: str = ""
    name: str = ""
    gender: str = "M"
    grade_level: str = ""
    major: str = ""
    enrollment_year: int = 2024
    created_at: Optional[datetime] = None


@dataclass
class Course:
    course_id: Optional[int] = None
    course_code: str = ""
    course_name: str = ""
    credit: float = 0.0
    semester: str = ""
    is_compulsory: bool = True
    prerequisite_course_id: Optional[int] = None
    created_by: Optional[int] = None


@dataclass
class StudentCourse:
    id: Optional[int] = None
    student_id: int = 0
    course_id: int = 0
    usual_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    predicted_final: Optional[float] = None


@dataclass
class StudyRecord:
    record_id: Optional[int] = None
    student_id: int = 0
    course_id: Optional[int] = None
    study_date: Optional[date] = None
    study_hours: float = 0.0
    task_completed: int = 0
    focus_score: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class HealthAssessment:
    assessment_id: Optional[int] = None
    student_id: int = 0
    assessment_date: Optional[date] = None
    academic_score: float = 0.0
    physical_score: float = 0.0
    mental_score: float = 0.0
    social_score: float = 0.0
    overall_health: float = 0.0
    risk_level: str = "LOW"


@dataclass
class KnowledgePoint:
    kp_id: Optional[int] = None
    kp_name: str = ""
    course_id: int = 0
    parent_kp_id: Optional[int] = None
    difficulty: int = 1
    weight: float = 1.0
    created_by: Optional[int] = None
    node_type: str = "kp"


@dataclass
class KnowledgeMastery:
    mastery_id: Optional[int] = None
    student_id: int = 0
    kp_id: int = 0
    mastery_level: float = 0.0
    last_assessed: Optional[date] = None


@dataclass
class RiskAlert:
    alert_id: Optional[int] = None
    student_id: int = 0
    alert_type: str = ""
    risk_level: str = "LOW"
    alert_message: str = ""
    rule_triggered: str = ""
    is_resolved: bool = False
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class AICoachLog:
    log_id: Optional[int] = None
    student_id: int = 0
    session_id: str = ""
    role: str = "user"
    message: str = ""
    tokens_used: int = 0
    created_at: Optional[datetime] = None


@dataclass
class PhysicalHealthRecord:
    id: Optional[int] = None
    student_id: int = 0
    record_date: Optional[date] = None
    exercise_type: Optional[str] = None
    exercise_duration: int = 0
    sleep_hours: Optional[float] = None
    steps: int = 0


@dataclass
class MentalHealthRecord:
    id: Optional[int] = None
    student_id: int = 0
    record_date: Optional[date] = None
    mood_score: Optional[int] = None
    stress_level: Optional[int] = None
    anxiety_level: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class SocialHealthRecord:
    id: Optional[int] = None
    student_id: int = 0
    record_date: Optional[date] = None
    activity_type: Optional[str] = None
    duration_minutes: int = 0
    interaction_count: int = 0


@dataclass
class User:
    user_id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    student_id: Optional[int] = None
    created_at: Optional[datetime] = None
