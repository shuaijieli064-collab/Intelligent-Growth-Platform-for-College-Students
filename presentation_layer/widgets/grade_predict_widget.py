"""成绩预测页面."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDoubleSpinBox, QGroupBox, QScrollArea, QCheckBox,
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import numpy as np

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from business_layer.grade_predictor_v2 import GradePredictorV2
from utils.chart_canvas import MplCanvas


class GradePredictWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._course_dao = CourseDAO(db)
        self._score_dao = StudentCourseDAO(db)
        self._predictor = GradePredictorV2(db)
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

        title = QLabel("成绩预测")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        # 预测输入
        input_group = QGroupBox("输入成绩预测期末")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        # 课程选择
        course_row = QHBoxLayout()
        course_row.addWidget(QLabel("选择课程:"))
        self._course_combo = QComboBox()
        courses = self._course_dao.get_by_student(self._student_id)
        self._course_combo.addItem("全部课程", None)
        for c in courses:
            self._course_combo.addItem(c.course_name, c.course_id)
        course_row.addWidget(self._course_combo)
        course_row.addStretch()
        input_layout.addLayout(course_row)

        # 成绩输入
        scores_row = QHBoxLayout()
        scores_row.addWidget(QLabel("平时成绩:"))
        self._usual_spin = QDoubleSpinBox()
        self._usual_spin.setRange(0, 100)
        self._usual_spin.setValue(75)
        self._usual_spin.setDecimals(1)
        self._usual_spin.setSuffix(" 分")
        scores_row.addWidget(self._usual_spin)

        scores_row.addSpacing(24)
        scores_row.addWidget(QLabel("期中成绩:"))
        self._midterm_spin = QDoubleSpinBox()
        self._midterm_spin.setRange(0, 100)
        self._midterm_spin.setValue(70)
        self._midterm_spin.setDecimals(1)
        self._midterm_spin.setSuffix(" 分")
        scores_row.addWidget(self._midterm_spin)
        scores_row.addStretch()
        input_layout.addLayout(scores_row)

        # 按钮行
        btn_row = QHBoxLayout()
        self._train_btn = QPushButton("训练模型")
        self._train_btn.setObjectName("primaryBtn")
        self._train_btn.clicked.connect(self._on_train)
        btn_row.addWidget(self._train_btn)

        self._xgb_check = QCheckBox("XGBoost")
        self._xgb_check.setStyleSheet("color: #666666; font-size: 18px;")
        btn_row.addWidget(self._xgb_check)

        self._predict_btn = QPushButton("预测成绩")
        self._predict_btn.setObjectName("successBtn")
        self._predict_btn.clicked.connect(self._on_predict)
        self._predict_btn.setEnabled(False)
        btn_row.addWidget(self._predict_btn)
        btn_row.addStretch()
        input_layout.addLayout(btn_row)

        # 结果展示
        self._result_label = QLabel("请先训练模型，然后输入成绩进行预测")
        self._result_label.setStyleSheet(
            "font-size: 28px; color: #d97706; padding: 12px; "
            "background-color: rgba(217,119,6,0.08); border-radius: 4px;"
        )
        self._result_label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self._result_label)

        # 模型指标
        self._metrics_label = QLabel("")
        self._metrics_label.setStyleSheet("font-size: 18px; color: #666666;")
        input_layout.addWidget(self._metrics_label)

        layout.addWidget(input_group)

        # 图表区
        chart_group = QGroupBox("历史成绩与预测")
        chart_layout = QVBoxLayout(chart_group)
        self._chart_canvas = MplCanvas(figsize=(8, 3.5))
        chart_layout.addWidget(self._chart_canvas)
        layout.addWidget(chart_group)

        layout.addStretch()
        scroll.setWidget(container)

    def _on_train(self) -> None:
        try:
            course_id = self._course_combo.currentData()
            use_xgb = self._xgb_check.isChecked() if hasattr(self, '_xgb_check') else False
            metrics = self._predictor.train(course_id=course_id, use_xgboost=use_xgb)
            if "error" in metrics:
                self._result_label.setText(f"⚠ {metrics['error']}")
                self._predict_btn.setEnabled(False)
                return
            self._predict_btn.setEnabled(True)
            self._metrics_label.setText(
                f"{metrics['algorithm']} | 样本: {metrics['samples']} | "
                f"CV_MAE: {metrics['cv_mae']} | 残差σ: {metrics['residual_std']}"
            )
            course_name = self._course_combo.currentText()
            self._result_label.setText(f"模型已就绪（{course_name}），请输入成绩并点击预测")
            self._draw_history_chart()
        except Exception as e:
            self._result_label.setText(f"训练失败: {str(e)}")

    def _on_predict(self) -> None:
        try:
            usual = self._usual_spin.value()
            midterm = self._midterm_spin.value()
            result = self._predictor.predict(usual, midterm)
            self._result_label.setText(
                f"预测: {result['predicted']} 分 | "
                f"95%置信区间: [{result['ci_lower']}, {result['ci_upper']}] | "
                f"及格概率: {result['pass_probability']}% | "
                f"{result['risk']}"
            )
            color = "#059669" if result['pass_probability'] > 80 else "#d97706" if result['pass_probability'] > 50 else "#dc2626"
            self._result_label.setStyleSheet(
                f"font-size: 28px; font-weight: bold; color: {color}; padding: 12px; "
                "background-color: rgba(16,185,129,0.08); border-radius: 4px;"
            )
            # 保存预测到数据库
            cid = self._course_combo.currentData()
            if cid:
                self._score_dao.update_predicted(self._student_id, cid, result['predicted'])
        except Exception as e:
            self._result_label.setText(f"预测失败: {str(e)}")

    def _draw_history_chart(self) -> None:
        scores = self._score_dao.get_student_scores(self._student_id)
        # Filter by selected course if one is chosen
        selected_cid = self._course_combo.currentData()
        if selected_cid:
            scores = [s for s in scores if s.get("course_id") == selected_cid]

        self._chart_canvas.fig.clear()
        ax = self._chart_canvas.fig.add_subplot(111)

        courses_names = []
        usuals = []
        midterms = []
        finals = []
        for s in scores:
            if all(s.get(k) is not None for k in ["usual_score", "midterm_score", "final_score"]):
                courses_names.append(s["course_name"][:6])
                usuals.append(s["usual_score"])
                midterms.append(s["midterm_score"])
                finals.append(s["final_score"])

        x = np.arange(len(courses_names))
        w = 0.25
        if courses_names:
            ax.bar(x - w, usuals, w, label="平时成绩", color="#91d5ff")
            ax.bar(x, midterms, w, label="期中成绩", color="#69c0ff")
            ax.bar(x + w, finals, w, label="期末成绩", color="#1890ff")
            ax.set_xticks(x)
            ax.set_xticklabels(courses_names, fontsize=9)
            ax.legend(fontsize=9)
            ax.set_ylabel("分数", fontsize=10)
            ax.set_ylim(0, 105)
            ax.set_title("各课程成绩对比", fontsize=12, fontweight="bold")
        else:
            ax.text(0.5, 0.5, "暂无完整成绩数据", ha="center", va="center",
                    transform=ax.transAxes, fontsize=14, color="#666666")

        self._chart_canvas.draw()

    def refresh(self) -> None:
        current_cid = self._course_combo.currentData()
        self._course_combo.clear()
        self._course_combo.addItem("全部课程", None)
        for c in self._course_dao.get_by_student(self._student_id):
            self._course_combo.addItem(c.course_name, c.course_id)
        if current_cid:
            idx = self._course_combo.findData(current_cid)
            if idx >= 0:
                self._course_combo.setCurrentIndex(idx)
        # 重建预测模型并重绘图表，避免用旧学生的模型/数据做预测
        self._predictor = GradePredictorV2(self._db)
        self._predict_btn.setEnabled(False)
        self._metrics_label.setText("")
        self._result_label.setText("请先训练模型，然后输入成绩进行预测")
        self._result_label.setStyleSheet(
            "font-size: 28px; color: #d97706; padding: 12px; "
            "background-color: rgba(217,119,6,0.08); border-radius: 4px;"
        )
        self._draw_history_chart()
