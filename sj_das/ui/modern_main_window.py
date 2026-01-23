"""
Modern Main Window - Professional Edition
Engineered for stability, performance, and "Adobe-class" user experience.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import (FluentIcon, FluentWindow, InfoBar, InfoBarPosition,
                            NavigationItemPosition, SplashScreen, Theme,
                            setTheme)

from sj_das.core.licensing import get_license_manager
from sj_das.core.services.ai_service import AIService
# Import Views
from sj_das.ui.assembler_view import AssemblerView
from sj_das.ui.digital_twin_view import DigitalTwinView
from sj_das.ui.modern_designer_view import PremiumDesignerView
from sj_das.utils.logger import logger


class ModernMainWindow(FluentWindow):
    """
    Main Application Controller.
    Manages global state, navigation, and top-level services.
    """

    def __init__(self):
        super().__init__()

        # 1. Integration: Bootstrap IoC Container
        self._bootstrap_services()

        # 2. Core Setup
        self.setWindowTitle("SJ-DAS | Professional AI Textile Suite")
        self.resize(1600, 1000)  # Professional wide default

        # 2. Appearance
        self._apply_professional_theme()

        # 3. UI Composition
        self._init_views()
        self._init_navigation()
        self._init_status_system()

        # 4. Services
        self.ai_service = AIService.instance()
        self._connect_service_signals()

        # 5. Licensing Check (Post-UI load)
        QTimer.singleShot(1000, self._check_license)

        logger.info("ModernMainWindow initialized.")

    def _bootstrap_services(self):
        """Register Enterprise Services in IoC Container."""
        from sj_das.core.feature_flags import FeatureFlagManager
        from sj_das.core.ioc_container import ServiceContainer
        from sj_das.core.services.ai_service import AIService
        from sj_das.core.services.textile_service import TextileService

        container = ServiceContainer.instance()

        # Register Feature Flags
        container.register_singleton(
            FeatureFlagManager,
            FeatureFlagManager.instance())

        # Register Core Services (Using their internal Singleton logic for now)
        # In a full migration, we would move instantiation here.
        container.register_singleton(AIService, AIService.instance())
        container.register_singleton(TextileService, TextileService.instance())

        # Phase 13: Cloud Service
        from sj_das.core.services.cloud_service import CloudService
        container.register_singleton(CloudService, CloudService.instance())

        # Phase 15: The Cortex (Collaborative AI)
        from sj_das.core.cortex.orchestrator import CortexOrchestrator
        container.register_singleton(
            CortexOrchestrator,
            CortexOrchestrator.instance())

        logger.info("Enterprise Services Bootstrapped via IoC.")

    def _apply_professional_theme(self):
        """Load the master Adobe-style stylesheet."""
        setTheme(Theme.DARK)

        style_path = Path(__file__).parent.parent / \
            "assets" / "adobe_theme.qss"
        if style_path.exists():
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            logger.warning("Adobe theme not found, falling back to default.")

    def _init_views(self):
        """Initialize main views."""
        self.designer_view = PremiumDesignerView()
        self.designer_view.setObjectName("designerView")

        self.production_view = AssemblerView()
        self.production_view.setObjectName("productionView")

        self.twin_view = DigitalTwinView()
        self.twin_view.setObjectName("twinView")

    def _init_navigation(self):
        """Build the navigation side bar."""

        # Primary Modules
        self.addSubInterface(
            self.designer_view,
            FluentIcon.EDIT,
            "Design Studio")
        self.addSubInterface(
            self.production_view,
            FluentIcon.IOT,
            "Loom Production")
        self.addSubInterface(self.twin_view, FluentIcon.ZOOM, "Digital Twin")

        self.navigationInterface.addSeparator()

        # Global Actions (File, AI, Settings)
        # Using Navigation items as action triggers
        self.navigationInterface.addItem(
            routeKey="ai_panel",
            icon=FluentIcon.ROBOT,
            text="AI Assistant",
            onClick=self._toggle_ai_panel,
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.addItem(
            routeKey="settings",
            icon=FluentIcon.SETTING,
            text="Settings",
            onClick=self._show_settings,
            position=NavigationItemPosition.BOTTOM
        )

    def _init_status_system(self):
        """Initialize status bar or notification system."""
        # FluentWindow handles this mostly, but we can add global hooks here
        pass

    def _connect_service_signals(self):
        """Connect global services to UI feedback."""
        self.ai_service.error_occurred.connect(self._show_error)
        self.ai_service.analysis_completed.connect(
            lambda r: self._show_notification(
                "Analysis Complete",
                "Head to the Design panel to see results."))

    # --- Action Handlers ---

    def _toggle_ai_panel(self):
        # Implementation depends on AI Panel architecture (Dock vs Window)
        # For now, we delegate to Designer View which likely holds the panel
        if hasattr(self.designer_view, "toggle_ai_panel"):
            self.switchTo(self.designer_view)  # Ensure view is active
            self.designer_view.toggle_ai_panel()
        else:
            self._show_notification(
                "AI Assistant",
                "Switch to Design Studio to use AI features.")

    def _show_settings(self):
        from sj_das.ui.dialogs.ai_settings_dialog import AISettingsDialog
        d = AISettingsDialog(self)
        d.exec()

    def _check_license(self):
        mgr = get_license_manager()
        if not mgr.validate():
            current_title = self.windowTitle()
            self.setWindowTitle(f"{current_title} (TRIAL)")
            self._show_notification(
                "Trial Mode",
                f"Unlicensed copy. ID: {mgr.machine_id}",
                type="warning")

    # --- Utility ---

    def _show_notification(self, title, content, type="info"):
        """Show a non-intrusive toast notification."""
        position = InfoBarPosition.TOP_RIGHT
        if type == "error":
            InfoBar.error(
                title=title,
                content=content,
                position=position,
                parent=self,
                duration=5000)
        elif type == "warning":
            InfoBar.warning(
                title=title,
                content=content,
                position=position,
                parent=self,
                duration=5000)
        else:
            InfoBar.info(
                title=title,
                content=content,
                position=position,
                parent=self,
                duration=3000)

    def _show_error(self, message):
        self._show_notification("Error", message, type="error")


def create_modern_app():
    app = QApplication(sys.argv)
    app.setApplicationName("SJ-DAS Professional")

    # High DPI Scaling for 'Retina' look
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    window = ModernMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    create_modern_app()
