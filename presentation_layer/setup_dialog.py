"""首次启动配置对话框 + 数据库自动初始化."""
from __future__ import annotations

import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from config import DEFAULT_DB_CONFIG, DEFAULT_LLM_CONFIG, save_runtime_config


def _resource_path(relative: str) -> str:
    """Locate bundled resource whether running as script or PyInstaller exe."""
    if getattr(sys, "frozen", False):
        return str(Path(sys._MEIPASS) / relative)
    return str(Path(__file__).resolve().parent.parent / relative)


SQL_FILES = ["schema.sql", "v2_extend.sql", "v3_health_extend.sql"]


class SetupDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("首次启动配置 - 大学生智能成长平台")
        self.setModal(True)
        self.setMinimumWidth(520)
        self._init_ok = False
        self._build_ui()
        self._fill_defaults()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        db_group = QGroupBox("数据库配置")
        db_form = QFormLayout(db_group)
        self._host = QLineEdit()
        self._port = QSpinBox()
        self._port.setRange(1, 65535)
        self._user = QLineEdit()
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.Password)
        self._database = QLineEdit()
        self._charset = QLineEdit()

        db_form.addRow("主机", self._host)
        db_form.addRow("端口", self._port)
        db_form.addRow("用户名", self._user)
        db_form.addRow("密码", self._password)
        db_form.addRow("数据库名", self._database)
        db_form.addRow("字符集", self._charset)
        layout.addWidget(db_group)

        llm_group = QGroupBox("LLM 配置（可选）")
        llm_form = QFormLayout(llm_group)
        self._api_key = QLineEdit()
        self._api_url = QLineEdit()
        self._model = QLineEdit()
        llm_form.addRow("API Key", self._api_key)
        llm_form.addRow("API URL", self._api_url)
        llm_form.addRow("模型", self._model)
        layout.addWidget(llm_group)

        note = QLabel("可先只填写数据库信息；LLM 功能可后续在 config.json 中补充。")
        note.setStyleSheet("color: #888888; font-size: 16px; padding: 2px 0;")
        layout.addWidget(note)

        # 进度条
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setTextVisible(True)
        self._progress.setFixedHeight(22)
        layout.addWidget(self._progress)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #666666; font-size: 15px;")
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        # 按钮
        btn_layout = QHBoxLayout()
        self._init_btn = QPushButton("🔧 测试连接并初始化数据库")
        self._init_btn.setStyleSheet(
            "QPushButton { background-color: #d97706; color: white; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background-color: #d97706; }"
            "QPushButton:disabled { background-color: #999999; }"
        )
        self._init_btn.clicked.connect(self._on_init)
        btn_layout.addWidget(self._init_btn)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        btn_layout.addWidget(button_box)
        layout.addLayout(btn_layout)

    def _fill_defaults(self) -> None:
        self._host.setText(DEFAULT_DB_CONFIG["host"])
        self._port.setValue(int(DEFAULT_DB_CONFIG["port"]))
        self._user.setText(DEFAULT_DB_CONFIG["user"])
        self._password.setText(DEFAULT_DB_CONFIG["password"])
        self._database.setText(DEFAULT_DB_CONFIG["database"])
        self._charset.setText(DEFAULT_DB_CONFIG.get("charset", "utf8mb4"))

        self._api_key.setText(DEFAULT_LLM_CONFIG["api_key"])
        self._api_url.setText(DEFAULT_LLM_CONFIG["api_url"])
        self._model.setText(DEFAULT_LLM_CONFIG["model"])

    # ── 收集表单数据 ──────────────────────────────────────

    def _db_config(self) -> dict:
        return {
            "host": self._host.text().strip(),
            "port": self._port.value(),
            "user": self._user.text().strip(),
            "password": self._password.text(),
            "database": self._database.text().strip(),
            "charset": self._charset.text().strip() or "utf8mb4",
        }

    def _llm_config(self) -> dict:
        return {
            "api_key": self._api_key.text().strip(),
            "api_url": self._api_url.text().strip() or DEFAULT_LLM_CONFIG["api_url"],
            "model": self._model.text().strip() or DEFAULT_LLM_CONFIG["model"],
        }

    def _validate(self) -> bool:
        cfg = self._db_config()
        if not cfg["host"] or not cfg["user"] or not cfg["database"]:
            QMessageBox.warning(self, "配置不完整", "请填写数据库主机、用户名和数据库名。")
            return False
        return True

    # ── 初始化按钮 ────────────────────────────────────────

    def _on_init(self) -> None:
        if not self._validate():
            return

        self._init_btn.setEnabled(False)
        self._init_btn.setText("正在初始化...")
        self._progress.setVisible(True)
        self._status_label.setVisible(True)

        db_cfg = self._db_config()
        try:
            self._run_init(db_cfg)
            self._init_ok = True
            self._status_label.setText("✅ 数据库初始化完成！点击「确定」启动程序。")
            self._status_label.setStyleSheet("color: #4ade80; font-size: 16px; font-weight: bold;")
            QMessageBox.information(self, "初始化成功", "数据库已就绪，点击「确定」启动程序。")
        except Exception as e:
            self._status_label.setText(f"❌ 初始化失败：{e}")
            self._status_label.setStyleSheet("color: #f87171; font-size: 16px;")
            QMessageBox.critical(self, "初始化失败", str(e))
        finally:
            self._init_btn.setEnabled(True)
            self._init_btn.setText("🔧 测试连接并初始化数据库")

    def _run_init(self, db_cfg: dict) -> None:
        import pymysql

        steps = 4 + len(SQL_FILES)
        self._progress.setMaximum(steps)
        step = 0

        # 1. 连接 MySQL 并创建数据库
        step += 1
        self._set_status(step, steps, "连接 MySQL 服务器...")
        conn = pymysql.connect(
            host=db_cfg["host"], port=db_cfg["port"],
            user=db_cfg["user"], password=db_cfg["password"],
            charset=db_cfg.get("charset", "utf8mb4"),
        )
        try:
            with conn.cursor() as cur:
                dbname = db_cfg["database"]
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{dbname}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conn.commit()
        finally:
            conn.close()

        # 2. 执行 SQL 建表脚本
        from data_layer.database import DatabaseManager

        db = DatabaseManager(
            host=db_cfg["host"], port=db_cfg["port"],
            user=db_cfg["user"], password=db_cfg["password"],
            database=db_cfg["database"], charset=db_cfg.get("charset", "utf8mb4"),
        )
        for sql_file in SQL_FILES:
            step += 1
            self._set_status(step, steps, f"执行 {sql_file}...")
            sql_path = _resource_path(f"sql/{sql_file}")
            sql_text = Path(sql_path).read_text(encoding="utf-8")
            for stmt in sql_text.split(";"):
                stmt = stmt.strip()
                if stmt:
                    db.execute_update(stmt)

        # 3. 生成模拟数据
        step += 1
        self._set_status(step, steps, "生成学生数据...")
        student_ids = self._seed_students(db)

        step += 1
        self._set_status(step, steps, "生成课程数据...")
        course_ids = self._seed_courses(db)

        step += 1
        self._set_status(step, steps, "生成选课与成绩...")
        self._seed_enrollments(db, student_ids, course_ids)

        step += 1
        self._set_status(step, steps, "生成学习记录...")
        self._seed_study_records(db, student_ids, course_ids)

        step += 1
        self._set_status(step, steps, "生成知识图谱...")
        kp_map = self._seed_knowledge_points(db, course_ids)
        self._seed_knowledge_mastery(db, student_ids, kp_map)

        step += 1
        self._set_status(step, steps, "生成健康数据...")
        self._seed_physical_health(db, student_ids)
        self._seed_mental_health(db, student_ids)
        self._seed_social_health(db, student_ids)

        # 保存配置
        save_runtime_config(db_cfg, self._llm_config())
        db.close()

    def _set_status(self, current: int, total: int, msg: str) -> None:
        self._progress.setValue(current)
        self._status_label.setText(f"[{current}/{total}] {msg}")
        self._status_label.repaint()
        self._progress.repaint()

    # ── 确定按钮 ──────────────────────────────────────────

    def _on_accept(self) -> None:
        if not self._validate():
            return
        if not self._init_ok:
            retry = QMessageBox.question(
                self, "未初始化",
                "尚未初始化数据库，是否继续？\n\n"
                "建议先点击「测试连接并初始化数据库」完成初始化。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if retry != QMessageBox.Yes:
                return
            save_runtime_config(self._db_config(), self._llm_config())
        self.accept()

    # ── 模拟数据种子（与 generate_mock_data.py 逻辑一致） ──

    @staticmethod
    def _seed_students(db):
        students = [
            ("2022001", "张三", "M", "大二", "计算机科学与技术", 2022),
            ("2022002", "李四", "F", "大二", "计算机科学与技术", 2022),
            ("2022003", "王五", "M", "大二", "软件工程", 2022),
            ("2022004", "赵六", "F", "大一", "数据科学与大数据", 2023),
            ("2022005", "钱七", "M", "大三", "人工智能", 2021),
        ]
        ids = []
        for sno, name, gender, grade, major, year in students:
            sid = db.execute_insert(
                "INSERT INTO student (student_no, name, gender, grade_level, major, enrollment_year) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (sno, name, gender, grade, major, year),
            )
            ids.append(sid)
        return ids

    @staticmethod
    def _seed_courses(db):
        courses = [
            ("CS101", "程序设计基础", 4.0, "2025-春", True, None),
            ("CS102", "数据结构与算法", 4.0, "2025-春", True, None),
            ("CS201", "面向对象程序设计", 3.0, "2025-春", True, None),
            ("CS202", "数据库原理", 3.0, "2025-春", True, None),
            ("CS301", "人工智能导论", 3.0, "2025-春", False, None),
            ("MATH101", "高等数学(上)", 5.0, "2025-春", True, None),
            ("MATH102", "线性代数", 3.0, "2025-春", True, None),
            ("ENG101", "大学英语(4)", 2.0, "2025-春", True, None),
        ]
        prereq_map = {
            "CS102": "CS101",
            "CS201": "CS101",
            "CS301": "MATH101",
        }
        ids = {}
        for code, name, credit, sem, comp, _ in courses:
            cid = db.execute_insert(
                "INSERT INTO course (course_code, course_name, credit, semester, is_compulsory, "
                "prerequisite_course_id) VALUES (%s, %s, %s, %s, %s, NULL)",
                (code, name, credit, sem, comp),
            )
            ids[code] = cid
        for code, prereq_code in prereq_map.items():
            db.execute_update(
                "UPDATE course SET prerequisite_course_id=%s WHERE course_id=%s",
                (ids[prereq_code], ids[code]),
            )
        return list(ids.values())

    @staticmethod
    def _seed_enrollments(db, student_ids, course_ids):
        for sid in student_ids:
            selected = random.sample(course_ids, random.randint(5, len(course_ids)))
            for cid in selected:
                usual = round(random.uniform(55, 98), 1)
                midterm = round(random.uniform(50, 97), 1)
                final = round(usual * 0.3 + midterm * 0.4 + random.uniform(10, 30), 1)
                final = min(100, max(0, final))
                db.execute_insert(
                    "INSERT INTO student_course (student_id, course_id, usual_score, "
                    "midterm_score, final_score) VALUES (%s, %s, %s, %s, %s)",
                    (sid, cid, usual, midterm, final),
                )

    @staticmethod
    def _seed_study_records(db, student_ids, course_ids):
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        for sid in student_ids:
            avg_hours = random.uniform(2.0, 6.0)
            avg_focus = random.randint(40, 85)
            for day_offset in range(30):
                d = start_date + timedelta(days=day_offset)
                if random.random() < 0.85:
                    hours = round(max(0.5, random.gauss(avg_hours, 1.5)), 1)
                    focus = min(100, max(10, int(random.gauss(avg_focus, 15))))
                    cid = random.choice(course_ids) if random.random() < 0.6 else None
                    db.execute_insert(
                        "INSERT INTO study_record (student_id, course_id, study_date, "
                        "study_hours, task_completed, focus_score) VALUES (%s, %s, %s, %s, %s, %s)",
                        (sid, cid, d, hours, random.randint(0, 5), focus),
                    )

    @staticmethod
    def _seed_knowledge_points(db, course_ids):
        result = {}
        for idx, cid in enumerate(course_ids):
            kp_ids = []
            for i in range(6):
                name = f"第{i+1}章-知识点"
                parent_id = kp_ids[-1] if kp_ids and i > 0 else None
                difficulty = min(5, max(1, i))
                kp_id = db.execute_insert(
                    "INSERT INTO knowledge_point (kp_name, course_id, parent_kp_id, "
                    "difficulty, weight) VALUES (%s, %s, %s, %s, %s)",
                    (name, cid, parent_id, difficulty, round(random.uniform(0.8, 1.2), 2)),
                )
                kp_ids.append(kp_id)
            result[cid] = kp_ids
        return result

    @staticmethod
    def _seed_knowledge_mastery(db, student_ids, kp_map):
        for sid in student_ids:
            for cid, kp_ids in kp_map.items():
                for kp_id in kp_ids:
                    base = random.uniform(40, 95)
                    mastery = round(max(5, min(100, random.gauss(base, 18))), 1)
                    db.execute_insert(
                        "INSERT INTO knowledge_mastery (student_id, kp_id, mastery_level, "
                        "last_assessed) VALUES (%s, %s, %s, %s)",
                        (sid, kp_id, mastery, date.today() - timedelta(days=random.randint(0, 14))),
                    )

    @staticmethod
    def _seed_physical_health(db, student_ids):
        exercise_types = ["跑步", "球类", "健身", "瑜伽", "游泳", "骑行", "其他"]
        end_date = date.today()
        for sid in student_ids:
            for day_offset in range(14):
                d = end_date - timedelta(days=day_offset)
                if random.random() < 0.6:
                    db.execute_insert(
                        "INSERT INTO physical_health_record (student_id, record_date, "
                        "exercise_type, exercise_duration, sleep_hours, steps) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (sid, d, random.choice(exercise_types),
                         random.randint(0, 90), round(random.uniform(5, 9), 1),
                         random.randint(1000, 15000)),
                    )

    @staticmethod
    def _seed_mental_health(db, student_ids):
        end_date = date.today()
        for sid in student_ids:
            base_mood = random.randint(5, 8)
            base_stress = random.randint(1, 3)
            base_anxiety = random.randint(1, 3)
            for day_offset in range(14):
                d = end_date - timedelta(days=day_offset)
                if random.random() < 0.55:
                    db.execute_insert(
                        "INSERT INTO mental_health_record (student_id, record_date, "
                        "mood_score, stress_level, anxiety_level, notes) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (sid, d,
                         max(1, min(10, int(random.gauss(base_mood, 1.5)))),
                         max(1, min(5, int(random.gauss(base_stress, 0.8)))),
                         max(1, min(5, int(random.gauss(base_anxiety, 0.7)))),
                         random.choice(["状态不错", "有点累", "充满干劲", "需要休息", None])),
                    )

    @staticmethod
    def _seed_social_health(db, student_ids):
        activity_types = ["社团活动", "朋友聚会", "团队项目", "志愿服务", "学术交流", "其他"]
        end_date = date.today()
        for sid in student_ids:
            for day_offset in range(30):
                d = end_date - timedelta(days=day_offset)
                if random.random() < 0.25:
                    db.execute_insert(
                        "INSERT INTO social_health_record (student_id, record_date, "
                        "activity_type, duration_minutes, interaction_count) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (sid, d, random.choice(activity_types),
                         random.randint(30, 240), random.randint(1, 20)),
                    )
