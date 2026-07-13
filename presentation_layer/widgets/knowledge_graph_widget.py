"""知识图谱页面."""
import networkx as nx
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QGroupBox, QTextEdit, QScrollArea,
)

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO
from business_layer.knowledge_graph import KnowledgeGraph
from utils.chart_canvas import MplCanvas


class KnowledgeGraphWidget(QWidget):
    MASTERY_COLORS = {
        "mastered": "#059669",
        "in_progress": "#d97706",
        "weak": "#dc2626",
    }

    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._course_dao = CourseDAO(db)
        self._kg = KnowledgeGraph(db)
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

        title = QLabel("知识图谱")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        # 课程选择
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("选择课程:"))
        self._course_combo = QComboBox()
        self._course_combo.blockSignals(True)
        courses = self._course_dao.get_by_student(self._student_id)
        for c in courses:
            self._course_combo.addItem(c.course_name, c.course_id)
        self._course_combo.blockSignals(False)
        self._course_combo.currentIndexChanged.connect(self._on_course_changed)
        sel_row.addWidget(self._course_combo)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        # 图例
        legend_row = QHBoxLayout()
        for status, color, label in [
            ("mastered", "#059669", "已掌握 ≥80%"),
            ("in_progress", "#d97706", "进行中 ≥50%"),
            ("weak", "#dc2626", "薄弱 <50%"),
        ]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 28px;")
            legend_row.addWidget(dot)
            legend_row.addWidget(QLabel(label))
            legend_row.addSpacing(16)
        legend_row.addStretch()
        layout.addLayout(legend_row)

        # 图谱
        graph_group = QGroupBox("知识图谱结构")
        graph_layout = QVBoxLayout(graph_group)
        self._graph_canvas = MplCanvas(figsize=(7, 4.5))
        graph_layout.addWidget(self._graph_canvas)
        layout.addWidget(graph_group, 1)

        # 薄弱节点 + 学习建议
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        weak_group = QGroupBox("薄弱知识点")
        weak_layout = QVBoxLayout(weak_group)
        self._weak_text = QTextEdit()
        self._weak_text.setReadOnly(True)
        self._weak_text.setMaximumHeight(150)
        weak_layout.addWidget(self._weak_text)
        bottom_row.addWidget(weak_group)

        suggest_group = QGroupBox("建议学习顺序")
        suggest_layout = QVBoxLayout(suggest_group)
        self._suggest_text = QTextEdit()
        self._suggest_text.setReadOnly(True)
        self._suggest_text.setMaximumHeight(150)
        suggest_layout.addWidget(self._suggest_text)
        bottom_row.addWidget(suggest_group)

        layout.addLayout(bottom_row)
        scroll.setWidget(container)

    def _on_course_changed(self) -> None:
        self.refresh()

    def _draw_graph(self) -> None:
        course_id = self._course_combo.currentData()
        if course_id is None:
            return

        try:
            self._kg.build_graph(course_id)
            if len(self._kg.graph) == 0:
                return

            mastery = self._kg.mark_mastery(self._student_id)
            pos = self._kg.get_node_positions()
            labels = self._kg.get_node_labels()

            # 确保 pos 覆盖所有节点
            graph_nodes = list(self._kg.graph.nodes())
            if not all(n in pos for n in graph_nodes):
                pos = nx.spring_layout(self._kg.graph, seed=42)

            self._graph_canvas.fig.clear()
            ax = self._graph_canvas.fig.add_subplot(111)

            node_colors = [self.MASTERY_COLORS.get(mastery.get(n, "in_progress"), "#d9d9d9")
                           for n in graph_nodes]

            nx.draw(self._kg.graph, pos, ax=ax, with_labels=True, labels=labels,
                    node_color=node_colors, node_size=800, font_size=9,
                    edge_color="#666666", arrows=True, arrowsize=15,
                    font_color="#1a1a1a", font_weight="bold")

            ax.set_title("课程知识图谱 (绿色=已掌握 | 黄色=进行中 | 红色=薄弱)",
                         fontsize=11, fontweight="bold")
            self._graph_canvas.draw()

            # 更新薄弱节点列表
            weak = self._kg.get_weak_nodes(self._student_id)
            if weak:
                self._weak_text.setText("\n".join(
                    f"• {w['kp_name']} (掌握度: {w['mastery']}%)" for w in weak
                ))
            else:
                self._weak_text.setText("暂无薄弱知识点，继续加油！")

            # 学习建议
            order = self._kg.suggest_study_order(self._student_id)
            if order:
                self._suggest_text.setText("\n".join(
                    f"{i+1}. {name}" for i, name in enumerate(order)
                ))
            else:
                self._suggest_text.setText("所有知识点掌握良好！")
        except Exception as e:
            self._graph_canvas.fig.clear()
            ax = self._graph_canvas.fig.add_subplot(111)
            import traceback
            err_msg = f"图谱渲染失败: {type(e).__name__}: {e}"
            print(err_msg)
            traceback.print_exc()
            ax.text(0.5, 0.5, err_msg, ha="center", va="center",
                    transform=ax.transAxes, fontsize=11, color="#dc2626")
            self._graph_canvas.draw()

    def refresh(self) -> None:
        if self._course_combo.count() > 0:
            self._draw_graph()
