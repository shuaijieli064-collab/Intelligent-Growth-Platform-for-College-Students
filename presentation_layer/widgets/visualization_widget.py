"""数据可视化页面 - 学习曲线 / 健康趋势 / 成绩对比."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QScrollArea,
)
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np
import pandas as pd

from data_layer.database import DatabaseManager
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.dao.health_dao import HealthDAO
from data_layer.dao.course_dao import StudentCourseDAO
from data_layer.dao.knowledge_dao import KnowledgeDAO
from business_layer.data_processor import DataProcessor
from utils.chart_canvas import MplCanvas


class VisualizationWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._study_dao = StudyRecordDAO(db)
        self._health_dao = HealthDAO(db)
        self._score_dao = StudentCourseDAO(db)
        self._knowledge_dao = KnowledgeDAO(db)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()

        # Tab 1: 学习曲线
        self._learning_canvas = MplCanvas(figsize=(9, 4))
        self._tabs.addTab(self._learning_canvas, "学习曲线")

        # Tab 2: 健康趋势
        self._health_canvas = MplCanvas(figsize=(9, 4))
        self._tabs.addTab(self._health_canvas, "健康趋势")

        # Tab 3: 成绩对比
        self._score_canvas = MplCanvas(figsize=(9, 4))
        self._tabs.addTab(self._score_canvas, "成绩雷达")

        # Tab 4: 知识掌握热力图
        self._heatmap_canvas = MplCanvas(figsize=(9, 4))
        self._tabs.addTab(self._heatmap_canvas, "知识掌握热力图")

        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs)

    def _on_tab_changed(self, index: int) -> None:
        if index == 0:
            self._plot_learning_curve()
        elif index == 1:
            self._plot_health_trend()
        elif index == 2:
            self._plot_score_radar()
        elif index == 3:
            self._plot_knowledge_heatmap()

    def _plot_learning_curve(self) -> None:
        records = self._study_dao.get_all_by_student(self._student_id)
        self._learning_canvas.fig.clear()

        ax1 = self._learning_canvas.fig.add_subplot(111)

        if not records:
            ax1.text(0.5, 0.5, "暂无学习记录", ha="center", va="center",
                     transform=ax1.transAxes, fontsize=14, color="#666666")
            self._learning_canvas.draw()
            return

        df = pd.DataFrame(records)
        df["study_date"] = pd.to_datetime(df["study_date"])
        df = df.sort_values("study_date")

        daily = df.groupby("study_date").agg(
            hours=("study_hours", "sum"),
            focus=("focus_score", "mean"),
            tasks=("task_completed", "sum"),
        ).reset_index()

        ax1.fill_between(daily["study_date"], daily["hours"], alpha=0.15, color="#91d5ff")
        ax1.plot(daily["study_date"], daily["hours"], "o-", color="#1890ff",
                 linewidth=1.5, markersize=4, label="学习时长(h)")

        # 7日移动平均
        if len(daily) >= 7:
            ma = daily["hours"].rolling(7).mean()
            ax1.plot(daily["study_date"], ma, "-", color="#ff7a45", linewidth=2,
                     label="7日均线")

        # 专注度（右轴）
        ax2 = ax1.twinx()
        ax2.plot(daily["study_date"], daily["focus"], "s-", color="#52c41a",
                 linewidth=1, markersize=3, alpha=0.6, label="专注度")
        ax2.set_ylabel("专注度", fontsize=10, color="#52c41a")
        ax2.set_ylim(0, 105)

        ax1.set_xlabel("日期", fontsize=10)
        ax1.set_ylabel("学习时长 (小时)", fontsize=10, color="#1890ff")
        ax1.set_title("学习曲线 - 每日学习时长与专注度", fontsize=12, fontweight="bold")

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

        ax1.xaxis.set_major_formatter(DateFormatter("%m-%d"))
        self._learning_canvas.fig.autofmt_xdate()
        self._learning_canvas.draw()

    def _plot_health_trend(self) -> None:
        history = self._health_dao.get_history(self._student_id)
        self._health_canvas.fig.clear()

        ax = self._health_canvas.fig.add_subplot(111)

        if not history:
            ax.text(0.5, 0.5, "暂无健康评估数据", ha="center", va="center",
                    transform=ax.transAxes, fontsize=14, color="#666666")
            self._health_canvas.draw()
            return

        dates = [h.assessment_date for h in reversed(history)]
        overall = [h.overall_health for h in reversed(history)]
        academic = [h.academic_score for h in reversed(history)]
        physical = [h.physical_score for h in reversed(history)]
        mental = [h.mental_score for h in reversed(history)]
        social = [h.social_score for h in reversed(history)]

        ax.plot(dates, overall, "o-", color="#1a1a1a", linewidth=2.5, markersize=5,
                label="综合健康度")
        ax.plot(dates, academic, "s--", color="#1890ff", linewidth=1, markersize=4,
                alpha=0.7, label="学术")
        ax.plot(dates, physical, "^--", color="#52c41a", linewidth=1, markersize=4,
                alpha=0.7, label="身体")
        ax.plot(dates, mental, "d--", color="#722ed1", linewidth=1, markersize=4,
                alpha=0.7, label="心理")
        ax.plot(dates, social, "v--", color="#fa8c16", linewidth=1, markersize=4,
                alpha=0.7, label="社交")

        ax.axhline(y=80, color="#52c41a", linestyle=":", alpha=0.5, label="健康线(80)")
        ax.axhline(y=60, color="#faad14", linestyle=":", alpha=0.5, label="警戒线(60)")

        ax.set_xlabel("日期", fontsize=10)
        ax.set_ylabel("分数", fontsize=10)
        ax.set_ylim(0, 105)
        ax.set_title("健康度趋势", fontsize=12, fontweight="bold")
        ax.legend(loc="lower left", fontsize=8, ncol=3)
        ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
        self._health_canvas.fig.autofmt_xdate()
        self._health_canvas.draw()

    def _plot_score_radar(self) -> None:
        scores = self._score_dao.get_student_scores(self._student_id)
        self._score_canvas.fig.clear()

        ax = self._score_canvas.fig.add_subplot(111, projection="polar")

        if not scores:
            ax.text(0.5, 0.5, "暂无成绩数据", ha="center", va="center",
                    transform=ax.transAxes, fontsize=14, color="#666666")
            self._score_canvas.draw()
            return

        courses = [s["course_name"][:6] for s in scores]
        usual_vals = [s["usual_score"] or 0 for s in scores]
        midterm_vals = [s["midterm_score"] or 0 for s in scores]
        final_vals = [s["final_score"] or 0 for s in scores]

        N = len(courses)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()

        # 闭合
        usual_vals.append(usual_vals[0])
        midterm_vals.append(midterm_vals[0])
        final_vals.append(final_vals[0])
        angles.append(angles[0])

        ax.fill(angles, usual_vals, alpha=0.1, color="#91d5ff")
        ax.plot(angles, usual_vals, "o-", color="#91d5ff", linewidth=1.5, label="平时成绩")
        ax.fill(angles, midterm_vals, alpha=0.1, color="#69c0ff")
        ax.plot(angles, midterm_vals, "s-", color="#69c0ff", linewidth=1.5, label="期中成绩")
        ax.fill(angles, final_vals, alpha=0.1, color="#1890ff")
        ax.plot(angles, final_vals, "d-", color="#1890ff", linewidth=2, label="期末成绩")

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(courses, fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_title("各课程成绩雷达图", fontsize=12, fontweight="bold", pad=20)
        ax.legend(loc="upper right", fontsize=9, bbox_to_anchor=(1.3, 1.0))

        self._score_canvas.draw()

    def _plot_knowledge_heatmap(self) -> None:
        kps = self._knowledge_dao.get_all_knowledge_points()
        mastery = self._knowledge_dao.get_mastery(self._student_id)
        mastery_map = {m["kp_id"]: m["mastery_level"] for m in mastery}

        self._heatmap_canvas.fig.clear()
        ax = self._heatmap_canvas.fig.add_subplot(111)

        if not kps:
            ax.text(0.5, 0.5, "暂无知识图谱数据", ha="center", va="center",
                    transform=ax.transAxes, fontsize=14)
            self._heatmap_canvas.draw()
            return

        # 按课程分组
        courses = sorted(set(kp["course_name"] for kp in kps))
        course_kps = {c: [kp for kp in kps if kp["course_name"] == c] for c in courses}

        # 构建热力图数据矩阵
        max_kps = max(len(v) for v in course_kps.values())
        data = np.zeros((len(courses), max_kps))
        labels = []

        for i, course in enumerate(courses):
            labels.append(course[:8])
            for j, kp in enumerate(course_kps[course]):
                data[i, j] = mastery_map.get(kp["kp_id"], 0)

        im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
        ax.set_xticks(range(max_kps))
        ax.set_xticklabels([f"KP{i+1}" for i in range(max_kps)], fontsize=8, rotation=45)
        ax.set_yticks(range(len(courses)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title("知识掌握热力图 (红=薄弱 | 黄=一般 | 绿=掌握)", fontsize=12, fontweight="bold")

        # 标注百分比
        for i in range(len(courses)):
            for j in range(max_kps):
                if data[i, j] > 0:
                    ax.text(j, i, f"{data[i,j]:.0f}", ha="center", va="center",
                            fontsize=7, color="white" if data[i,j] < 50 else "black")

        cbar = self._heatmap_canvas.fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("掌握度 %", fontsize=9)

        self._heatmap_canvas.draw()

    def refresh(self) -> None:
        self._on_tab_changed(self._tabs.currentIndex())
