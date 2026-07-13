"""主窗口 - 侧边栏导航 + QStackedWidget 多页面 + 主题切换."""
from __future__ import annotations

import json
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget, QLabel, QStatusBar, QListWidgetItem,
    QComboBox, QPushButton,
)
from PyQt5.QtCore import Qt

from data_layer.database import DatabaseManager
from data_layer.dao.student_dao import StudentDAO
from presentation_layer.styles import (
    get_qss, get_theme, get_theme_color, set_theme, toggle_theme,
    apply_theme,
)
from presentation_layer.widgets.dashboard_widget import DashboardWidget
from presentation_layer.widgets.digital_twin_widget import DigitalTwinWidget
from presentation_layer.widgets.grade_predict_widget import GradePredictWidget
from presentation_layer.widgets.knowledge_graph_widget import KnowledgeGraphWidget
from presentation_layer.widgets.ai_coach_widget import AICoachWidget
from presentation_layer.widgets.risk_warning_widget import RiskWarningWidget
from presentation_layer.widgets.visualization_widget import VisualizationWidget
from presentation_layer.widgets.study_plan_widget import StudyPlanWidget
from presentation_layer.widgets.resource_widget import ResourceWidget
from presentation_layer.widgets.focus_monitor_widget import FocusMonitorWidget
from presentation_layer.widgets.growth_archive_widget import GrowthArchiveWidget
from presentation_layer.widgets.data_entry_widget import DataEntryWidget

THEME_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def _load_saved_theme() -> str:
    try:
        if THEME_CONFIG_PATH.exists():
            data = json.loads(THEME_CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("theme", "light")
    except Exception:
        pass
    return "light"


def _save_theme(theme: str) -> None:
    try:
        data = {}
        if THEME_CONFIG_PATH.exists():
            data = json.loads(THEME_CONFIG_PATH.read_text(encoding="utf-8"))
        data["theme"] = theme
        THEME_CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


class MainWindow(QMainWindow):
    NAV_ITEMS = [
        ("数据录入", "📝"),
        ("首页仪表盘", "🏠"),
        ("数字孪生", "👤"),
        ("成绩预测", "📊"),
        ("知识图谱", "🧠"),
        ("AI 学习教练", "🤖"),
        ("风险预警", "⚠"),
        ("学习计划", "📋"),
        ("资源推荐", "💡"),
        ("专注度监测", "🎯"),
        ("成长档案", "📁"),
        ("数据可视化", "📈"),
    ]

    def __init__(self, db: DatabaseManager) -> None:
        super().__init__()
        self._db = db
        self._student_dao = StudentDAO(db)
        self._current_student_id = 1

        # Load saved theme
        saved_theme = _load_saved_theme()
        set_theme(saved_theme)

        self._init_student()
        self.setWindowTitle("大学生智能成长平台")
        self.resize(1280, 860)
        self.setMinimumSize(1080, 720)
        self.setStyleSheet(get_qss())
        self._setup_ui()
        self._populate_pages()
        self._setup_status_bar()

    def _init_student(self) -> None:
        students = self._student_dao.get_all()
        if students:
            self._current_student_id = students[0].student_id
            self._current_student = students[0]
        else:
            self._current_student = None

    def _populate_student_combo(self) -> None:
        self._student_combo.blockSignals(True)
        self._student_combo.clear()
        students = self._student_dao.get_all()
        for s in students:
            self._student_combo.addItem(f"{s.name} ({s.student_no})", s.student_id)
        idx = self._student_combo.findData(self._current_student_id)
        if idx >= 0:
            self._student_combo.setCurrentIndex(idx)
        self._student_combo.blockSignals(False)

    def _on_student_changed(self) -> None:
        student_id = self._student_combo.currentData()
        if student_id is not None and student_id != self._current_student_id:
            self.switch_student(student_id)

    def _setup_ui(self) -> None:
        c = get_theme_color
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 侧边栏
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(230)
        sidebar_widget.setStyleSheet(f"background-color: {c('bg_sidebar')};")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        title = QLabel("🎓 智能成长平台")
        title.setObjectName("appTitle")
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)

        student_label = QLabel("选择学生")
        student_label.setStyleSheet(
            f"color: {c('text_muted')}; font-size: 16px; font-weight: 600; "
            "letter-spacing: 0.8px; padding: 10px 20px 4px 20px; text-transform: uppercase;"
        )
        sidebar_layout.addWidget(student_label)

        self._student_combo = QComboBox()
        self._student_combo.setStyleSheet(
            "QComboBox {"
            f"  background-color: {c('bg_input')}; color: {c('text_primary')}; "
            f"  border: 1px solid {c('border_focus')};"
            "  border-radius: 8px; padding: 6px 14px; font-size: 18px; margin: 0 16px 10px 16px;"
            "}"
            "QComboBox::drop-down { border: none; padding-right: 6px; }"
            "QComboBox QAbstractItemView {"
            f"  background-color: {c('bg_input')}; color: {c('text_primary')}; "
            f"  border: 1px solid {c('border_focus')};"
            f"  selection-background-color: {c('selection_bg')}; font-size: 18px;"
            "}"
        )
        self._populate_student_combo()
        self._student_combo.currentIndexChanged.connect(self._on_student_changed)
        sidebar_layout.addWidget(self._student_combo)

        self._sidebar = QListWidget()
        self._sidebar.setObjectName("sidebar")
        for name, icon in self.NAV_ITEMS:
            item = QListWidgetItem(f"  {icon}  {name}")
            item.setSizeHint(item.sizeHint())
            self._sidebar.addItem(item)
        self._sidebar.setCurrentRow(0)
        self._sidebar.currentRowChanged.connect(self._switch_page)
        sidebar_layout.addWidget(self._sidebar)
        sidebar_layout.addStretch()

        # 主题切换按钮
        self._theme_btn = QPushButton()
        self._update_theme_button_text()
        self._theme_btn.setCursor(Qt.PointingHandCursor)
        self._theme_btn.clicked.connect(self._toggle_theme)
        self._theme_btn.setStyleSheet(
            "QPushButton {"
            f"  background-color: transparent; color: {c('text_secondary')}; "
            "  border: none; border-radius: 8px; padding: 10px 16px; font-size: 16px;"
            "  margin: 4px 12px;"
            "}"
            f"QPushButton:hover {{ background-color: {c('accent_light')}; }}"
        )
        sidebar_layout.addWidget(self._theme_btn)

        layout.addWidget(sidebar_widget)

        # 内容区
        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

    def _update_theme_button_text(self) -> None:
        current = get_theme()
        if current == "dark":
            self._theme_btn.setText("☀️  浅色模式")
        else:
            self._theme_btn.setText("🌙  暗色模式")

    def _update_sidebar_colors(self) -> None:
        c = get_theme_color
        # Update sidebar inline styles
        sidebar = self._theme_btn.parent()
        if sidebar:
            sidebar.setStyleSheet(f"background-color: {c('bg_sidebar')};")
        self._student_combo.setStyleSheet(
            "QComboBox {"
            f"  background-color: {c('bg_input')}; color: {c('text_primary')}; "
            f"  border: 1px solid {c('border_focus')};"
            "  border-radius: 8px; padding: 6px 14px; font-size: 18px; margin: 0 16px 10px 16px;"
            "}"
            "QComboBox::drop-down { border: none; padding-right: 6px; }"
            "QComboBox QAbstractItemView {"
            f"  background-color: {c('bg_input')}; color: {c('text_primary')}; "
            f"  border: 1px solid {c('border_focus')};"
            f"  selection-background-color: {c('selection_bg')}; font-size: 18px;"
            "}"
        )
        self._theme_btn.setStyleSheet(
            "QPushButton {"
            f"  background-color: transparent; color: {c('text_secondary')}; "
            "  border: none; border-radius: 8px; padding: 10px 16px; font-size: 16px;"
            "  margin: 4px 12px;"
            "}"
            f"QPushButton:hover {{ background-color: {c('accent_light')}; }}"
        )

    def _toggle_theme(self) -> None:
        new_theme = toggle_theme()
        apply_theme(self, new_theme)
        _save_theme(new_theme)
        self._update_theme_button_text()
        self._update_sidebar_colors()
        self.refresh_all()

    def _setup_status_bar(self) -> None:
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._update_status()

    def _update_status(self) -> None:
        if self._current_student:
            s = self._current_student
            self._status.showMessage(
                f"当前学生: {s.name} | 学号: {s.student_no} | "
                f"专业: {s.major} | {s.grade_level}"
            )

    def _on_student_data_changed(self) -> None:
        self._current_student = self._student_dao.get_by_id(self._current_student_id)
        self._populate_student_combo()
        self._update_status()

    def switch_student(self, student_id: int) -> None:
        s = self._student_dao.get_by_id(student_id)
        if s:
            self._current_student_id = student_id
            self._current_student = s
            self._update_status()
            self._sync_student_combo()
            self.refresh_all()

    def _sync_student_combo(self) -> None:
        idx = self._student_combo.findData(self._current_student_id)
        if idx >= 0:
            self._student_combo.blockSignals(True)
            self._student_combo.setCurrentIndex(idx)
            self._student_combo.blockSignals(False)

    def _populate_pages(self) -> None:
        sid = self._current_student_id
        self._stack.addWidget(DataEntryWidget(self._db, sid, on_student_updated=self._on_student_data_changed))
        self._stack.addWidget(DashboardWidget(self._db, sid))
        self._stack.addWidget(DigitalTwinWidget(self._db, sid))
        self._stack.addWidget(GradePredictWidget(self._db, sid))
        self._stack.addWidget(KnowledgeGraphWidget(self._db, sid))
        self._stack.addWidget(AICoachWidget(self._db, sid))
        self._stack.addWidget(RiskWarningWidget(self._db, sid))
        self._stack.addWidget(StudyPlanWidget(self._db, sid))
        self._stack.addWidget(ResourceWidget(self._db, sid))
        self._stack.addWidget(FocusMonitorWidget(self._db, sid))
        self._stack.addWidget(GrowthArchiveWidget(self._db, sid))
        self._stack.addWidget(VisualizationWidget(self._db, sid))

    def _switch_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        widget = self._stack.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def refresh_all(self) -> None:
        for i in range(self._stack.count()):
            widget = self._stack.widget(i)
            widget._student_id = self._current_student_id
            if hasattr(widget, "refresh"):
                widget.refresh()
            # Also refresh chart canvases
            if hasattr(widget, "_chart_canvas"):
                widget._chart_canvas.refresh_theme()
            if hasattr(widget, "_heat_canvas"):
                widget._heat_canvas.refresh_theme()
