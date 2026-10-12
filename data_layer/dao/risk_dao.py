"""风险告警数据访问对象."""
from datetime import datetime
from data_layer.database import DatabaseManager
from data_layer.models import RiskAlert


class RiskDAO:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def save_alert(self, alert: RiskAlert) -> int:
        sql = ("INSERT INTO risk_alert (student_id, alert_type, risk_level, alert_message, "
               "rule_triggered) VALUES (%s, %s, %s, %s, %s)")
        if self._db._db_type == "postgres":
            sql += " RETURNING alert_id"
        return self._db.execute_insert(
            sql,
            (alert.student_id, alert.alert_type, alert.risk_level,
             alert.alert_message, alert.rule_triggered),
        )

    def save_alerts(self, alerts: list[RiskAlert]) -> None:
        """批量插入告警：同一规则已有未解决告警时跳过，避免重复刷屏."""
        for alert in alerts:
            if self.has_open_alert(alert.student_id, alert.rule_triggered):
                continue
            self.save_alert(alert)

    def has_open_alert(self, student_id: int, rule_triggered: str) -> bool:
        rows = self._db.execute_query(
            "SELECT alert_id FROM risk_alert WHERE student_id = %s "
            "AND rule_triggered = %s AND is_resolved = FALSE LIMIT 1",
            (student_id, rule_triggered),
        )
        return len(rows) > 0

    def get_by_student(self, student_id: int,
                       unresolved_only: bool = False) -> list[RiskAlert]:
        sql = "SELECT * FROM risk_alert WHERE student_id = %s"
        if unresolved_only:
            sql += " AND is_resolved = FALSE"
        sql += " ORDER BY created_at DESC"
        rows = self._db.execute_query(sql, (student_id,))
        return [RiskAlert(**r) for r in rows]

    def get_all_active(self) -> list[RiskAlert]:
        rows = self._db.execute_query(
            "SELECT * FROM risk_alert WHERE is_resolved = FALSE ORDER BY created_at DESC"
        )
        return [RiskAlert(**r) for r in rows]

    def resolve(self, alert_id: int, student_id: int | None = None) -> bool:
        if student_id is None:
            sql = "UPDATE risk_alert SET is_resolved=TRUE, resolved_at=%s WHERE alert_id=%s"
            params = (datetime.now(), alert_id)
        else:
            sql = ("UPDATE risk_alert SET is_resolved=TRUE, resolved_at=%s "
                   "WHERE alert_id=%s AND student_id=%s")
            params = (datetime.now(), alert_id, student_id)
        return self._db.execute_update(sql, params) > 0

    def delete(self, alert_id: int, student_id: int | None = None) -> bool:
        if student_id is None:
            sql, params = "DELETE FROM risk_alert WHERE alert_id = %s", (alert_id,)
        else:
            sql = "DELETE FROM risk_alert WHERE alert_id = %s AND student_id = %s"
            params = (alert_id, student_id)
        return self._db.execute_update(sql, params) > 0
