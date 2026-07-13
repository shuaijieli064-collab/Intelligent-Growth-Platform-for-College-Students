"""专注度监测页面 — theme-aware."""
from datetime import date, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox, QScrollArea,
)
from PyQt5.QtCore import Qt

from data_layer.database import DatabaseManager
from business_layer.focus_monitor import FocusMonitor
from presentation_layer.styles import get_theme, get_theme_color, apply_chart_theme
from utils.chart_canvas import MplCanvas


class FocusMonitorWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._monitor = FocusMonitor(db, student_id)
        self._setup_ui()

    def _tc(self, key: str) -> str:
        """Shorthand for theme color lookup."""
        return get_theme_color(key)

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

        title = QLabel("专注度监测")
        title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {self._tc('text_primary')};")
        layout.addWidget(title)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self._focus_card = self._make_card("实时专注指数", "--", "当前专注度", self._tc("accent"))
        cards_row.addWidget(self._focus_card)

        self._level_card = self._make_card("专注等级", "--", "评估", self._tc("success"))
        cards_row.addWidget(self._level_card)

        self._trend_card = self._make_card("趋势", "--", "近7天变化", self._tc("warning"))
        cards_row.addWidget(self._trend_card)

        layout.addLayout(cards_row)

        chart_group = QGroupBox("专注度趋势 (14天)")
        chart_layout = QVBoxLayout(chart_group)
        self._chart_canvas = MplCanvas(figsize=(8, 3.5))
        chart_layout.addWidget(self._chart_canvas)
        layout.addWidget(chart_group)

        heat_group = QGroupBox("专注度热历图 (30天)")
        heat_layout = QVBoxLayout(heat_group)
        self._heat_canvas = MplCanvas(figsize=(8, 2.5))
        heat_layout.addWidget(self._heat_canvas)
        layout.addWidget(heat_group)

        layout.addStretch()
        scroll.setWidget(container)

    def _make_card(self, title: str, value: str, desc: str, color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(180, 100)
        cl = QVBoxLayout(card)
        cl.setSpacing(4)
        t = QLabel(title); t.setObjectName("cardTitle"); cl.addWidget(t)
        v = QLabel(value); v.setObjectName("cardValue")
        v.setStyleSheet(f"color: {color}; font-size: 38px; font-weight: bold;"); cl.addWidget(v)
        d = QLabel(desc); d.setObjectName("cardDesc"); cl.addWidget(d)
        return card

    def _draw_focus_chart(self) -> None:
        accent = self._tc("accent")
        success = self._tc("success")
        daily = self._monitor.get_daily_focus(14)
        self._chart_canvas.fig.clear()
        ax = self._chart_canvas.fig.add_subplot(111)

        if daily:
            dates = [d["date"] for d in daily]
            focus = [d["avg_focus"] for d in daily]
            ax.fill_between(range(len(dates)), focus, alpha=0.15, color=accent)
            ax.plot(range(len(dates)), focus, "o-", color=accent, linewidth=2, markersize=5)
            ax.axhline(y=80, color=success, linestyle=":", alpha=0.5, label="优秀(80)")
            ax.axhline(y=60, color=accent, linestyle=":", alpha=0.5, label="正常(60)")
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels([d[-5:] for d in dates], rotation=45, fontsize=8)
            ax.set_ylim(0, 105)
            ax.set_ylabel("专注度", fontsize=10)
            ax.legend(fontsize=8, loc="upper left")

        ax.set_title("每日专注度变化", fontsize=12, fontweight="bold")
        self._chart_canvas.draw()

    def _draw_heatmap(self) -> None:
        danger = self._tc("danger")
        warning = self._tc("warning")
        accent = self._tc("accent")
        success = self._tc("success")
        edge = self._tc("bg_card")

        heat_data = self._monitor.get_focus_heatmap(30)
        self._heat_canvas.fig.clear()
        ax = self._heat_canvas.fig.add_subplot(111)

        if heat_data:
            dates = sorted(heat_data.keys())
            values = [heat_data[d] for d in dates]
            colors = [
                danger if v < 40 else warning if v < 60 else accent if v < 80 else success
                for v in values
            ]
            ax.bar(range(len(dates)), [1]*len(dates), color=colors, width=1.0, edgecolor=edge)
            ax.set_yticks([])
            ax.set_xticks(range(0, len(dates), max(1, len(dates)//10)))
            ax.set_xticklabels([dates[i][-5:] for i in range(0, len(dates), max(1, len(dates)//10))],
                               rotation=45, fontsize=8)
            t = get_theme()
            title_text = "专注度热历图 (深绿>=80 | 蓝>=60 | 橙>=40 | 红<40)"
            if t == "dark":
                title_text = "专注度热历图 (绿>=80 | 黄>=60 | 橙>=40 | 红<40)"
            ax.set_title(title_text, fontsize=11, fontweight="bold")
        self._heat_canvas.draw()

    def refresh(self) -> None:
        apply_chart_theme(get_theme())
        success = self._tc("success")
        danger = self._tc("danger")
        accent = self._tc("accent")
        warning = self._tc("warning")

        focus = self._monitor.get_current_focus()
        level = self._monitor.get_focus_level()
        trend = self._monitor.get_focus_trend()

        # 专注指数
        color = success if focus >= 80 else warning if focus >= 60 else danger
        self._focus_card.findChild(QLabel, "cardValue").setText(f"{focus}")
        self._focus_card.findChild(QLabel, "cardValue").setStyleSheet(
            f"color: {color}; font-size: 38px; font-weight: bold;"
        )

        # 专注等级
        level_color = {
            "高度专注 🟢": success, "正常 🟡": warning,
            "注意力分散 🟠": "#ea580c", "严重分心 🔴": danger
        }.get(level, self._tc("text_muted"))
        self._level_card.findChild(QLabel, "cardValue").setText(level.split(" ")[0] if " " in level else level)
        self._level_card.findChild(QLabel, "cardValue").setStyleSheet(
            f"color: {level_color}; font-size: 38px; font-weight: bold;"
        )
        self._level_card.findChild(QLabel, "cardDesc").setText(level.split(" ")[1] if " " in level else "")

        # 趋势
        trend_text = {"improving": "↑ 改善中", "declining": "↓ 下降中", "stable": "→ 稳定"}
        trend_label = trend_text.get(trend.get("trend", ""), "→ 稳定")
        trend_color2 = success if trend.get("trend") == "improving" else danger if trend.get("trend") == "declining" else accent
        self._trend_card.findChild(QLabel, "cardValue").setText(f"{trend.get('change', 0):+.0f}")
        self._trend_card.findChild(QLabel, "cardValue").setStyleSheet(
            f"color: {trend_color2}; font-size: 38px; font-weight: bold;"
        )
        self._trend_card.findChild(QLabel, "cardDesc").setText(trend_label)

        # Refresh chart canvas theme
        self._chart_canvas.refresh_theme()
        self._heat_canvas.refresh_theme()

        self._draw_focus_chart()
        self._draw_heatmap()
