"""学习计划生成器页面."""
import json
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDoubleSpinBox, QDateEdit, QGroupBox,
    QListWidget, QProgressBar, QScrollArea, QMessageBox, QTextEdit,
)
from PyQt5.QtCore import QDate

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO
from business_layer.study_plan_generator import StudyPlanGenerator


class StudyPlanWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._generator = StudyPlanGenerator(db, student_id)
        self._course_dao = CourseDAO(db)
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

        title = QLabel("智能学习计划生成器")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        # 输入区
        input_group = QGroupBox("制定新计划")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("课程:"))
        self._course_combo = QComboBox()
        courses = self._course_dao.get_by_student(self._student_id)
        for c in courses:
            self._course_combo.addItem(c.course_name, c.course_id)
        r1.addWidget(self._course_combo)
        r1.addStretch()
        input_layout.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("目标分数:"))
        self._goal_spin = QDoubleSpinBox()
        self._goal_spin.setRange(60, 100); self._goal_spin.setValue(85)
        self._goal_spin.setDecimals(0); self._goal_spin.setSuffix(" 分")
        r2.addWidget(self._goal_spin)
        r2.addSpacing(20)
        r2.addWidget(QLabel("考试日期:"))
        self._exam_date = QDateEdit()
        self._exam_date.setDate(QDate.currentDate().addMonths(1))
        self._exam_date.setCalendarPopup(True)
        r2.addWidget(self._exam_date)
        r2.addStretch()
        input_layout.addLayout(r2)

        gen_btn = QPushButton("生成学习计划")
        gen_btn.setObjectName("primaryBtn")
        gen_btn.clicked.connect(self._on_generate)
        input_layout.addWidget(gen_btn)
        layout.addWidget(input_group)

        # 计划列表
        plans_group = QGroupBox("我的学习计划")
        plans_layout = QVBoxLayout(plans_group)
        self._plan_list = QListWidget()
        self._plan_list.currentRowChanged.connect(self._on_plan_selected)
        plans_layout.addWidget(self._plan_list)

        # 操作按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._progress_btn = QPushButton("完成下个任务")
        self._progress_btn.setObjectName("successBtn")
        self._progress_btn.clicked.connect(self._on_complete_task)
        btn_row.addWidget(self._progress_btn)

        self._complete_btn = QPushButton("全部完成")
        self._complete_btn.clicked.connect(self._on_complete)
        btn_row.addWidget(self._complete_btn)

        self._cancel_btn = QPushButton("取消计划")
        self._cancel_btn.clicked.connect(self._on_cancel)
        btn_row.addWidget(self._cancel_btn)

        self._delete_btn = QPushButton("删除")
        self._delete_btn.setObjectName("dangerBtn")
        self._delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(self._delete_btn)

        delete_all_btn = QPushButton("删除全部")
        delete_all_btn.setStyleSheet(
            "QPushButton { background-color: #dc2626; color: white; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-size: 18px; font-weight: bold; }"
        )
        delete_all_btn.clicked.connect(self._on_delete_all)
        btn_row.addWidget(delete_all_btn)

        btn_row.addStretch()
        plans_layout.addLayout(btn_row)
        layout.addWidget(plans_group)

        # 计划详情
        detail_group = QGroupBox("任务详情")
        detail_layout = QVBoxLayout(detail_group)
        self._detail_view = QTextEdit()
        self._detail_view.setReadOnly(True)
        self._detail_view.setMaximumHeight(200)
        detail_layout.addWidget(self._detail_view)
        layout.addWidget(detail_group)

        layout.addStretch()
        scroll.setWidget(container)

    def _current_plan_id(self) -> int | None:
        idx = self._plan_list.currentRow()
        plans = self._generator.get_plans()
        if 0 <= idx < len(plans):
            return plans[idx].get("id")
        return None

    def _on_generate(self) -> None:
        if self._course_combo.count() == 0:
            QMessageBox.information(self, "提示", "你还没有选课。请先在「数据录入 → 课程管理」中添加课程。")
            return
        course_id = self._course_combo.currentData()
        if not course_id:
            QMessageBox.information(self, "提示", "请先选择一门课程。")
            return
        subject = self._course_combo.currentText()
        goal = self._goal_spin.value()
        exam = self._exam_date.date().toPyDate()
        try:
            plan_id = self._generator.generate(subject, course_id, goal, exam)
            QMessageBox.information(self, "成功", f"学习计划已生成！")
            self.refresh()
            # 自动选中并显示新生成的计划
            plans = self._generator.get_plans()
            for i, p in enumerate(plans):
                if p.get("id") == plan_id:
                    self._plan_list.setCurrentRow(i)
                    break
        except Exception as e:
            QMessageBox.warning(self, "失败", f"生成失败: {e}")

    def _on_plan_selected(self) -> None:
        plans = self._generator.get_plans()
        idx = self._plan_list.currentRow()
        if 0 <= idx < len(plans):
            p = plans[idx]
            content = p.get("plan_content", [])
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    content = []

            done_count = sum(1 for t in (content or []) if isinstance(t, dict) and t.get("done"))
            total_count = len(content) if isinstance(content, list) else 1
            real_progress = int(done_count / max(1, total_count) * 100)

            lines = [f"📋 {p.get('subject', '')} | 目标: {p.get('goal_score', 0)}分 | "
                     f"进度: {done_count}/{total_count} 任务 ({real_progress}%) | 状态: {p.get('status', '')}"]
            lines.append("─" * 40)
            if isinstance(content, list):
                for task in content:
                    check = "✅" if task.get("done") else "⬜"
                    icon = {"review": "📖", "practice": "✏️", "mock_exam": "📝"}.get(
                        task.get("type", ""), "📌")
                    lines.append(
                        f"  {check} Day {task.get('day', '?'):>3}: {icon} {task.get('task', '')} "
                        f"({task.get('duration_min', 0)}min) [{task.get('priority', '')}]"
                    )
            self._detail_view.setText("\n".join(lines))

    def _on_complete_task(self) -> None:
        pid = self._current_plan_id()
        if not pid:
            return
        plans = self._generator.get_plans()
        idx = self._plan_list.currentRow()
        if 0 <= idx < len(plans):
            p = plans[idx]
            content = p.get("plan_content", [])
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    return
            if not isinstance(content, list) or not content:
                return
            # Find first undone task and mark it done
            found = False
            for task in content:
                if not task.get("done"):
                    task["done"] = True
                    found = True
                    break
            if not found:
                # All done — reset
                for task in content:
                    task["done"] = False
            # Calculate progress from actual task completion
            done_count = sum(1 for t in content if t.get("done"))
            progress = int(done_count / len(content) * 100)
            self._generator._dao.update_progress(pid, progress)
            # Update the plan_content JSON in DB
            import json as _json
            self._generator._dao._db.execute_update(
                "UPDATE study_plan SET plan_content = %s WHERE id = %s",
                (_json.dumps(content, ensure_ascii=False), pid),
            )
            self.refresh()
            self._on_plan_selected()

    def _on_complete(self) -> None:
        pid = self._current_plan_id()
        if pid:
            self._generator.complete_plan(pid)
            self.refresh()

    def _on_cancel(self) -> None:
        pid = self._current_plan_id()
        if pid:
            self._generator._dao.cancel(pid)
            self.refresh()

    def _on_delete(self) -> None:
        pid = self._current_plan_id()
        if pid and QMessageBox.question(
            self, "确认", "确定要删除这个计划吗？"
        ) == QMessageBox.Yes:
            self._generator._dao.delete(pid)
            self.refresh()

    def _on_delete_all(self) -> None:
        plans = self._generator.get_plans()
        if not plans:
            return
        if QMessageBox.question(self, "确认",
            f"确定删除全部 {len(plans)} 个学习计划？此操作不可撤销！"
        ) == QMessageBox.Yes:
            self._generator._dao.delete_all_for_student(self._student_id)
            self._detail_view.clear()
            self.refresh()

    def refresh(self) -> None:
        # 重建业务对象，避免切换学生后仍读写旧学生的计划
        self._generator = StudyPlanGenerator(self._db, self._student_id)
        # Reload course combo
        current_cid = self._course_combo.currentData()
        self._course_combo.clear()
        for c in self._course_dao.get_by_student(self._student_id):
            self._course_combo.addItem(c.course_name, c.course_id)
        if current_cid:
            idx = self._course_combo.findData(current_cid)
            if idx >= 0:
                self._course_combo.setCurrentIndex(idx)
        # Reload plan list
        self._plan_list.clear()
        self._detail_view.clear()
        plans = self._generator.get_plans()
        for p in plans:
            status = p.get("status", "")
            progress = p.get("progress", 0)
            content = p.get("plan_content", [])
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    content = []
            tasks_count = len(content) if isinstance(content, list) else 0
            icon = "✅" if status == "completed" else "🚫" if status == "cancelled" else "📋"
            self._plan_list.addItem(
                f"{icon} {p.get('subject', '')} | 目标 {p.get('goal_score', 0)}分 | "
                f"进度 {progress}% | {tasks_count} 个任务 | "
                f"{str(p.get('created_at', ''))[:19]}"
            )
