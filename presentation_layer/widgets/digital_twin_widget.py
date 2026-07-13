"""数字孪生页面 - 健康仪表盘 + 雷达图."""
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFrame,
    QProgressBar, QScrollArea,
)
from PyQt5.QtCore import Qt

from data_layer.database import DatabaseManager
from business_layer.digital_twin import DigitalTwin
from presentation_layer.styles import get_risk_colors, get_theme_color
from utils.chart_canvas import MplCanvas


class DigitalTwinWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
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

        title = QLabel("数字孪生 - 学生健康画像")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        # 顶部：进度条 + 风险等级
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # 健康度进度条
        gauge_group = QGroupBox("综合健康度")
        gauge_layout = QVBoxLayout(gauge_group)
        self._health_bar = QProgressBar()
        self._health_bar.setMinimum(0)
        self._health_bar.setMaximum(100)
        self._health_bar.setTextVisible(True)
        self._health_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #d9d9d9; border-radius: 8px; "
            "text-align: center; font-size: 28px; font-weight: bold; height: 30px; }"
            "QProgressBar::chunk { border-radius: 8px; }"
        )
        self._health_value = QLabel("0 / 100")
        self._health_value.setAlignment(Qt.AlignCenter)
        self._health_value.setStyleSheet("font-size: 28px; color: #666666;")
        gauge_layout.addWidget(self._health_bar)
        gauge_layout.addWidget(self._health_value)
        top_row.addWidget(gauge_group)

        # 风险等级指示
        risk_group = QGroupBox("风险等级")
        risk_layout = QVBoxLayout(risk_group)
        self._risk_label = QLabel("--")
        self._risk_label.setAlignment(Qt.AlignCenter)
        self._risk_label.setStyleSheet("font-size: 46px; font-weight: bold;")
        risk_layout.addWidget(self._risk_label)
        top_row.addWidget(risk_group)

        layout.addLayout(top_row)

        # 雷达图
        radar_group = QGroupBox("四维度雷达图")
        radar_layout = QVBoxLayout(radar_group)
        self._radar_canvas = MplCanvas(figsize=(4.5, 4))
        radar_layout.addWidget(self._radar_canvas)
        layout.addWidget(radar_group)

        # 四维度详情进度条
        detail_group = QGroupBox("维度详情")
        detail_layout = QVBoxLayout(detail_group)
        detail_layout.setSpacing(10)

        self._dim_bars = {}
        for name, label_cn in [
            ("academic", "学术健康"), ("physical", "身体健康"),
            ("mental", "心理健康"), ("social", "社交健康"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label_cn)
            lbl.setFixedWidth(100)
            lbl.setStyleSheet("font-weight: bold; font-size: 18px;")
            row.addWidget(lbl)

            bar = QProgressBar()
            bar.setMinimum(0)
            bar.setMaximum(100)
            bar.setTextVisible(True)
            row.addWidget(bar)

            val = QLabel("0")
            val.setFixedWidth(40)
            val.setAlignment(Qt.AlignRight)
            row.addWidget(val)

            detail_layout.addLayout(row)
            self._dim_bars[name] = (bar, val)

        layout.addWidget(detail_group)
        layout.addStretch()
        scroll.setWidget(container)

    def _update_health_bar_color(self, value: float) -> str:
        if value >= 80:
            return "#059669"
        elif value >= 60:
            return "#d97706"
        elif value >= 40:
            return "#ea580c"
        return "#dc2626"

    def _draw_radar(self, values: dict[str, float]) -> None:
        categories = ["学术健康", "身体健康", "心理健康", "社交健康"]
        order = ["academic", "physical", "mental", "social"]
        data = [values.get(k, 0) for k in order]

        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        data.append(data[0])
        angles.append(angles[0])

        self._radar_canvas.fig.clear()
        ax = self._radar_canvas.fig.add_subplot(111, projection="polar")
        ax.fill(angles, data, alpha=0.25, color="#1890ff")
        ax.plot(angles, data, "o-", color="#1890ff", linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8)
        ax.set_title("健康四维度评估", fontsize=13, fontweight="bold", pad=20)
        self._radar_canvas.draw()

    def refresh(self) -> None:
        if not hasattr(self, '_twin'):
            self._twin = DigitalTwin(self._student_id, self._db)
        result = self._twin.assess_overall()

        color = self._update_health_bar_color(result.overall)
        self._health_bar.setValue(int(result.overall))
        self._health_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #d9d9d9; border-radius: 8px; "
            "text-align: center; font-size: 28px; font-weight: bold; height: 30px; }"
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 8px; }}"
        )
        self._health_value.setText(f"{result.overall} / 100")

        risk_color = get_risk_colors().get(result.risk_level.value, "#52c41a")
        self._risk_label.setText(result.risk_level.value)
        self._risk_label.setStyleSheet(
            f"font-size: 46px; font-weight: bold; color: {risk_color};"
        )

        dims = {"academic": result.academic, "physical": result.physical,
                "mental": result.mental, "social": result.social}
        self._draw_radar(dims)

        for name, (bar, val) in self._dim_bars.items():
            v = dims.get(name, 0)
            bar.setValue(int(v))
            c = self._update_health_bar_color(v)
            bar.setStyleSheet(
                "QProgressBar { border: 1px solid #d9d9d9; border-radius: 4px; "
                "text-align: center; height: 22px; }"
                f"QProgressBar::chunk {{ background-color: {c}; border-radius: 4px; }}"
            )
            val.setText(str(int(v)))
