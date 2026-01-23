"""
AI Settings Dialog for configuring AI providers including MiniMax M2.1.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QSpinBox, QTabWidget,
                             QVBoxLayout, QWidget)
from qfluentwidgets import (ComboBox, LineEdit, PushButton, SpinBox,
                            SwitchButton)

from sj_das.core.ai_config import get_ai_config


class AISettingsDialog(QDialog):
    """Dialog for configuring AI providers and settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_ai_config()
        self.setWindowTitle("AI Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🤖 AI Provider Configuration")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tab widget for different providers
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2B2B2B;
            }
            QTabBar::tab {
                background: #1E1E1E;
                color: #E2E8F0;
                padding: 8px 16px;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background: #6366F1;
            }
        """)

        # MiniMax Tab
        minimax_tab = self._create_minimax_tab()
        tabs.addTab(minimax_tab, "MiniMax M2.1")

        # Gemini Tab
        gemini_tab = self._create_gemini_tab()
        tabs.addTab(gemini_tab, "Google Gemini")

        # HuggingFace Tab
        hf_tab = self._create_huggingface_tab()
        tabs.addTab(hf_tab, "HuggingFace")

        # General Settings Tab
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "General")

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _create_minimax_tab(self) -> QWidget:
        """Create MiniMax configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # Info
        info = QLabel(
            "Configure MiniMax M2.1 for intelligent design analysis and recommendations.")
        info.setWordWrap(True)
        info.setStyleSheet(
            "color: #94A3B8; padding: 10px; background: #1E293B; border-radius: 5px;")
        layout.addWidget(info)

        # API Key Group
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()

        self.minimax_api_key = QLineEdit()
        self.minimax_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.minimax_api_key.setPlaceholderText("Enter your MiniMax API key")
        api_layout.addRow("API Key:", self.minimax_api_key)

        self.minimax_endpoint = QLineEdit()
        self.minimax_endpoint.setPlaceholderText(
            "https://api.minimax.io/v1/text/chatcompletion_v2")
        api_layout.addRow("Endpoint:", self.minimax_endpoint)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Settings Group
        settings_group = QGroupBox("Model Settings")
        settings_layout = QFormLayout()

        self.minimax_temperature = QSpinBox()
        self.minimax_temperature.setRange(0, 100)
        self.minimax_temperature.setValue(70)
        self.minimax_temperature.setSuffix(" (0.7)")
        settings_layout.addRow("Temperature:", self.minimax_temperature)

        self.minimax_max_tokens = QSpinBox()
        self.minimax_max_tokens.setRange(256, 4096)
        self.minimax_max_tokens.setValue(2048)
        settings_layout.addRow("Max Tokens:", self.minimax_max_tokens)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Enable/Disable
        enable_layout = QHBoxLayout()
        enable_layout.addWidget(QLabel("Enable MiniMax:"))
        self.minimax_enabled = QCheckBox()
        self.minimax_enabled.setChecked(False)
        enable_layout.addWidget(self.minimax_enabled)
        enable_layout.addStretch()
        layout.addLayout(enable_layout)

        # Help
        help_label = QLabel(
            '<a href="https://api.minimax.io">Get API Key</a> | '
            '<a href="file:///docs/MINIMAX_INTEGRATION.md">Documentation</a>'
        )
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("color: #6366F1; padding: 10px;")
        layout.addWidget(help_label)

        layout.addStretch()
        return widget

    def _create_gemini_tab(self) -> QWidget:
        """Create Gemini configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "Configure Google Gemini for multimodal AI capabilities.")
        info.setWordWrap(True)
        info.setStyleSheet(
            "color: #94A3B8; padding: 10px; background: #1E293B; border-radius: 5px;")
        layout.addWidget(info)

        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()

        self.gemini_api_key = QLineEdit()
        self.gemini_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_api_key.setPlaceholderText("Enter your Gemini API key")
        api_layout.addRow("API Key:", self.gemini_api_key)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        enable_layout = QHBoxLayout()
        enable_layout.addWidget(QLabel("Enable Gemini:"))
        self.gemini_enabled = QCheckBox()
        enable_layout.addWidget(self.gemini_enabled)
        enable_layout.addStretch()
        layout.addLayout(enable_layout)

        layout.addStretch()
        return widget

    def _create_huggingface_tab(self) -> QWidget:
        """Create HuggingFace configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "Configure HuggingFace for Stable Diffusion and other models.")
        info.setWordWrap(True)
        info.setStyleSheet(
            "color: #94A3B8; padding: 10px; background: #1E293B; border-radius: 5px;")
        layout.addWidget(info)

        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()

        self.hf_api_key = QLineEdit()
        self.hf_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.hf_api_key.setPlaceholderText(
            "Enter your HuggingFace API key (optional)")
        api_layout.addRow("API Key:", self.hf_api_key)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        enable_layout = QHBoxLayout()
        enable_layout.addWidget(QLabel("Enable HuggingFace:"))
        self.hf_enabled = QCheckBox()
        enable_layout.addWidget(self.hf_enabled)
        enable_layout.addStretch()
        layout.addLayout(enable_layout)

        layout.addStretch()
        return widget

    def _create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Provider Priority
        priority_group = QGroupBox("Provider Priority")
        priority_layout = QVBoxLayout()

        priority_info = QLabel(
            "Set the order in which AI providers are tried (1 = highest priority):")
        priority_info.setWordWrap(True)
        priority_layout.addWidget(priority_info)

        # MiniMax Priority
        minimax_priority_layout = QHBoxLayout()
        minimax_priority_layout.addWidget(QLabel("MiniMax M2.1:"))
        self.minimax_priority = QSpinBox()
        self.minimax_priority.setRange(1, 10)
        self.minimax_priority.setValue(1)
        minimax_priority_layout.addWidget(self.minimax_priority)
        minimax_priority_layout.addStretch()
        priority_layout.addLayout(minimax_priority_layout)

        # Gemini Priority
        gemini_priority_layout = QHBoxLayout()
        gemini_priority_layout.addWidget(QLabel("Google Gemini:"))
        self.gemini_priority = QSpinBox()
        self.gemini_priority.setRange(1, 10)
        self.gemini_priority.setValue(2)
        gemini_priority_layout.addWidget(self.gemini_priority)
        gemini_priority_layout.addStretch()
        priority_layout.addLayout(gemini_priority_layout)

        # HuggingFace Priority
        hf_priority_layout = QHBoxLayout()
        hf_priority_layout.addWidget(QLabel("HuggingFace:"))
        self.hf_priority = QSpinBox()
        self.hf_priority.setRange(1, 10)
        self.hf_priority.setValue(3)
        hf_priority_layout.addWidget(self.hf_priority)
        hf_priority_layout.addStretch()
        priority_layout.addLayout(hf_priority_layout)

        priority_group.setLayout(priority_layout)
        layout.addWidget(priority_group)

        # Fallback Settings
        fallback_group = QGroupBox("Fallback Settings")
        fallback_layout = QVBoxLayout()

        self.enable_fallback = QCheckBox(
            "Enable automatic fallback to next provider on error")
        self.enable_fallback.setChecked(True)
        fallback_layout.addWidget(self.enable_fallback)

        self.enable_pollinations = QCheckBox(
            "Enable Pollinations.ai as final fallback (no API key required)")
        self.enable_pollinations.setChecked(True)
        fallback_layout.addWidget(self.enable_pollinations)

        fallback_group.setLayout(fallback_layout)
        layout.addWidget(fallback_group)

        layout.addStretch()
        return widget

    def load_settings(self):
        """Load current settings from config."""
        # MiniMax
        minimax_config = self.config.get_provider_config('minimax')
        if minimax_config:
            api_key = minimax_config.api_key
            if api_key:
                self.minimax_api_key.setText(api_key)
            self.minimax_endpoint.setText(minimax_config.endpoint)
            self.minimax_enabled.setChecked(minimax_config.enabled)
            self.minimax_priority.setValue(minimax_config.priority)

        # Gemini
        gemini_config = self.config.get_provider_config('gemini')
        if gemini_config:
            api_key = gemini_config.api_key
            if api_key:
                self.gemini_api_key.setText(api_key)
            self.gemini_enabled.setChecked(gemini_config.enabled)
            self.gemini_priority.setValue(gemini_config.priority)

        # HuggingFace
        hf_config = self.config.get_provider_config('huggingface')
        if hf_config:
            api_key = hf_config.api_key
            if api_key:
                self.hf_api_key.setText(api_key)
            self.hf_enabled.setChecked(hf_config.enabled)
            self.hf_priority.setValue(hf_config.priority)

    def save_settings(self):
        """Save settings to config."""
        try:
            # Save MiniMax
            minimax_key = self.minimax_api_key.text().strip()
            if minimax_key:
                self.config.set_api_key('minimax', minimax_key)
            self.config.enable_provider(
                'minimax', self.minimax_enabled.isChecked())
            self.config.set_provider_priority(
                'minimax', self.minimax_priority.value())

            # Save Gemini
            gemini_key = self.gemini_api_key.text().strip()
            if gemini_key:
                self.config.set_api_key('gemini', gemini_key)
            self.config.enable_provider(
                'gemini', self.gemini_enabled.isChecked())
            self.config.set_provider_priority(
                'gemini', self.gemini_priority.value())

            # Save HuggingFace
            hf_key = self.hf_api_key.text().strip()
            if hf_key:
                self.config.set_api_key('huggingface', hf_key)
            self.config.enable_provider(
                'huggingface', self.hf_enabled.isChecked())
            self.config.set_provider_priority(
                'huggingface', self.hf_priority.value())

            QMessageBox.information(
                self,
                "Settings Saved",
                "AI provider settings have been saved successfully!\n\n"
                "Restart the application for changes to take full effect."
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )

    def test_connection(self):
        """Test connection to enabled providers."""
        results = []

        # Test MiniMax
        if self.minimax_enabled.isChecked():
            api_key = self.minimax_api_key.text().strip()
            if api_key:
                try:
                    from sj_das.core.engines.llm.minimax_engine import (
                        MiniMaxConfig, MiniMaxEngine)
                    config = MiniMaxConfig(api_key=api_key)
                    engine = MiniMaxEngine(config)
                    success = engine.configure(api_key)
                    if success:
                        results.append("✓ MiniMax M2.1: Connected")
                    else:
                        results.append("✗ MiniMax M2.1: Connection failed")
                except Exception as e:
                    results.append(f"✗ MiniMax M2.1: {str(e)}")
            else:
                results.append("⚠ MiniMax M2.1: No API key provided")

        # Show results
        if results:
            QMessageBox.information(
                self,
                "Connection Test",
                "\n".join(results)
            )
        else:
            QMessageBox.warning(
                self,
                "Connection Test",
                "No providers enabled for testing."
            )
