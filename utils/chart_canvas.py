"""Matplotlib canvas embedded in PyQt5 — theme-aware via styles.py."""
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from presentation_layer.styles import get_theme, get_theme_color, apply_chart_theme

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Apply initial theme
apply_chart_theme(get_theme())


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, figsize=(6, 4), dpi=100, parent=None) -> None:
        bg = get_theme_color("bg_card")
        self.fig = Figure(figsize=figsize, dpi=dpi, facecolor=bg)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet(f"background-color: {bg};")

    def refresh_theme(self) -> None:
        """Re-apply theme after a theme switch."""
        bg = get_theme_color("bg_card")
        self.fig.set_facecolor(bg)
        apply_chart_theme(get_theme())
        self.draw()
