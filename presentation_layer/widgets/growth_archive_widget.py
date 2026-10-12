"""成长档案页面."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QTextEdit, QListWidget, QScrollArea, QMessageBox,
)
from PyQt5.QtCore import Qt

from data_layer.database import DatabaseManager
from business_layer.growth_archiver import GrowthArchiver


class GrowthArchiveWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._archiver = GrowthArchiver(db, student_id)
        self._setup_ui()

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

        title = QLabel("成长档案")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        # 生成按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        week_btn = QPushButton("生成周报")
        week_btn.setObjectName("primaryBtn")
        week_btn.clicked.connect(lambda: self._on_generate("weekly"))
        btn_row.addWidget(week_btn)

        month_btn = QPushButton("生成月报")
        month_btn.setObjectName("primaryBtn")
        month_btn.clicked.connect(lambda: self._on_generate("monthly"))
        btn_row.addWidget(month_btn)

        sem_btn = QPushButton("生成学期报告")
        sem_btn.setObjectName("successBtn")
        sem_btn.clicked.connect(lambda: self._on_generate("semester"))
        btn_row.addWidget(sem_btn)

        delete_btn = QPushButton("删除选中")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(delete_btn)

        delete_all_btn = QPushButton("删除全部")
        delete_all_btn.setStyleSheet(
            "QPushButton { background-color: #dc2626; color: white; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-size: 18px; font-weight: bold; }"
        )
        delete_all_btn.clicked.connect(self._on_delete_all)
        btn_row.addWidget(delete_all_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # 报告列表
        list_group = QGroupBox("历史报告")
        list_layout = QVBoxLayout(list_group)
        self._report_list = QListWidget()
        self._report_list.itemClicked.connect(self._on_report_selected)
        list_layout.addWidget(self._report_list)
        layout.addWidget(list_group, 1)

        # 报告详情
        detail_group = QGroupBox("报告详情")
        detail_layout = QVBoxLayout(detail_group)
        self._detail_view = QTextEdit()
        self._detail_view.setReadOnly(True)
        self._detail_view.setMaximumHeight(250)
        detail_layout.addWidget(self._detail_view)
        layout.addWidget(detail_group)

        layout.addStretch()
        scroll.setWidget(container)

    def _on_generate(self, report_type: str) -> None:
        try:
            if report_type == "weekly":
                rid = self._archiver.generate_weekly()
            elif report_type == "monthly":
                rid = self._archiver.generate_monthly()
            else:
                rid = self._archiver.generate_semester()
            QMessageBox.information(self, "成功", f"报告已生成 (ID: {rid})")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "失败", f"生成失败: {e}")

    def _on_delete(self) -> None:
        reports = self._archiver.get_reports()
        idx = self._report_list.currentRow()
        if 0 <= idx < len(reports):
            rid = reports[idx]["id"]
            if QMessageBox.question(self, "确认", f"删除报告 #{rid}？") == QMessageBox.Yes:
                self._archiver._dao.delete(rid)
                self.refresh()

    def _on_delete_all(self) -> None:
        reports = self._archiver.get_reports()
        if not reports:
            return
        if QMessageBox.question(self, "确认",
            f"确定删除全部 {len(reports)} 份成长报告？此操作不可撤销！"
        ) == QMessageBox.Yes:
            for r in reports:
                self._archiver._dao.delete(r["id"])
            self.refresh()

    def _on_report_selected(self) -> None:
        reports = self._archiver.get_reports()
        idx = self._report_list.currentRow()
        if 0 <= idx < len(reports):
            r = reports[idx]
            detail = r.get("detail", {})
            if isinstance(detail, str):
                import json
                try:
                    detail = json.loads(detail)
                except json.JSONDecodeError:
                    detail = {}

            text = f"""
            📅 类型: {r.get('report_type', '')} 报告
            📊 健康度: {r.get('health_score', 0)}/100 | 风险: {r.get('risk_level', 'N/A')}
            📆 周期: {r.get('period_start', '')} ~ {r.get('period_end', '')}
            ────────────────────────────
            📝 {r.get('summary', '暂无摘要')}
            """
            self._detail_view.setText(text)

    def refresh(self) -> None:
        # Rebuild archiver so generate/list/delete act on the current student
        self._archiver = GrowthArchiver(self._db, self._student_id)
        self._report_list.clear()
        self._detail_view.clear()
        reports = self._archiver.get_reports()
        type_names = {"weekly": "周报", "monthly": "月报", "semester": "学期报告"}
        for r in reports:
            tname = type_names.get(r.get("report_type", ""), r.get("report_type", ""))
            self._report_list.addItem(
                f"[{tname}] {str(r.get('report_date', ''))} | "
                f"健康: {r.get('health_score', 0):.0f} | {r.get('summary', '')[:50]}"
            )
