"""首页仪表盘 - 汇总卡片."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QScrollArea, QGroupBox, QListWidget,
)
from PyQt5.QtCore import Qt

from data_layer.database import DatabaseManager
from data_layer.dao.student_dao import StudentDAO
from data_layer.dao.health_dao import HealthDAO
from data_layer.dao.risk_dao import RiskDAO
from business_layer.digital_twin import DigitalTwin, RiskLevel
from presentation_layer.styles import get_risk_colors, get_theme_color


class DashboardWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._student_dao = StudentDAO(db)
        self._health_dao = HealthDAO(db)
        self._risk_dao = RiskDAO(db)
        self._twin = DigitalTwin(student_id, db)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self._title = QLabel("")
        self._title.setStyleSheet("font-size: 34px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(self._title)

        self._subtitle = QLabel("")
        self._subtitle.setStyleSheet("font-size: 28px; color: #666666; margin-bottom: 8px;")
        layout.addWidget(self._subtitle)

        # 健康度卡片行
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self._health_card, self._health_value_lbl = self._make_card("综合健康度", "--", "健康指数")
        cards_layout.addWidget(self._health_card)

        self._risk_card, self._risk_value_lbl = self._make_card("风险等级", "--", "")
        cards_layout.addWidget(self._risk_card)

        self._alert_card, self._alert_value_lbl = self._make_card("活跃告警", "--", "")
        cards_layout.addWidget(self._alert_card)

        self._acad_card, self._acad_value_lbl = self._make_card("学业健康", "--", "四维度评分")
        cards_layout.addWidget(self._acad_card)

        layout.addLayout(cards_layout)

        # 四维度详情
        dims_group = QGroupBox("四维度健康详情")
        self._dims_layout = QGridLayout(dims_group)
        self._dims_layout.setSpacing(12)
        self._dim_labels = {}
        for i, (name, label_cn, desc) in enumerate([
            ("academic", "学术健康", "课程成绩综合评估"),
            ("physical", "身体健康", "学习规律性与任务完成度"),
            ("mental", "心理健康", "专注度稳定性和情绪状态"),
            ("social", "社交健康", "学习活跃度与持续性"),
        ]):
            lbl = QLabel(label_cn)
            self._dims_layout.addWidget(lbl, i, 0)
            val = QLabel("--")
            val.setStyleSheet("font-size: 32px; font-weight: bold;")
            self._dims_layout.addWidget(val, i, 1)
            self._dims_layout.addWidget(QLabel(desc), i, 2)
            self._dim_labels[name] = val
        layout.addWidget(dims_group)

        # 最近告警
        alerts_group = QGroupBox("最近风险告警")
        alerts_layout = QVBoxLayout(alerts_group)
        self._alert_list = QListWidget()
        self._alert_list.setMaximumHeight(150)
        alerts_layout.addWidget(self._alert_list)
        layout.addWidget(alerts_group)

        layout.addStretch()
        scroll.setWidget(container)

    def _make_card(self, title: str, value: str, desc: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(200, 110)
        clayout = QVBoxLayout(card)
        clayout.setSpacing(4)
        t = QLabel(title); t.setObjectName("cardTitle"); clayout.addWidget(t)
        v = QLabel(value)
        v.setObjectName("cardValue")
        clayout.addWidget(v)
        d = QLabel(desc); d.setObjectName("cardDesc"); clayout.addWidget(d)
        return card, v

    @staticmethod
    def _risk_desc(level: RiskLevel) -> str:
        return {"LOW": "状态良好", "MEDIUM": "需关注", "HIGH": "风险较高", "CRITICAL": "紧急"}.get(
            level.value, ""
        )

    def _load_data(self) -> None:
        student = self._student_dao.get_by_id(self._student_id)
        if student:
            self._title.setText(f"欢迎回来，{student.name}！")
            self._subtitle.setText("以下是你的学习成长概览")

        result = self._twin.assess_overall()
        risk_color = get_risk_colors().get(result.risk_level.value, "#52c41a")

        self._health_value_lbl.setText(f"{result.overall}/100")
        self._health_value_lbl.setStyleSheet(f"color: {risk_color}; font-size: 38px; font-weight: bold;")

        self._risk_value_lbl.setText(result.risk_level.value)
        self._risk_value_lbl.setStyleSheet(f"color: {risk_color}; font-size: 38px; font-weight: bold;")
        self._risk_card.findChild(QLabel, "cardDesc").setText(self._risk_desc(result.risk_level))

        active_alerts = self._risk_dao.get_by_student(self._student_id, unresolved_only=True)
        alert_count = len(active_alerts)
        alert_color = "#dc2626" if alert_count > 0 else "#059669"
        self._alert_value_lbl.setText(str(alert_count))
        self._alert_value_lbl.setStyleSheet(f"color: {alert_color}; font-size: 38px; font-weight: bold;")
        self._alert_card.findChild(QLabel, "cardDesc").setText("个待处理" if alert_count > 0 else "一切正常")

        self._acad_value_lbl.setText(f"{result.academic}/100")

        for name, val in [("academic", result.academic), ("physical", result.physical),
                          ("mental", result.mental), ("social", result.social)]:
            color = "#059669" if val >= 80 else "#d97706" if val >= 60 else "#dc2626"
            self._dim_labels[name].setText(f"{val:.0f}")
            self._dim_labels[name].setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")

        self._alert_list.clear()
        alerts = self._risk_dao.get_by_student(self._student_id)
        for a in alerts[:10]:
            resolved = "[已解决]" if a.is_resolved else "[处理中]"
            self._alert_list.addItem(
                f"{resolved} [{a.alert_type}] {a.alert_message} - "
                f"{a.created_at.strftime('%m-%d %H:%M') if a.created_at else ''}"
            )
        if not alerts:
            self._alert_list.addItem("暂无风险告警，继续保持！")

    def refresh(self) -> None:
        # Auto-save a health assessment so health trend chart has data
        try:
            from business_layer.digital_twin import DigitalTwin
            dt = DigitalTwin(self._student_id, self._db)
            dt.save_assessment()
        except Exception:
            pass
        self._load_data()
