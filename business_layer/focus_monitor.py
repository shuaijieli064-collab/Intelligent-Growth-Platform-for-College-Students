"""专注度监测系统."""
from datetime import date, timedelta
from data_layer.database import DatabaseManager
from data_layer.dao.study_record_dao import StudyRecordDAO


class FocusMonitor:
    def __init__(self, db: DatabaseManager, student_id: int) -> None:
        self._dao = StudyRecordDAO(db)
        self._student_id = student_id

    def get_current_focus(self) -> float:
        records = self._dao.get_by_student(self._student_id, days=1)
        if not records:
            return 0.0
        focus_vals = [r["focus_score"] for r in records if r["focus_score"] is not None]
        return round(sum(focus_vals) / len(focus_vals), 1) if focus_vals else 0.0

    def get_daily_focus(self, days: int = 7) -> list[dict]:
        records = self._dao.get_by_student(self._student_id, days=days)
        daily = {}
        for r in records:
            d = str(r["study_date"])
            if d not in daily:
                daily[d] = {"scores": [], "hours": 0}
            daily[d]["hours"] += float(r["study_hours"])
            if r["focus_score"] is not None:
                daily[d]["scores"].append(r["focus_score"])

        return [
            {
                "date": d, "hours": round(v["hours"], 1),
                "avg_focus": round(sum(v["scores"]) / len(v["scores"]), 1)
                if v["scores"] else 0,
            }
            for d, v in sorted(daily.items())
        ]

    def get_focus_trend(self, days: int = 14) -> dict:
        daily = self.get_daily_focus(days)
        if not daily:
            return {"trend": "stable", "avg": 0, "change": 0, "daily": []}

        first_week = [d["avg_focus"] for d in daily[:7]]
        second_week = [d["avg_focus"] for d in daily[7:14]]

        avg = round(sum(d["avg_focus"] for d in daily) / len(daily), 1)
        week1_avg = sum(first_week) / len(first_week) if first_week else avg
        week2_avg = sum(second_week) / len(second_week) if second_week else avg
        change = round(week2_avg - week1_avg, 1)

        if change > 5:
            trend = "improving"
        elif change < -5:
            trend = "declining"
        else:
            trend = "stable"

        return {"trend": trend, "avg": avg, "change": change, "daily": daily}

    def get_focus_heatmap(self, days: int = 30) -> dict[str, float]:
        daily = self.get_daily_focus(days)
        return {d["date"]: d["avg_focus"] for d in daily}

    def get_focus_level(self) -> str:
        score = self.get_current_focus()
        if score >= 80:
            return "高度专注 🟢"
        elif score >= 60:
            return "正常 🟡"
        elif score >= 40:
            return "注意力分散 🟠"
        return "严重分心 🔴"
