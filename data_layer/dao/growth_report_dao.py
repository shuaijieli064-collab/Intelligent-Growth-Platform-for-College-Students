"""成长档案 DAO."""
import json
from datetime import date
from typing import Optional
from data_layer.database import DatabaseManager


class GrowthReportDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, student_id: int, report_type: str, report_date: date,
               period_start: Optional[date], period_end: Optional[date], summary: str = "",
               detail: Optional[dict] = None, health_score: float = 0,
               risk_level: str = "LOW") -> int:
        return self._db.execute_insert(
            "INSERT INTO growth_report (student_id, report_type, report_date, "
            "period_start, period_end, summary, detail, health_score, risk_level) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (student_id, report_type, report_date, period_start, period_end,
             summary, json.dumps(detail or {}, ensure_ascii=False),
             health_score, risk_level),
        )

    def _parse_detail(self, r: dict) -> dict:
        if isinstance(r.get("detail"), str):
            try:
                r["detail"] = json.loads(r["detail"])
            except json.JSONDecodeError:
                r["detail"] = {}
        if not isinstance(r.get("detail"), dict):
            r["detail"] = {}
        return r

    def get_by_student(self, student_id: int) -> list[dict]:
        rows = self._db.execute_query(
            "SELECT * FROM growth_report WHERE student_id = %s ORDER BY report_date DESC",
            (student_id,),
        )
        return [self._parse_detail(r) for r in rows]

    def get_by_type(self, student_id: int, report_type: str) -> list[dict]:
        return self._db.execute_query(
            "SELECT * FROM growth_report WHERE student_id = %s AND report_type = %s "
            "ORDER BY report_date DESC",
            (student_id, report_type),
        )

    def get_latest(self, student_id: int, report_type: str = None) -> dict | None:
        if report_type:
            rows = self._db.execute_query(
                "SELECT * FROM growth_report WHERE student_id = %s AND report_type = %s "
                "ORDER BY report_date DESC LIMIT 1",
                (student_id, report_type),
            )
        else:
            rows = self._db.execute_query(
                "SELECT * FROM growth_report WHERE student_id = %s "
                "ORDER BY report_date DESC LIMIT 1",
                (student_id,),
            )
        return self._parse_detail(rows[0]) if rows else None

    def get_by_id(self, report_id: int) -> dict | None:
        rows = self._db.execute_query(
            "SELECT * FROM growth_report WHERE id = %s",
            (report_id,),
        )
        return self._parse_detail(rows[0]) if rows else None

    def delete(self, report_id: int) -> bool:
        return self._db.execute_update(
            "DELETE FROM growth_report WHERE id = %s", (report_id,),
        ) > 0
