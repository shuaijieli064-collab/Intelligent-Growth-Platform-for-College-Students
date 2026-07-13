"""学习资源推荐页面."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QListWidget, QScrollArea, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO
from business_layer.resource_recommender import ResourceRecommender


class ResourceWidget(QWidget):
    TYPE_ICONS = {"video": "🎬", "exercise": "📝", "article": "📖", "course": "🎓"}

    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._recommender = ResourceRecommender(db, student_id)
        self._course_dao = CourseDAO(db)
        self._current_results: list[dict] = []
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

        title = QLabel("学习资源推荐")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("基于课程:"))
        self._course_combo = QComboBox()
        courses = self._course_dao.get_by_student(self._student_id)
        for c in courses:
            self._course_combo.addItem(c.course_name, c.course_id)
        ctrl_row.addWidget(self._course_combo)

        rec_btn = QPushButton("智能推荐")
        rec_btn.setObjectName("primaryBtn")
        rec_btn.clicked.connect(self._on_recommend)
        ctrl_row.addWidget(rec_btn)
        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        res_group = QGroupBox("推荐资源")
        res_layout = QVBoxLayout(res_group)
        self._resource_list = QListWidget()
        self._resource_list.itemDoubleClicked.connect(self._on_item_clicked)
        res_layout.addWidget(self._resource_list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        mark_btn = QPushButton("标记完成")
        mark_btn.setObjectName("successBtn")
        mark_btn.clicked.connect(self._on_mark_done)
        btn_row.addWidget(mark_btn)
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
        res_layout.addLayout(btn_row)
        layout.addWidget(res_group)

        layout.addStretch()
        scroll.setWidget(container)

    def _on_recommend(self) -> None:
        if self._course_combo.count() == 0:
            QMessageBox.information(self, "提示", "你还没有选课。请先在「数据录入 → 课程管理」中添加课程，或在「数据录入 → 成绩录入」中录入选课。")
            return
        course_id = self._course_combo.currentData()
        if not course_id:
            QMessageBox.information(self, "提示", "请先选择一门课程，再进行智能推荐。")
            return
        course_name = self._course_combo.currentText()
        self._current_results = self._recommender.recommend(course_id, course_name)
        self._show_results(self._current_results)

    def _show_results(self, results: list[dict]) -> None:
        self._resource_list.clear()
        for r in results:
            icon = self.TYPE_ICONS.get(r.get("type", r.get("resource_type", "")), "📌")
            done = "✅" if r.get("is_completed") else ""
            self._resource_list.addItem(
                f"{done} {icon} [{r.get('type', r.get('resource_type', ''))}] "
                f"{r.get('title', '')} | {r.get('kp_name', '综合')} | {r.get('reason', '')}"
            )

    def _on_item_clicked(self, item) -> None:
        idx = self._resource_list.currentRow()
        if 0 <= idx < len(self._current_results):
            url = self._current_results[idx].get("url", "")
            if url:
                QDesktopServices.openUrl(QUrl(url))

    def _current_id(self) -> int | None:
        idx = self._resource_list.currentRow()
        if 0 <= idx < len(self._current_results):
            return self._current_results[idx].get("id")
        return None

    def _on_mark_done(self) -> None:
        rid = self._current_id()
        if rid:
            self._recommender.mark_done(rid)
            self.refresh()

    def _on_delete(self) -> None:
        rid = self._current_id()
        if rid and QMessageBox.question(
            self, "确认", "确定要删除这条推荐吗？"
        ) == QMessageBox.Yes:
            self._recommender._dao.delete(rid)
            self.refresh()

    def _on_delete_all(self) -> None:
        recs = self._recommender.get_recommendations()
        if not recs:
            return
        if QMessageBox.question(self, "确认",
            f"确定删除全部 {len(recs)} 条推荐资源？"
        ) == QMessageBox.Yes:
            self._recommender._dao.delete_all_for_student(self._student_id)
            self._current_results = []
            self.refresh()

    def refresh(self) -> None:
        # Reload course list (student may have enrolled in new courses)
        current_cid = self._course_combo.currentData()
        self._course_combo.clear()
        for c in self._course_dao.get_by_student(self._student_id):
            self._course_combo.addItem(c.course_name, c.course_id)
        if current_cid:
            idx = self._course_combo.findData(current_cid)
            if idx >= 0:
                self._course_combo.setCurrentIndex(idx)
        # Reload recommendations
        recs = self._recommender.get_recommendations()
        self._current_results = recs
        self._show_results(recs)
