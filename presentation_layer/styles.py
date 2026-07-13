"""Dual-theme QSS — Claude-inspired light & warm dark, with theme manager."""
from __future__ import annotations

import matplotlib.pyplot as plt
from typing import Any

# ═══════════════════════════════════════════════════════════════
# LIGHT QSS — Claude warm white
# ═══════════════════════════════════════════════════════════════
LIGHT_QSS = """
QMainWindow {
    background-color: #faf9f7;
    color: #1a1a1a;
}

QListWidget#sidebar {
    background-color: #f3f1ed;
    color: #555555;
    border: none;
    border-right: 1px solid #e8e5e1;
    font-size: 17px;
    padding: 12px 0;
    outline: none;
    font-weight: 500;
}
QListWidget#sidebar::item {
    height: 52px;
    padding: 0 22px;
    border-left: 3px solid transparent;
    margin: 2px 0;
    border-radius: 0px 8px 8px 0px;
}
QListWidget#sidebar::item:selected {
    background-color: #e8e3d9;
    color: #1a1a1a;
    border-left: 3px solid #d97706;
}
QListWidget#sidebar::item:hover:!selected {
    background-color: #ede9e2;
    color: #333333;
}

QLabel#appTitle {
    color: #1a1a1a;
    font-size: 21px;
    font-weight: 700;
    padding: 24px 20px;
    background-color: #f3f1ed;
    border-bottom: 1px solid #e8e5e1;
    letter-spacing: 1px;
}

QFrame#card {
    background-color: #ffffff;
    border-radius: 14px;
    border: 1px solid #e8e5e1;
    padding: 24px;
}
QFrame#card:hover { border-color: #d4cfc6; }

QLabel#cardTitle {
    font-size: 16px; font-weight: 600; color: #888888;
    text-transform: uppercase; letter-spacing: 1.5px;
}
QLabel#cardValue { font-size: 42px; font-weight: 700; color: #1a1a1a; }
QLabel#cardDesc { font-size: 17px; color: #999999; }

QPushButton#primaryBtn {
    background-color: #d97706; color: #ffffff; border: none;
    border-radius: 10px; padding: 10px 28px; font-size: 17px; font-weight: 600;
}
QPushButton#primaryBtn:hover { background-color: #b8610a; }
QPushButton#primaryBtn:pressed { background-color: #92400e; }

QPushButton#dangerBtn {
    background-color: #dc2626; color: #ffffff; border: none;
    border-radius: 10px; padding: 8px 20px; font-size: 16px; font-weight: 600;
}
QPushButton#dangerBtn:hover { background-color: #b91c1c; }

QPushButton#successBtn {
    background-color: #059669; color: #ffffff; border: none;
    border-radius: 10px; padding: 8px 20px; font-size: 16px; font-weight: 600;
}
QPushButton#successBtn:hover { background-color: #047857; }

QPushButton {
    background-color: #ffffff; color: #333333; border: 1px solid #d4cfc6;
    border-radius: 10px; padding: 8px 22px; font-size: 17px;
}
QPushButton:hover { background-color: #faf8f5; border-color: #d97706; color: #d97706; }
QPushButton:pressed { background-color: #f3f1ed; }

QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit {
    border: 1px solid #d4cfc6; border-radius: 10px; padding: 10px 16px;
    font-size: 17px; background-color: #ffffff; color: #1a1a1a;
    selection-background-color: rgba(217,119,6,0.2);
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QDateEdit:focus {
    border-color: #d97706; border-width: 1.5px;
}
QComboBox::drop-down { border: none; padding-right: 10px; }
QComboBox QAbstractItemView {
    background-color: #ffffff; color: #1a1a1a; border: 1px solid #d4cfc6;
    border-radius: 8px; padding: 6px; selection-background-color: #f5efe6; font-size: 17px;
}

QTableWidget {
    background-color: #ffffff; color: #1a1a1a; border: 1px solid #e8e5e1;
    gridline-color: #f0eee9; font-size: 17px;
    alternate-background-color: #faf9f7; selection-background-color: #f5efe6; border-radius: 12px;
}
QTableWidget::item { padding: 10px 12px; border-bottom: 1px solid #f0eee9; }
QTableWidget::item:selected { background-color: #e8e3d9; color: #1a1a1a; }
QHeaderView::section {
    background-color: #faf9f7; color: #666666; border: none;
    border-bottom: 2px solid #e8e5e1; padding: 14px 12px; font-weight: 600;
    font-size: 16px; text-transform: uppercase; letter-spacing: 0.8px;
}

QTabWidget::pane { border: 1px solid #e8e5e1; background-color: #ffffff; border-radius: 12px; padding: 6px; }
QTabBar::tab {
    padding: 12px 30px; font-size: 17px; font-weight: 500; color: #888888;
    background-color: transparent; border: none; border-bottom: 2px solid transparent; margin-right: 6px;
}
QTabBar::tab:selected { color: #1a1a1a; border-bottom: 2px solid #d97706; }
QTabBar::tab:hover:!selected { color: #555555; border-bottom-color: #d4cfc6; }

QGroupBox {
    font-size: 17px; font-weight: 600; color: #333333; border: 1px solid #e8e5e1;
    border-radius: 12px; margin-top: 20px; padding: 26px 16px 16px 16px; background-color: #ffffff;
}
QGroupBox::title { subcontrol-origin: margin; left: 18px; padding: 0 10px; color: #d97706; }

QProgressBar {
    border: 1px solid #e8e5e1; border-radius: 8px; text-align: center; font-size: 15px;
    font-weight: 600; color: #1a1a1a; background-color: #f3f1ed; height: 10px;
}
QProgressBar::chunk { border-radius: 7px; background-color: #d97706; }

QStatusBar {
    background-color: #f3f1ed; color: #888888; font-size: 16px;
    padding: 8px 16px; border-top: 1px solid #e8e5e1;
}

QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { background-color: #faf9f7; width: 10px; border-radius: 5px; margin: 2px; }
QScrollBar::handle:vertical { background-color: #d4cfc6; border-radius: 5px; min-height: 36px; }
QScrollBar::handle:vertical:hover { background-color: #b8b0a6; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { background-color: #faf9f7; height: 10px; border-radius: 5px; margin: 2px; }
QScrollBar::handle:horizontal { background-color: #d4cfc6; border-radius: 5px; min-width: 36px; }
QScrollBar::handle:horizontal:hover { background-color: #b8b0a6; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

QTextEdit, QPlainTextEdit {
    background-color: #ffffff; color: #1a1a1a; border: 1px solid #d4cfc6;
    border-radius: 10px; padding: 14px; font-size: 17px;
    selection-background-color: rgba(217,119,6,0.18);
}
QTextEdit:focus, QPlainTextEdit:focus { border-color: #d97706; }

QListWidget {
    background-color: #ffffff; color: #1a1a1a; border: 1px solid #e8e5e1;
    border-radius: 10px; font-size: 17px;
}
QListWidget::item { padding: 10px 14px; }
QListWidget::item:selected { background-color: #f5efe6; color: #1a1a1a; }

QLabel { color: #1a1a1a; }

QCheckBox, QRadioButton { color: #1a1a1a; font-size: 17px; spacing: 8px; }
QCheckBox::indicator {
    width: 18px; height: 18px; border: 1.5px solid #d4cfc6;
    border-radius: 5px; background-color: #ffffff;
}
QCheckBox::indicator:checked { background-color: #d97706; border-color: #d97706; }
QCheckBox::indicator:hover { border-color: #d97706; }

QToolTip {
    background-color: #ffffff; color: #1a1a1a; border: 1px solid #e8e5e1;
    border-radius: 8px; padding: 8px 12px; font-size: 16px;
}
"""

# ═══════════════════════════════════════════════════════════════
# DARK QSS — Warm charcoal with amber accents
# ═══════════════════════════════════════════════════════════════
DARK_QSS = """
QMainWindow {
    background-color: #1a1b1e;
    color: #e4e4e4;
}

QListWidget#sidebar {
    background-color: #141517;
    color: #999999;
    border: none;
    border-right: 1px solid #2a2b2e;
    font-size: 17px;
    padding: 12px 0;
    outline: none;
    font-weight: 500;
}
QListWidget#sidebar::item {
    height: 52px;
    padding: 0 22px;
    border-left: 3px solid transparent;
    margin: 2px 0;
    border-radius: 0px 8px 8px 0px;
}
QListWidget#sidebar::item:selected {
    background-color: #2d2518;
    color: #f0c070;
    border-left: 3px solid #d97706;
}
QListWidget#sidebar::item:hover:!selected {
    background-color: #222326;
    color: #cccccc;
}

QLabel#appTitle {
    color: #e4e4e4;
    font-size: 21px;
    font-weight: 700;
    padding: 24px 20px;
    background-color: #141517;
    border-bottom: 1px solid #2a2b2e;
    letter-spacing: 1px;
}

QFrame#card {
    background-color: #212226;
    border-radius: 14px;
    border: 1px solid #2a2b2e;
    padding: 24px;
}
QFrame#card:hover { border-color: #3d3e42; }

QLabel#cardTitle {
    font-size: 16px; font-weight: 600; color: #888888;
    text-transform: uppercase; letter-spacing: 1.5px;
}
QLabel#cardValue { font-size: 42px; font-weight: 700; color: #f0c070; }
QLabel#cardDesc { font-size: 17px; color: #777777; }

QPushButton#primaryBtn {
    background-color: #d97706; color: #ffffff; border: none;
    border-radius: 10px; padding: 10px 28px; font-size: 17px; font-weight: 600;
}
QPushButton#primaryBtn:hover { background-color: #f59b1e; }
QPushButton#primaryBtn:pressed { background-color: #b8610a; }

QPushButton#dangerBtn {
    background-color: #dc2626; color: #ffffff; border: none;
    border-radius: 10px; padding: 8px 20px; font-size: 16px; font-weight: 600;
}
QPushButton#dangerBtn:hover { background-color: #ef4444; }

QPushButton#successBtn {
    background-color: #10b981; color: #ffffff; border: none;
    border-radius: 10px; padding: 8px 20px; font-size: 16px; font-weight: 600;
}
QPushButton#successBtn:hover { background-color: #34d399; }

QPushButton {
    background-color: #2a2b2e; color: #cccccc; border: 1px solid #3d3e42;
    border-radius: 10px; padding: 8px 22px; font-size: 17px;
}
QPushButton:hover { background-color: #323336; border-color: #d97706; color: #f0c070; }
QPushButton:pressed { background-color: #252629; }

QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit {
    border: 1px solid #3d3e42; border-radius: 10px; padding: 10px 16px;
    font-size: 17px; background-color: #212226; color: #e4e4e4;
    selection-background-color: rgba(217,119,6,0.25);
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QDateEdit:focus {
    border-color: #d97706; border-width: 1.5px;
}
QComboBox::drop-down { border: none; padding-right: 10px; }
QComboBox QAbstractItemView {
    background-color: #212226; color: #e4e4e4; border: 1px solid #3d3e42;
    border-radius: 8px; padding: 6px; selection-background-color: #3d2e18; font-size: 17px;
}

QTableWidget {
    background-color: #212226; color: #e4e4e4; border: 1px solid #2a2b2e;
    gridline-color: #2a2b2e; font-size: 17px;
    alternate-background-color: #1e1f21; selection-background-color: #2d2518; border-radius: 12px;
}
QTableWidget::item { padding: 10px 12px; border-bottom: 1px solid #2a2b2e; }
QTableWidget::item:selected { background-color: #3d2e18; color: #f0c070; }
QHeaderView::section {
    background-color: #1e1f21; color: #888888; border: none;
    border-bottom: 2px solid #3d3e42; padding: 14px 12px; font-weight: 600;
    font-size: 16px; text-transform: uppercase; letter-spacing: 0.8px;
}

QTabWidget::pane { border: 1px solid #2a2b2e; background-color: #212226; border-radius: 12px; padding: 6px; }
QTabBar::tab {
    padding: 12px 30px; font-size: 17px; font-weight: 500; color: #888888;
    background-color: transparent; border: none; border-bottom: 2px solid transparent; margin-right: 6px;
}
QTabBar::tab:selected { color: #f0c070; border-bottom: 2px solid #d97706; }
QTabBar::tab:hover:!selected { color: #aaaaaa; border-bottom-color: #3d3e42; }

QGroupBox {
    font-size: 17px; font-weight: 600; color: #cccccc; border: 1px solid #2a2b2e;
    border-radius: 12px; margin-top: 20px; padding: 26px 16px 16px 16px; background-color: #212226;
}
QGroupBox::title { subcontrol-origin: margin; left: 18px; padding: 0 10px; color: #d97706; }

QProgressBar {
    border: 1px solid #2a2b2e; border-radius: 8px; text-align: center; font-size: 15px;
    font-weight: 600; color: #e4e4e4; background-color: #1a1b1e; height: 10px;
}
QProgressBar::chunk { border-radius: 7px; background-color: #d97706; }

QStatusBar {
    background-color: #141517; color: #777777; font-size: 16px;
    padding: 8px 16px; border-top: 1px solid #2a2b2e;
}

QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { background-color: #1a1b1e; width: 10px; border-radius: 5px; margin: 2px; }
QScrollBar::handle:vertical { background-color: #3d3e42; border-radius: 5px; min-height: 36px; }
QScrollBar::handle:vertical:hover { background-color: #555559; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { background-color: #1a1b1e; height: 10px; border-radius: 5px; margin: 2px; }
QScrollBar::handle:horizontal { background-color: #3d3e42; border-radius: 5px; min-width: 36px; }
QScrollBar::handle:horizontal:hover { background-color: #555559; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

QTextEdit, QPlainTextEdit {
    background-color: #212226; color: #e4e4e4; border: 1px solid #3d3e42;
    border-radius: 10px; padding: 14px; font-size: 17px;
    selection-background-color: rgba(217,119,6,0.22);
}
QTextEdit:focus, QPlainTextEdit:focus { border-color: #d97706; }

QListWidget {
    background-color: #212226; color: #e4e4e4; border: 1px solid #2a2b2e;
    border-radius: 10px; font-size: 17px;
}
QListWidget::item { padding: 10px 14px; }
QListWidget::item:selected { background-color: #3d2e18; color: #f0c070; }

QLabel { color: #e4e4e4; }

QCheckBox, QRadioButton { color: #e4e4e4; font-size: 17px; spacing: 8px; }
QCheckBox::indicator {
    width: 18px; height: 18px; border: 1.5px solid #3d3e42;
    border-radius: 5px; background-color: #212226;
}
QCheckBox::indicator:checked { background-color: #d97706; border-color: #d97706; }
QCheckBox::indicator:hover { border-color: #d97706; }

QToolTip {
    background-color: #2a2b2e; color: #e4e4e4; border: 1px solid #3d3e42;
    border-radius: 8px; padding: 8px 12px; font-size: 16px;
}
"""

# ═══════════════════════════════════════════════════════════════
# THEME MANAGER
# ═══════════════════════════════════════════════════════════════
QSS_MAP: dict[str, str] = {"light": LIGHT_QSS, "dark": DARK_QSS}
_current_theme: str = "light"

# --- Theme color map for inline widget styles ---
# light / dark
THEME_COLORS: dict[str, dict[str, str]] = {
    "light": {
        "text_primary": "#1a1a1a",
        "text_secondary": "#555555",
        "text_muted": "#888888",
        "bg_card": "#ffffff",
        "bg_input": "#ffffff",
        "bg_surface": "#faf9f7",
        "bg_sidebar": "#f3f1ed",
        "border": "#e8e5e1",
        "border_focus": "#d4cfc6",
        "accent": "#d97706",
        "accent_light": "#f5efe6",
        "success": "#059669",
        "danger": "#dc2626",
        "warning": "#d97706",
        "selection_bg": "rgba(217,119,6,0.15)",
    },
    "dark": {
        "text_primary": "#e4e4e4",
        "text_secondary": "#aaaaaa",
        "text_muted": "#777777",
        "bg_card": "#212226",
        "bg_input": "#212226",
        "bg_surface": "#1a1b1e",
        "bg_sidebar": "#141517",
        "border": "#2a2b2e",
        "border_focus": "#3d3e42",
        "accent": "#f0c070",
        "accent_light": "#3d2e18",
        "success": "#10b981",
        "danger": "#f43f5e",
        "warning": "#f59e0b",
        "selection_bg": "rgba(217,119,6,0.2)",
    },
}

RISK_COLORS: dict[str, dict[str, str]] = {
    "light": {"CRITICAL": "#dc2626", "HIGH": "#d97706", "MEDIUM": "#e5a30b", "LOW": "#059669"},
    "dark": {"CRITICAL": "#f43f5e", "HIGH": "#f59e0b", "MEDIUM": "#fbbf24", "LOW": "#10b981"},
}


def get_theme() -> str:
    return _current_theme


def set_theme(theme: str) -> None:
    global _current_theme
    if theme in QSS_MAP:
        _current_theme = theme


def toggle_theme() -> str:
    global _current_theme
    _current_theme = "dark" if _current_theme == "light" else "light"
    return _current_theme


def get_qss(theme: str | None = None) -> str:
    return QSS_MAP.get(theme or _current_theme, LIGHT_QSS)


def get_theme_color(key: str, theme: str | None = None) -> str:
    """Get a theme color for inline widget styles."""
    t = theme or _current_theme
    return THEME_COLORS.get(t, THEME_COLORS["light"]).get(key, "")


def get_risk_colors(theme: str | None = None) -> dict[str, str]:
    t = theme or _current_theme
    return RISK_COLORS.get(t, RISK_COLORS["light"])


def apply_chart_theme(theme: str | None = None) -> None:
    """Update matplotlib rcParams for current theme."""
    t = theme or _current_theme
    if t == "dark":
        plt.rcParams.update({
            "figure.facecolor": "#212226",
            "axes.facecolor": "#212226",
            "axes.edgecolor": "#2a2b2e",
            "axes.labelcolor": "#aaaaaa",
            "axes.labelsize": 13,
            "text.color": "#aaaaaa",
            "xtick.color": "#888888",
            "xtick.labelsize": 11,
            "ytick.color": "#888888",
            "ytick.labelsize": 11,
            "grid.color": "#2a2b2e",
            "grid.alpha": 0.5,
            "legend.facecolor": "#212226",
            "legend.edgecolor": "#2a2b2e",
            "legend.labelcolor": "#aaaaaa",
            "legend.fontsize": 10,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "figure.titlesize": 18,
            "figure.titleweight": "bold",
        })
    else:
        plt.rcParams.update({
            "figure.facecolor": "#ffffff",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#e8e5e1",
            "axes.labelcolor": "#555555",
            "axes.labelsize": 13,
            "text.color": "#555555",
            "xtick.color": "#888888",
            "xtick.labelsize": 11,
            "ytick.color": "#888888",
            "ytick.labelsize": 11,
            "grid.color": "#e8e5e1",
            "grid.alpha": 0.6,
            "legend.facecolor": "#ffffff",
            "legend.edgecolor": "#e8e5e1",
            "legend.labelcolor": "#555555",
            "legend.fontsize": 10,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "figure.titlesize": 18,
            "figure.titleweight": "bold",
        })


def apply_theme(app: Any, theme: str) -> None:
    """Apply theme globally: QSS + matplotlib."""
    set_theme(theme)
    app.setStyleSheet(get_qss(theme))
    apply_chart_theme(theme)


# ── Backward-compatible MAIN_STYLE ──
# (used by main_window.py for initial QSS)
MAIN_STYLE = LIGHT_QSS
