"""AI学习教练页面 - 对话界面 + API 配置."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QGroupBox, QScrollArea, QComboBox, QFrame,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer

from data_layer.database import DatabaseManager
from business_layer.ai_coach import AICoach
from config import LLM_PROVIDERS, save_llm_config_to_json, reload_llm_config, LLM_CONFIG


class AICoachWidget(QWidget):
    def __init__(self, db: DatabaseManager, student_id: int, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._student_id = student_id
        self._coach = AICoach(db, student_id)
        self._api_configured = bool(LLM_CONFIG.get("api_key", ""))
        self._setup_ui()
        self._refresh_api_status()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("AI 学习教练")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        desc = QLabel("与AI教练对话，获取个性化学习建议、情绪疏导和生涯规划指导")
        desc.setStyleSheet("font-size: 18px; color: #666666;")
        layout.addWidget(desc)

        # ── API 配置栏 ──
        self._api_bar = QFrame()
        self._api_bar.setStyleSheet(
            "QFrame { background-color: #faf8f5; border: 1px solid #e8e5e1; "
            "border-radius: 10px; padding: 12px; }"
        )
        api_layout = QVBoxLayout(self._api_bar)
        api_layout.setSpacing(8)

        # 状态行
        self._api_status = QLabel()
        self._api_status.setStyleSheet("font-size: 17px; font-weight: 600;")
        api_layout.addWidget(self._api_status)

        # 设置行
        settings_row = QHBoxLayout()
        settings_row.setSpacing(8)

        settings_row.addWidget(QLabel("提供商:"))
        self._provider_combo = QComboBox()
        for key, info in LLM_PROVIDERS.items():
            self._provider_combo.addItem(info["name"], key)
        # Select current provider
        current_provider = LLM_CONFIG.get("provider", "deepseek")
        idx = self._provider_combo.findData(current_provider)
        if idx >= 0:
            self._provider_combo.setCurrentIndex(idx)
        self._provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        self._provider_combo.setStyleSheet(
            "QComboBox { padding: 4px 8px; font-size: 16px; border-radius: 6px; }"
        )
        settings_row.addWidget(self._provider_combo)

        settings_row.addWidget(QLabel("Key:"))
        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("输入API Key...")
        self._key_input.setEchoMode(QLineEdit.Password)
        current_key = LLM_CONFIG.get("api_key", "")
        if current_key and current_key not in ("your-zhipu-api-key-here", "your-dashscope-api-key-here"):
            self._key_input.setText(current_key)
        self._key_input.setStyleSheet("padding: 6px 10px; font-size: 16px; border-radius: 6px; min-width: 200px;")
        settings_row.addWidget(self._key_input)

        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet(
            "QPushButton { padding: 6px 14px; font-size: 16px; border-radius: 6px; "
            "background-color: #f0eee9; border: 1px solid #d4cfc6; }"
            "QPushButton:hover { background-color: #d4cfc6; }"
        )
        test_btn.clicked.connect(self._test_connection)
        settings_row.addWidget(test_btn)

        save_btn = QPushButton("保存")
        save_btn.setObjectName("primaryBtn")
        save_btn.setStyleSheet(
            "QPushButton { padding: 6px 16px; font-size: 16px; }"
        )
        save_btn.clicked.connect(self._save_api_config)
        settings_row.addWidget(save_btn)

        settings_row.addStretch()

        # 注册链接
        provider_key = self._provider_combo.currentData()
        provider_info = LLM_PROVIDERS.get(provider_key, {})
        register_url = provider_info.get("register_url", "")
        if register_url:
            reg_link = QLabel(f'<a href="{register_url}" style="color:#d97706;">获取免费API Key →</a>')
            reg_link.setOpenExternalLinks(True)
            reg_link.setStyleSheet("font-size: 16px;")
            settings_row.addWidget(reg_link)

        api_layout.addLayout(settings_row)
        layout.addWidget(self._api_bar)

        # ── 对话区 ──
        chat_group = QGroupBox("对话")
        chat_layout = QVBoxLayout(chat_group)
        self._chat_display = QTextEdit()
        self._chat_display.setReadOnly(True)
        self._chat_display.setStyleSheet(
            "background-color: #faf9f7; border: 1px solid #f0eee9; "
            "border-radius: 6px; padding: 12px; font-size: 18px; color: #1a1a1a;"
        )
        chat_layout.addWidget(self._chat_display)

        input_row = QHBoxLayout()
        self._input_box = QLineEdit()
        self._input_box.setPlaceholderText("输入你的问题...")
        self._input_box.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input_box)

        send_btn = QPushButton("发送")
        send_btn.setObjectName("primaryBtn")
        send_btn.clicked.connect(self._on_send)
        input_row.addWidget(send_btn)

        chat_layout.addLayout(input_row)
        layout.addWidget(chat_group, 1)

        # ── 快捷按钮 ──
        quick_group = QGroupBox("快捷操作")
        quick_layout = QHBoxLayout(quick_group)
        quick_layout.setSpacing(8)

        actions = [
            ("📚 学习建议", "study"),
            ("💪 情绪疏导", "emotion"),
            ("🎯 生涯规划", "career"),
            ("📋 成绩分析", "grades"),
            ("🌟 每日激励", "motivation"),
            ("🔄 新对话", "clear"),
        ]
        for label, action in actions:
            btn = QPushButton(label)
            btn.setStyleSheet(
                "QPushButton { background-color: #f0eee9; border: 1px solid #d4cfc6; "
                "border-radius: 4px; padding: 6px 12px; font-size: 18px; color: #333333; }"
                "QPushButton:hover { background-color: #d4cfc6; border-color: #d97706; }"
            )
            btn.clicked.connect(lambda checked, a=action: self._quick_action(a))
            quick_layout.addWidget(btn)

        quick_layout.addStretch()
        layout.addWidget(quick_group)

        # 初始问候
        self._append_message("assistant",
            "你好！我是你的AI学习教练 🤖\n\n"
            "我可以帮你：\n"
            "• 分析你的学习数据并提供建议\n"
            "• 制定个性化的学习计划\n"
            "• 提供情绪疏导和心理支持\n"
            "• 进行生涯规划指导\n\n"
            "请随时向我提问！"
        )

    def _refresh_api_status(self) -> None:
        llm = reload_llm_config()
        has_key = bool(llm.get("api_key", "") and
                       llm.get("api_key", "") not in ("your-zhipu-api-key-here", "your-dashscope-api-key-here"))
        provider = llm.get("provider", "deepseek")
        provider_name = LLM_PROVIDERS.get(provider, {}).get("name", provider)

        if has_key:
            self._api_status.setText(f"✅ 已配置: {provider_name}  |  " f'Key: {llm["api_key"][:8]}...{llm["api_key"][-4:]}')
            self._api_status.setStyleSheet("color: #059669; font-size: 16px; font-weight: 600;")
        else:
            self._api_status.setText("⚙️ 请配置 API Key 以启用 AI 教练（推荐免费 DeepSeek: platform.deepseek.com）")
            self._api_status.setStyleSheet("color: #d97706; font-size: 16px; font-weight: 600;")
        # Always show the bar so users can change config anytime
        self._api_bar.setVisible(True)

    def _on_provider_changed(self) -> None:
        key = self._provider_combo.currentData()
        info = LLM_PROVIDERS.get(key, {})
        if info.get("api_url"):
            pass  # Keep existing key input

    def _save_api_config(self) -> None:
        provider = self._provider_combo.currentData()
        api_key = self._key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "提示", "请输入 API Key")
            return

        info = LLM_PROVIDERS.get(provider, {})
        api_url = info.get("api_url", "")
        model = info.get("model", "")

        save_llm_config_to_json(provider, api_key, api_url, model)
        reload_llm_config()
        self._coach = AICoach(self._db, self._student_id)
        self._refresh_api_status()
        QMessageBox.information(self, "成功", "API 配置已保存！")

    def _test_connection(self) -> None:
        provider = self._provider_combo.currentData()
        api_key = self._key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "提示", "请先输入 API Key")
            return

        info = LLM_PROVIDERS.get(provider, {})
        api_url = info.get("api_url", "")
        model = info.get("model", "")

        from utils.llm_client import LLMClient
        client = LLMClient(api_key=api_key, api_url=api_url, model=model)
        try:
            ok = client.test_connection()
            if ok:
                QMessageBox.information(self, "成功", "连接成功！API 可用。\n点击「保存」以应用配置。")
            else:
                QMessageBox.warning(self, "失败", "连接测试失败，请检查 API Key 和网络。")
        except Exception as e:
            QMessageBox.warning(self, "失败", f"连接失败: {e}")

    def _on_send(self) -> None:
        text = self._input_box.text().strip()
        if not text:
            return
        self._input_box.setEnabled(False)
        self._append_message("user", text)
        self._input_box.clear()
        QTimer.singleShot(100, lambda: self._do_chat(text))

    def _do_chat(self, text: str) -> None:
        try:
            reply = self._coach.chat(text)
        except Exception as e:
            reply = (
                f"抱歉，AI服务暂时不可用。\n\n"
                f"错误: {e}\n\n"
                f"请在上方配置栏中设置有效的 API Key。\n"
                f"推荐使用 DeepSeek（免费注册即可获取）: https://platform.deepseek.com/"
            )
        self._append_message("assistant", reply)
        self._input_box.setEnabled(True)
        self._input_box.setFocus()

    def _quick_action(self, action: str) -> None:
        prompts = {
            "study": "请根据我的学习数据，给我3条本周的学习建议",
            "emotion": "我最近学习压力很大，有什么缓解方法吗？",
            "career": "根据我的专业和成绩，给我一些职业规划建议",
            "grades": "请分析我的成绩情况，告诉我应该在哪些方面提高",
            "motivation": "给我一些学习动力和激励的话语",
            "clear": "__CLEAR__",
        }
        if action == "clear":
            self._coach.clear_history()
            self._chat_display.clear()
            self._append_message("assistant", "对话已清空，有什么我可以帮你的吗？")
            return
        prompt = prompts.get(action, "")
        if prompt:
            self._input_box.setText(prompt)
            self._on_send()

    def _append_message(self, role: str, text: str) -> None:
        if role == "user":
            prefix = "🧑 你"
            color = "#d97706"
        else:
            prefix = "🤖 AI教练"
            color = "#059669"
        self._chat_display.append(
            f'<p><b style="color:{color}">{prefix}:</b></p>'
            f'<p style="margin-left:12px; color:#1a1a1a;">{text}</p>'
            f'<hr style="border:none; border-top:1px solid #f0eee9; margin:4px 0;">'
        )
        scrollbar = self._chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def refresh(self) -> None:
        self._refresh_api_status()
