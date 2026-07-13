"""大学生智能成长平台 - 程序入口."""
from __future__ import annotations

import importlib
import sys
import traceback

from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox

import config


def _reload_config() -> None:
    global config
    config = importlib.reload(config)


def _show_first_run_config() -> bool:
    from presentation_layer.setup_dialog import SetupDialog

    dialog = SetupDialog()
    return dialog.exec_() == QDialog.Accepted


def _create_database_connection():
    from data_layer.database import DatabaseManager

    db_config = config.DB_CONFIG
    db = DatabaseManager(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset=db_config.get("charset", "utf8mb4"),
    )
    db.execute_query("SELECT 1")
    return db


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    if not config.config_file_exists():
        if not _show_first_run_config():
            sys.exit(0)
        _reload_config()

    try:
        db = _create_database_connection()
    except Exception as e:
        retry = QMessageBox.question(
            None,
            "数据库连接失败",
            f"数据库连接失败：\n{e}\n\n是否重新配置数据库？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if retry != QMessageBox.Yes:
            traceback.print_exc()
            sys.exit(1)
        if not _show_first_run_config():
            sys.exit(1)
        _reload_config()
        db = _create_database_connection()

    try:
        from presentation_layer.main_window import MainWindow

        window = MainWindow(db)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "启动失败", f"程序启动失败:\n{e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
