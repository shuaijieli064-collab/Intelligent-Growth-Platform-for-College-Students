"""风险预警页面."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QScrollArea,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from data_layer.database import DatabaseManager
from data_layer.dao.risk_dao import RiskDAO
from business_layer.risk_warning import RiskWarningSystem
from data_layer.models import RiskAlert


class RiskWarningWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._risk_dao = RiskDAO(db)
        self._warning_system = RiskWarningSystem(db)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("风险预警")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        # 控制栏
        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("筛选:"))
        self._filter_combo = QComboBox()
        self._filter_combo.addItem("全部", "all")
        self._filter_combo.addItem("未处理", "unresolved")
        self._filter_combo.addItem("学业", "学业")
        self._filter_combo.addItem("健康", "健康")
        self._filter_combo.addItem("心理", "心理")
        self._filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        ctrl_row.addWidget(self._filter_combo)

        ctrl_row.addStretch()

        refresh_btn = QPushButton("刷新评估")
        refresh_btn.setObjectName("primaryBtn")
        refresh_btn.clicked.connect(self._on_evaluate)
        ctrl_row.addWidget(refresh_btn)

        resolve_all_btn = QPushButton("全部处理")
        resolve_all_btn.setObjectName("successBtn")
        resolve_all_btn.clicked.connect(self._on_resolve_all)
        ctrl_row.addWidget(resolve_all_btn)

        delete_all_btn = QPushButton("全部删除")
        delete_all_btn.setObjectName("dangerBtn")
        delete_all_btn.clicked.connect(self._on_delete_all)
        ctrl_row.addWidget(delete_all_btn)

        layout.addLayout(ctrl_row)

        # 告警表格
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["时间", "类型", "风险等级", "告警内容", "触发规则", "操作"]
        )
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.setColumnWidth(0, 140)
        self._table.setColumnWidth(1, 80)
        self._table.setColumnWidth(2, 80)
        self._table.setColumnWidth(4, 140)
        self._table.setColumnWidth(5, 80)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table, 1)

    def _on_filter_changed(self) -> None:
        self.refresh()

    def _on_evaluate(self) -> None:
        self._warning_system.evaluate_and_save(self._student_id)
        self.refresh()

    def _on_resolve(self, alert_id: int) -> None:
        self._risk_dao.resolve(alert_id)
        self.refresh()

    def _on_delete(self, alert_id: int) -> None:
        self._risk_dao.delete(alert_id)
        self.refresh()

    def _on_resolve_all(self) -> None:
        from PyQt5.QtWidgets import QMessageBox
        alerts = self._risk_dao.get_by_student(self._student_id, unresolved_only=True)
        if not alerts:
            return
        if QMessageBox.question(self, "确认",
            f"确定处理全部 {len(alerts)} 条未解决的告警？"
        ) == QMessageBox.Yes:
            for a in alerts:
                self._risk_dao.resolve(a.alert_id)
            self.refresh()

    def _on_delete_all(self) -> None:
        from PyQt5.QtWidgets import QMessageBox
        alerts = self._risk_dao.get_by_student(self._student_id)
        if not alerts:
            return
        if QMessageBox.question(self, "确认",
            f"确定删除全部 {len(alerts)} 条告警？此操作不可撤销！"
        ) == QMessageBox.Yes:
            for a in alerts:
                self._risk_dao.delete(a.alert_id)
            self.refresh()

    def refresh(self) -> None:
        filter_val = self._filter_combo.currentData()
        alerts = self._risk_dao.get_by_student(self._student_id)

        # 过滤
        if filter_val == "unresolved":
            alerts = [a for a in alerts if not a.is_resolved]
        elif filter_val in ("学业", "健康", "心理"):
            alerts = [a for a in alerts if a.alert_type == filter_val]

        self._table.setRowCount(len(alerts))
        risk_colors = {"CRITICAL": "#ff4d4f", "HIGH": "#fa8c16",
                       "MEDIUM": "#faad14", "LOW": "#52c41a"}

        for i, alert in enumerate(alerts):
            # 时间
            self._table.setItem(i, 0, QTableWidgetItem(
                alert.created_at.strftime("%m-%d %H:%M") if alert.created_at else "-"
            ))

            # 类型
            self._table.setItem(i, 1, QTableWidgetItem(alert.alert_type))

            # 风险等级
            level_item = QTableWidgetItem(alert.risk_level)
            color = risk_colors.get(alert.risk_level, "#000000")
            level_item.setForeground(QColor(color))
            self._table.setItem(i, 2, level_item)

            # 告警内容
            self._table.setItem(i, 3, QTableWidgetItem(alert.alert_message))

            # 触发规则
            self._table.setItem(i, 4, QTableWidgetItem(alert.rule_triggered))

            # 操作按钮
            op_widget = QWidget()
            op_layout = QHBoxLayout(op_widget)
            op_layout.setContentsMargins(2, 2, 2, 2)
            op_layout.setSpacing(4)

            if not alert.is_resolved:
                resolve_btn = QPushButton("处理")
                resolve_btn.setObjectName("successBtn")
                resolve_btn.clicked.connect(
                    lambda checked, aid=alert.alert_id: self._on_resolve(aid)
                )
                op_layout.addWidget(resolve_btn)

            delete_btn = QPushButton("删除")
            delete_btn.setObjectName("dangerBtn")
            delete_btn.clicked.connect(
                lambda checked, aid=alert.alert_id: self._on_delete(aid)
            )
            op_layout.addWidget(delete_btn)
            self._table.setCellWidget(i, 5, op_widget)
