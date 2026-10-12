"""数据录入页面 - 录入/查看/删除学习记录、成绩、个人信息."""
from datetime import date
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit,
    QGroupBox, QTabWidget, QTextEdit, QScrollArea, QMessageBox,
    QFormLayout, QListWidget,
)

from data_layer.database import DatabaseManager
from data_layer.dao.student_dao import StudentDAO
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.health_dao import HealthDAO
from data_layer.models import PhysicalHealthRecord, MentalHealthRecord, SocialHealthRecord


class DataEntryWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None, on_student_updated=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._student_dao = StudentDAO(db)
        self._course_dao = CourseDAO(db)
        self._score_dao = StudentCourseDAO(db)
        self._study_dao = StudyRecordDAO(db)
        self._health_dao = HealthDAO(db)
        self._on_student_updated = on_student_updated
        self._setup_ui()
        self._load_student_info()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("📝 数据录入与管理")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._create_study_tab(), "📝 学习记录")
        self._tabs.addTab(self._create_score_tab(), "📊 成绩录入")
        self._tabs.addTab(self._create_physical_tab(), "🏃 身体健康")
        self._tabs.addTab(self._create_mental_tab(), "🧠 心理健康")
        self._tabs.addTab(self._create_social_tab(), "🤝 社交健康")
        self._tabs.addTab(self._create_profile_tab(), "👤 个人信息")
        self._tabs.addTab(self._create_course_tab(), "📚 课程管理")
        layout.addWidget(self._tabs)

    # ── Tab 1: 学习记录 ──────────────────────────────────────
    def _create_study_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self._study_date = QDateEdit(); self._study_date.setDate(QDate.currentDate())
        self._study_date.setCalendarPopup(True)
        form.addRow("日期:", self._study_date)

        self._study_course = QComboBox()
        self._study_course.addItem("（无特定课程）", None)
        for c in self._course_dao.get_by_student(self._student_id):
            self._study_course.addItem(c.course_name, c.course_id)
        form.addRow("课程:", self._study_course)

        self._study_hours = QDoubleSpinBox()
        self._study_hours.setRange(0, 24); self._study_hours.setValue(2.0)
        self._study_hours.setSingleStep(0.5); self._study_hours.setSuffix(" 小时")
        form.addRow("学习时长:", self._study_hours)

        self._study_focus = QSpinBox()
        self._study_focus.setRange(0, 100); self._study_focus.setValue(70)
        self._study_focus.setSuffix(" 分")
        form.addRow("专注度自评:", self._study_focus)

        self._study_tasks = QSpinBox()
        self._study_tasks.setRange(0, 50); self._study_tasks.setValue(3)
        self._study_tasks.setSuffix(" 项")
        form.addRow("完成任务:", self._study_tasks)

        self._study_notes = QTextEdit()
        self._study_notes.setMaximumHeight(60)
        self._study_notes.setPlaceholderText("今天学了什么内容？有什么收获？")
        form.addRow("备注:", self._study_notes)

        layout.addLayout(form)

        btn = QPushButton("✅ 记录今天的学习")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._on_add_record)
        layout.addWidget(btn)

        self._record_msg = QLabel("")
        self._record_msg.setStyleSheet("color: #059669; font-size: 18px;")
        layout.addWidget(self._record_msg)

        # 历史记录列表
        hist_group = QGroupBox("最近学习记录（点击选中后可删除）")
        hist_layout = QVBoxLayout(hist_group)
        self._record_list = QListWidget()
        hist_layout.addWidget(self._record_list)

        del_row = QHBoxLayout()
        self._delete_record_btn = QPushButton("🗑 删除选中")
        self._delete_record_btn.setObjectName("dangerBtn")
        self._delete_record_btn.clicked.connect(self._on_delete_record)
        del_row.addWidget(self._delete_record_btn)

        delete_all_btn = QPushButton("🗑 删除全部记录")
        delete_all_btn.setStyleSheet(
            "QPushButton { background-color: #dc2626; color: white; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-size: 18px; font-weight: bold; }"
            "QPushButton:hover { background-color: #e11d48; }"
        )
        delete_all_btn.clicked.connect(self._on_delete_all_records)
        del_row.addWidget(delete_all_btn)
        del_row.addStretch()
        hist_layout.addLayout(del_row)
        layout.addWidget(hist_group)

        self._load_record_list()
        return w

    def _on_add_record(self) -> None:
        try:
            cid = self._study_course.currentData()
            d = self._study_date.date().toPyDate()
            h = self._study_hours.value()
            f = self._study_focus.value()
            t = self._study_tasks.value()
            n = self._study_notes.toPlainText().strip() or None
            rid = self._study_dao.add_record(self._student_id, d, h, cid, t, f, n)
            self._record_msg.setText(f"✅ 已记录！(ID:{rid})  {h}h 专注度{f}")
            self._load_record_list()
            self._refresh_health_assessment()
        except Exception as e:
            self._record_msg.setText(f"❌ {e}")

    def _load_record_list(self) -> None:
        self._record_list.clear()
        records = self._study_dao.get_all_by_student(self._student_id)
        for r in records[:30]:
            notes = r.get("notes") or ""
            self._record_list.addItem(
                f"[{str(r['study_date'])}] {r['study_hours']}h | "
                f"专注:{r.get('focus_score','-')} | 任务:{r.get('task_completed',0)} | "
                f"{notes[:30]}"
            )

    def _on_delete_record(self) -> None:
        records = self._study_dao.get_all_by_student(self._student_id)
        idx = self._record_list.currentRow()
        if 0 <= idx < len(records):
            rid = records[idx]["record_id"]
            if QMessageBox.question(self, "确认", f"删除记录 #{rid}？") == QMessageBox.Yes:
                self._study_dao.delete(rid)
                self._load_record_list()

    def _on_delete_all_records(self) -> None:
        records = self._study_dao.get_all_by_student(self._student_id)
        if not records:
            return
        if QMessageBox.question(self, "确认", f"确定删除全部 {len(records)} 条学习记录？此操作不可撤销！") == QMessageBox.Yes:
            for r in records:
                self._study_dao.delete(r["record_id"])
            self._load_record_list()

    # ── Tab 2: 成绩录入 ──────────────────────────────────────
    def _create_score_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        form = QFormLayout(); form.setSpacing(10)

        self._score_course = QComboBox()
        for c in self._course_dao.get_by_student(self._student_id):
            self._score_course.addItem(c.course_name, c.course_id)
        form.addRow("课程:", self._score_course)
        self._score_usual = QDoubleSpinBox()
        self._score_usual.setRange(0, 100); self._score_usual.setDecimals(1)
        self._score_usual.setValue(75); self._score_usual.setSuffix(" 分")
        form.addRow("平时成绩:", self._score_usual)
        self._score_midterm = QDoubleSpinBox()
        self._score_midterm.setRange(0, 100); self._score_midterm.setDecimals(1)
        self._score_midterm.setValue(70); self._score_midterm.setSuffix(" 分")
        form.addRow("期中成绩:", self._score_midterm)
        self._score_final = QDoubleSpinBox()
        self._score_final.setRange(0, 100); self._score_final.setDecimals(1)
        self._score_final.setValue(0); self._score_final.setSuffix(" 分")
        self._score_final.setSpecialValueText("（未参加）")
        self._score_final.setEnabled(False)
        form.addRow("期末成绩:", self._score_final)

        from PyQt5.QtWidgets import QCheckBox
        self._final_check = QCheckBox("已参加期末考试")
        self._final_check.setChecked(False)
        self._final_check.toggled.connect(lambda checked: self._score_final.setEnabled(checked))
        form.addRow("", self._final_check)
        layout.addLayout(form)

        save_btn = QPushButton("💾 保存成绩")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._on_save_score)
        layout.addWidget(save_btn)

        self._score_msg = QLabel("")
        self._score_msg.setStyleSheet("color: #059669; font-size: 18px;")
        layout.addWidget(self._score_msg)

        # 历史成绩
        score_hist_group = QGroupBox("已录成绩（选中后可删除）")
        score_hist_layout = QVBoxLayout(score_hist_group)
        self._score_history = QListWidget()
        score_hist_layout.addWidget(self._score_history)
        score_del_btn = QPushButton("🗑 删除选中成绩")
        score_del_btn.setObjectName("dangerBtn")
        score_del_btn.clicked.connect(self._on_delete_score)
        score_hist_layout.addWidget(score_del_btn)
        layout.addWidget(score_hist_group)
        self._load_score_history()

        layout.addStretch()
        return w

    def _on_save_score(self) -> None:
        try:
            cid = self._score_course.currentData()
            if not cid:
                QMessageBox.information(self, "提示", "请先选择课程。")
                return
            usual = self._score_usual.value()
            midterm = self._score_midterm.value()
            final = self._score_final.value() if self._final_check.isChecked() else None
            self._score_dao.update_scores(self._student_id, cid, usual, midterm, final)
            self._score_msg.setText(f"✅ 保存成功！平时:{usual} 期中:{midterm}" +
                                    (f" 期末:{final}" if final else " 期末:未参加"))
            self._load_score_history()
        except Exception as e:
            self._score_msg.setText(f"❌ {e}")

    def _load_score_history(self) -> None:
        self._score_history.clear()
        scores = self._score_dao.get_student_scores(self._student_id)
        for s in scores:
            us = s.get("usual_score", "-")
            ms = s.get("midterm_score", "-")
            fs = s.get("final_score", "未考")
            self._score_history.addItem(
                f"[{s.get('course_name', '')}] 平时:{us} 期中:{ms} 期末:{fs}"
            )

    def _on_delete_score(self) -> None:
        scores = self._score_dao.get_student_scores(self._student_id)
        idx = self._score_history.currentRow()
        if 0 <= idx < len(scores):
            s = scores[idx]
            course_name = s.get("course_name", "")
            sc_id = s.get("id")
            if sc_id and QMessageBox.question(self, "确认",
                f"删除「{course_name}」的成绩记录？") == QMessageBox.Yes:
                self._score_dao.delete_score(sc_id)
                self._load_score_history()

    # ── Tab 3: 身体健康 ──────────────────────────────────────
    def _create_physical_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        form = QFormLayout(); form.setSpacing(10)

        self._phy_date = QDateEdit(); self._phy_date.setDate(QDate.currentDate())
        self._phy_date.setCalendarPopup(True)
        form.addRow("日期:", self._phy_date)

        self._phy_exercise_type = QComboBox()
        self._phy_exercise_type.addItems(["跑步", "球类", "健身", "瑜伽", "游泳", "骑行", "步行", "其他"])
        self._phy_exercise_type.currentTextChanged.connect(self._on_exercise_type_changed)
        form.addRow("运动类型:", self._phy_exercise_type)

        self._phy_duration = QSpinBox()
        self._phy_duration.setRange(0, 480); self._phy_duration.setValue(30)
        self._phy_duration.setSuffix(" 分钟")
        form.addRow("运动时长:", self._phy_duration)

        self._phy_sleep = QDoubleSpinBox()
        self._phy_sleep.setRange(0, 24); self._phy_sleep.setValue(7.0)
        self._phy_sleep.setSingleStep(0.5); self._phy_sleep.setSuffix(" 小时")
        form.addRow("睡眠时长:", self._phy_sleep)

        self._phy_steps_label = QLabel("步数:")
        self._phy_steps = QSpinBox()
        self._phy_steps.setRange(0, 100000); self._phy_steps.setValue(5000)
        self._phy_steps.setSingleStep(500)
        form.addRow(self._phy_steps_label, self._phy_steps)

        layout.addLayout(form)

        btn = QPushButton("✅ 保存身体健康记录")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._on_save_physical)
        layout.addWidget(btn)

        self._phy_msg = QLabel("")
        self._phy_msg.setStyleSheet("color: #059669; font-size: 18px;")
        layout.addWidget(self._phy_msg)

        self._phy_history = QListWidget()
        self._phy_history.setMaximumHeight(150)
        layout.addWidget(QLabel("最近记录（选中后可删除）:"))
        layout.addWidget(self._phy_history)
        phy_del_row = QHBoxLayout()
        self._phy_del_btn = QPushButton("🗑 删除选中的身体健康记录")
        self._phy_del_btn.setObjectName("dangerBtn")
        self._phy_del_btn.clicked.connect(self._on_delete_physical)
        phy_del_row.addWidget(self._phy_del_btn)
        phy_del_row.addStretch()
        layout.addLayout(phy_del_row)
        layout.addStretch()
        return w

    def _on_save_physical(self) -> None:
        try:
            r = PhysicalHealthRecord(
                student_id=self._student_id,
                record_date=self._phy_date.date().toPyDate(),
                exercise_type=self._phy_exercise_type.currentText(),
                exercise_duration=self._phy_duration.value(),
                sleep_hours=self._phy_sleep.value(),
                steps=self._phy_steps.value(),
            )
            rid = self._health_dao.save_physical_record(r)
            self._phy_msg.setText(f"✅ 已保存 (ID:{rid})")
            self._load_physical_history()
            self._refresh_health_assessment()
        except Exception as e:
            self._phy_msg.setText(f"❌ {e}")

    def _on_exercise_type_changed(self, exercise_type: str) -> None:
        """Hide steps field for non-step-based exercises (swimming, yoga, etc.)."""
        no_steps = exercise_type in ("游泳", "瑜伽", "健身")
        self._phy_steps_label.setVisible(not no_steps)
        self._phy_steps.setVisible(not no_steps)

    def _load_physical_history(self) -> None:
        self._phy_history.clear()
        records = self._health_dao.get_physical_records(self._student_id, days=30)
        for r in records[:20]:
            self._phy_history.addItem(
                f"[{r['record_date']}] {r['exercise_type']} {r['exercise_duration']}min "
                f"| 睡眠:{r['sleep_hours']}h | 步数:{r['steps']}"
            )

    # ── Tab 4: 心理健康 ──────────────────────────────────────
    def _create_mental_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        form = QFormLayout(); form.setSpacing(10)

        self._men_date = QDateEdit(); self._men_date.setDate(QDate.currentDate())
        self._men_date.setCalendarPopup(True)
        form.addRow("日期:", self._men_date)

        self._men_mood = QSpinBox()
        self._men_mood.setRange(1, 10); self._men_mood.setValue(7)
        self._men_mood.setSuffix(" 分")
        form.addRow("心情评分(1-10):", self._men_mood)

        self._men_stress = QSpinBox()
        self._men_stress.setRange(1, 5); self._men_stress.setValue(2)
        self._men_stress.setSuffix(" 级")
        form.addRow("压力等级(1-5):", self._men_stress)

        self._men_anxiety = QSpinBox()
        self._men_anxiety.setRange(1, 5); self._men_anxiety.setValue(2)
        self._men_anxiety.setSuffix(" 级")
        form.addRow("焦虑等级(1-5):", self._men_anxiety)

        self._men_notes = QTextEdit()
        self._men_notes.setMaximumHeight(80)
        self._men_notes.setPlaceholderText("今天的感受如何？有什么想记录的？")
        form.addRow("心情日记:", self._men_notes)

        layout.addLayout(form)

        btn = QPushButton("✅ 保存心理健康记录")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._on_save_mental)
        layout.addWidget(btn)

        self._men_msg = QLabel("")
        self._men_msg.setStyleSheet("color: #059669; font-size: 18px;")
        layout.addWidget(self._men_msg)

        self._men_history = QListWidget()
        self._men_history.setMaximumHeight(150)
        layout.addWidget(QLabel("最近记录（选中后可删除）:"))
        layout.addWidget(self._men_history)
        men_del_row = QHBoxLayout()
        self._men_del_btn = QPushButton("🗑 删除选中的心理健康记录")
        self._men_del_btn.setObjectName("dangerBtn")
        self._men_del_btn.clicked.connect(self._on_delete_mental)
        men_del_row.addWidget(self._men_del_btn)
        men_del_row.addStretch()
        layout.addLayout(men_del_row)
        layout.addStretch()
        return w

    def _on_save_mental(self) -> None:
        try:
            r = MentalHealthRecord(
                student_id=self._student_id,
                record_date=self._men_date.date().toPyDate(),
                mood_score=self._men_mood.value(),
                stress_level=self._men_stress.value(),
                anxiety_level=self._men_anxiety.value(),
                notes=self._men_notes.toPlainText().strip() or None,
            )
            rid = self._health_dao.save_mental_record(r)
            self._men_msg.setText(f"✅ 已保存 (ID:{rid})")
            self._load_mental_history()
            self._refresh_health_assessment()
        except Exception as e:
            self._men_msg.setText(f"❌ {e}")

    def _load_mental_history(self) -> None:
        self._men_history.clear()
        records = self._health_dao.get_mental_records(self._student_id, days=30)
        for r in records[:20]:
            notes = r.get("notes") or ""
            self._men_history.addItem(
                f"[{r['record_date']}] 心情:{r['mood_score']}/10 "
                f"压力:{r['stress_level']}/5 焦虑:{r['anxiety_level']}/5"
                + (f" | {notes[:20]}" if notes else "")
            )

    # ── Tab 5: 社交健康 ──────────────────────────────────────
    def _create_social_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        form = QFormLayout(); form.setSpacing(10)

        self._soc_date = QDateEdit(); self._soc_date.setDate(QDate.currentDate())
        self._soc_date.setCalendarPopup(True)
        form.addRow("日期:", self._soc_date)

        self._soc_activity_type = QComboBox()
        self._soc_activity_type.addItems(["社团活动", "朋友聚会", "团队项目", "志愿服务", "学术交流", "其他"])
        form.addRow("活动类型:", self._soc_activity_type)

        self._soc_duration = QSpinBox()
        self._soc_duration.setRange(0, 600); self._soc_duration.setValue(60)
        self._soc_duration.setSuffix(" 分钟")
        form.addRow("活动时长:", self._soc_duration)

        self._soc_interactions = QSpinBox()
        self._soc_interactions.setRange(0, 100); self._soc_interactions.setValue(3)
        self._soc_interactions.setSuffix(" 人")
        form.addRow("互动人数:", self._soc_interactions)

        layout.addLayout(form)

        btn = QPushButton("✅ 保存社交健康记录")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._on_save_social)
        layout.addWidget(btn)

        self._soc_msg = QLabel("")
        self._soc_msg.setStyleSheet("color: #059669; font-size: 18px;")
        layout.addWidget(self._soc_msg)

        self._soc_history = QListWidget()
        self._soc_history.setMaximumHeight(150)
        layout.addWidget(QLabel("最近记录（选中后可删除）:"))
        layout.addWidget(self._soc_history)
        soc_del_row = QHBoxLayout()
        self._soc_del_btn = QPushButton("🗑 删除选中的社交健康记录")
        self._soc_del_btn.setObjectName("dangerBtn")
        self._soc_del_btn.clicked.connect(self._on_delete_social)
        soc_del_row.addWidget(self._soc_del_btn)
        soc_del_row.addStretch()
        layout.addLayout(soc_del_row)
        layout.addStretch()
        return w

    def _on_save_social(self) -> None:
        try:
            r = SocialHealthRecord(
                student_id=self._student_id,
                record_date=self._soc_date.date().toPyDate(),
                activity_type=self._soc_activity_type.currentText(),
                duration_minutes=self._soc_duration.value(),
                interaction_count=self._soc_interactions.value(),
            )
            rid = self._health_dao.save_social_record(r)
            self._soc_msg.setText(f"✅ 已保存 (ID:{rid})")
            self._load_social_history()
            self._refresh_health_assessment()
        except Exception as e:
            self._soc_msg.setText(f"❌ {e}")

    def _load_social_history(self) -> None:
        self._soc_history.clear()
        records = self._health_dao.get_social_records(self._student_id, days=30)
        for r in records[:20]:
            self._soc_history.addItem(
                f"[{r['record_date']}] {r['activity_type']} {r['duration_minutes']}min "
                f"| {r['interaction_count']}人互动"
            )

    def _on_delete_physical(self) -> None:
        records = self._health_dao.get_physical_records(self._student_id, days=30)
        idx = self._phy_history.currentRow()
        if 0 <= idx < len(records):
            rid = records[idx]["id"]
            if QMessageBox.question(self, "确认", f"删除身体健康记录 #{rid}？") == QMessageBox.Yes:
                self._health_dao.delete_physical(rid)
                self._load_physical_history()

    def _on_delete_mental(self) -> None:
        records = self._health_dao.get_mental_records(self._student_id, days=30)
        idx = self._men_history.currentRow()
        if 0 <= idx < len(records):
            rid = records[idx]["id"]
            if QMessageBox.question(self, "确认", f"删除心理健康记录 #{rid}？") == QMessageBox.Yes:
                self._health_dao.delete_mental(rid)
                self._load_mental_history()

    def _on_delete_social(self) -> None:
        records = self._health_dao.get_social_records(self._student_id, days=30)
        idx = self._soc_history.currentRow()
        if 0 <= idx < len(records):
            rid = records[idx]["id"]
            if QMessageBox.question(self, "确认", f"删除社交健康记录 #{rid}？") == QMessageBox.Yes:
                self._health_dao.delete_social(rid)
                self._load_social_history()

    # ── Tab 6: 个人信息 ──────────────────────────────────────
    def _create_profile_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        form = QFormLayout(); form.setSpacing(10)

        self._name_edit = QLineEdit(); form.addRow("姓名:", self._name_edit)
        self._sno_edit = QLineEdit()
        form.addRow("学号:", self._sno_edit)
        self._gender_combo = QComboBox()
        self._gender_combo.addItems(["男", "女"])
        form.addRow("性别:", self._gender_combo)
        self._grade_edit = QLineEdit(); form.addRow("年级:", self._grade_edit)
        self._major_edit = QLineEdit(); form.addRow("专业:", self._major_edit)
        self._year_spin = QSpinBox()
        self._year_spin.setRange(2016, 2030); self._year_spin.setValue(2024)
        form.addRow("入学年份:", self._year_spin)
        layout.addLayout(form)

        save_btn = QPushButton("💾 保存个人信息")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._on_save_profile)
        layout.addWidget(save_btn)

        self._profile_msg = QLabel("")
        self._profile_msg.setStyleSheet("color: #059669; font-size: 18px;")
        layout.addWidget(self._profile_msg)
        layout.addStretch()
        return w

    def _load_student_info(self) -> None:
        s = self._student_dao.get_by_id(self._student_id)
        if s:
            self._name_edit.setText(s.name)
            self._sno_edit.setText(s.student_no)
            gender_display = "男" if s.gender == "M" else "女" if s.gender == "F" else s.gender
            self._gender_combo.setCurrentText(gender_display)
            self._grade_edit.setText(s.grade_level)
            self._major_edit.setText(s.major)
            self._year_spin.setValue(s.enrollment_year)

    def _on_save_profile(self) -> None:
        try:
            s = self._student_dao.get_by_id(self._student_id)
            if s:
                s.student_no = self._sno_edit.text()
                s.name = self._name_edit.text()
                gender_display = self._gender_combo.currentText()
                s.gender = "M" if gender_display == "男" else "F"
                s.grade_level = self._grade_edit.text()
                s.major = self._major_edit.text()
                s.enrollment_year = self._year_spin.value()
                self._student_dao.update(s)
                self._profile_msg.setText("✅ 个人信息已更新")
                if self._on_student_updated:
                    self._on_student_updated()
        except Exception as e:
            self._profile_msg.setText(f"❌ {e}")

    # ── Tab 7: 课程管理 ──────────────────────────────────────
    def _create_course_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        add_group = QGroupBox("添加课程")
        add_form = QFormLayout(add_group)
        self._course_code_edit = QLineEdit()
        add_form.addRow("课程代码:", self._course_code_edit)
        self._course_name_edit = QLineEdit()
        add_form.addRow("课程名称:", self._course_name_edit)
        self._course_credit = QDoubleSpinBox()
        self._course_credit.setRange(0.5, 10); self._course_credit.setValue(3.0)
        self._course_credit.setSingleStep(0.5); self._course_credit.setDecimals(1)
        add_form.addRow("学分:", self._course_credit)
        self._course_semester = QLineEdit("2025-春")
        add_form.addRow("学期:", self._course_semester)
        self._course_compulsory = QComboBox()
        self._course_compulsory.addItems(["必修", "选修"])
        add_form.addRow("类型:", self._course_compulsory)
        layout.addWidget(add_group)

        add_btn = QPushButton("➕ 添加课程")
        add_btn.setObjectName("successBtn")
        add_btn.clicked.connect(self._on_add_course)
        layout.addWidget(add_btn)

        self._course_msg = QLabel("")
        self._course_msg.setStyleSheet("color: #059669; font-size: 18px;")
        layout.addWidget(self._course_msg)

        # 课程列表
        list_group = QGroupBox("已有课程（选中可删除）")
        list_layout = QVBoxLayout(list_group)
        self._course_list = QListWidget()
        list_layout.addWidget(self._course_list)

        del_btn = QPushButton("🗑 删除选中课程")
        del_btn.setObjectName("dangerBtn")
        del_btn.clicked.connect(self._on_delete_course)
        list_layout.addWidget(del_btn)
        layout.addWidget(list_group)

        self._load_course_list()
        return w

    def _on_add_course(self) -> None:
        try:
            code = self._course_code_edit.text().strip()
            name = self._course_name_edit.text().strip()
            if not code or not name:
                self._course_msg.setText("❌ 代码和名称不能为空")
                return
            credit = self._course_credit.value()
            semester = self._course_semester.text().strip()
            is_compulsory = self._course_compulsory.currentText() == "必修"

            cid = self._course_dao.create_with_defaults(code, name, credit, semester, is_compulsory)
            # 建课后立即为当前学生建立选课关系，否则该课程不会出现在各页课程下拉中
            self._score_dao.enroll(self._student_id, cid)
            self._course_msg.setText(f"✅ 课程已添加并选课 (ID:{cid})")
            self._course_code_edit.clear()
            self._course_name_edit.clear()
            self._load_course_list()
        except Exception as e:
            self._course_msg.setText(f"❌ {e}")

    def _load_course_list(self) -> None:
        self._course_list.clear()
        for c in self._course_dao.get_all():
            comp = "必修" if getattr(c, 'is_compulsory', True) else "选修"
            self._course_list.addItem(
                f"[{c.course_code}] {c.course_name} | {c.credit}学分 | {c.semester} | {comp}"
            )

    def _on_delete_course(self) -> None:
        courses = self._course_dao.get_all()
        idx = self._course_list.currentRow()
        if 0 <= idx < len(courses):
            c = courses[idx]
            if QMessageBox.question(self, "确认",
                f"删除课程「{c.course_name}」及其所有关联数据？") == QMessageBox.Yes:
                self._course_dao.delete(c.course_id)
                self._load_course_list()

    def _refresh_health_assessment(self) -> None:
        """Save a health assessment snapshot so health trend chart updates."""
        try:
            from business_layer.digital_twin import DigitalTwin
            dt = DigitalTwin(self._student_id, self._db)
            dt.save_assessment()
        except Exception:
            pass

    def _load_course_combos(self) -> None:
        """Refill course dropdowns with the current student's enrollments."""
        for combo, with_placeholder in ((self._study_course, True), (self._score_course, False)):
            combo.blockSignals(True)
            current = combo.currentData()
            combo.clear()
            if with_placeholder:
                combo.addItem("（无特定课程）", None)
            for c in self._course_dao.get_by_student(self._student_id):
                combo.addItem(c.course_name, c.course_id)
            idx = combo.findData(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.blockSignals(False)

    def refresh(self) -> None:
        self._load_student_info()
        self._load_record_list()
        self._load_score_history()
        self._load_physical_history()
        self._load_mental_history()
        self._load_social_history()
        self._load_course_list()
        self._load_course_combos()
