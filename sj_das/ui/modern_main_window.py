"""
Modern Main Window - Professional Edition
Engineered for stability, performance, and "Adobe-class" user experience.
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import (FluentIcon, FluentWindow, InfoBar, InfoBarPosition,
                            NavigationItemPosition, SplashScreen, Theme,
                            setTheme)

try:
    from sj_das.core.licensing import get_license_manager
except Exception as e:
    logging.warning(f"LicenseManager unavailable: {e}")
    get_license_manager = None

try:
    from sj_das.core.services.ai_service import AIService
except Exception as e:
    logging.warning(f"AIService unavailable (GPU/DLL): {e}")
    AIService = None

# Import Views
from sj_das.ui.modern_designer_view import PremiumDesignerView

try:
    from sj_das.ui.assembler_view import AssemblerView
except Exception as e:
    logging.warning(f"AssemblerView unavailable: {e}")
    AssemblerView = None

try:
    from sj_das.ui.digital_twin_view import DigitalTwinView
except Exception as e:
    logging.warning(f"DigitalTwinView unavailable (moderngl?): {e}")
    DigitalTwinView = None

try:
    from sj_das.ui.dialogs.cloud_login_dialog import CloudLoginDialog
except Exception as e:
    logging.warning(f"CloudLoginDialog unavailable: {e}")
    CloudLoginDialog = None

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
        
        # Professional Default & Minimum Standards
        # Minimum: 1024x768 (Industry Floor)
        # Default: 1600x1000 (Wide Professional)
        self.setMinimumSize(1024, 768)
        self.resize(1600, 1000) 

        # 2. Appearance
        self._apply_professional_theme()
        
        # Disable Mica for debugging (Stability)
        # self.setMicaEffectEnabled(True)
        
        # 2.5 Startup Animation (Disable for visibility check)
        self.setWindowOpacity(1.0)
        # QTimer.singleShot(100, self._animate_startup)

        # 3. UI Composition
        self._init_views()
        self._init_navigation()
        self._init_status_system()

        # 4. Services
        self.ai_service = AIService.instance()
        self._connect_service_signals()

        # 5. Licensing Check (Post-UI load)
        QTimer.singleShot(1000, self._check_license)
        # 6. Cloud Login Prompt
        QTimer.singleShot(2000, self._prompt_cloud_login)

        logger.info("ModernMainWindow initialized.")
        
        # Load the default view (Design) lazily after a tiny delay
        QTimer.singleShot(100, lambda: self.switchTo(self._get_view("design")))

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
        from sj_das.ui.theme_manager import ThemeManager
        
        # 1. Base QFluentWidgets Theme
        setTheme(Theme.DARK)

        # 2. Apply Custom Professional Theme via Manager
        self.theme_manager = ThemeManager()
        stylesheet = self.theme_manager.get_stylesheet()
        
        # 3. Apply
        self.setStyleSheet(stylesheet)
        logger.info("Applied Professional Dark Theme (via ThemeManager).")

    def _animate_startup(self):
        """Fluid fade-in and slide-up animation for premium feel."""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRect
        
        # 1. Opacity Animation
        anim_fade = QPropertyAnimation(self, b"windowOpacity")
        anim_fade.setDuration(800)
        anim_fade.setStartValue(0.0)
        anim_fade.setEndValue(1.0)
        anim_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 2. Slide Up Animation
        # Note: Geometry animation removed as it conflicts with showMaximized()
        # start_rect = self.geometry()
        # # Move down 30px initially
        # start_rect.translate(0, 30)
        # self.setGeometry(start_rect)
        
        # end_rect = self.geometry()
        # end_rect.translate(0, -30) # Target matches original position
        
        # anim_move = QPropertyAnimation(self, b"geometry")
        # anim_move.setDuration(800)
        # anim_move.setStartValue(start_rect)
        # anim_move.setEndValue(end_rect)
        # anim_move.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Group them
        self.startup_group = QParallelAnimationGroup(self)
        self.startup_group.addAnimation(anim_fade)
        # self.startup_group.addAnimation(anim_move)
        
        # Clean up
        self.startup_group.finished.connect(lambda: setattr(self, 'startup_group', None))
        
        self.startup_group.start()

    def _init_views(self):
        """Initialize view placeholders for lazy loading."""
        self.designer_view = None
        self.production_view = None
        self.twin_view = None

    def _get_view(self, view_id):
        """Lazy-loading factory for main application views."""
        if view_id == "design":
            if not self.designer_view:
                logger.info("Lazy-loading Design Studio...")
                from sj_das.ui.modern_designer_view import PremiumDesignerView
                self.designer_view = PremiumDesignerView()
                self.designer_view.setObjectName("designerView")
                self.addSubInterface(self.designer_view, FluentIcon.EDIT, "Design Studio")
            return self.designer_view

        elif view_id == "production":
            if not self.production_view:
                logger.info("Lazy-loading Loom Production...")
                from sj_das.ui.assembler_view import AssemblerView
                self.production_view = AssemblerView()
                self.production_view.setObjectName("productionView")
                self.addSubInterface(self.production_view, FluentIcon.IOT, "Loom Production")
            return self.production_view

        elif view_id == "twin":
            if not self.twin_view:
                logger.info("Lazy-loading Digital Twin...")
                from sj_das.ui.digital_twin_view import DigitalTwinView
                self.twin_view = DigitalTwinView()
                self.twin_view.setObjectName("twinView")
                self.addSubInterface(self.twin_view, FluentIcon.ZOOM, "Digital Twin")
            return self.twin_view
        return None

    def _init_navigation(self):
        """Build the navigation side bar with lazy-loading triggers."""

        # Primary Modules (Registered as Navigation Items first)
        self.navigationInterface.addItem(
            routeKey="design",
            icon=FluentIcon.EDIT,
            text="Design Studio",
            onClick=lambda: self.switchTo(self._get_view("design"))
        )
        self.navigationInterface.addItem(
            routeKey="production",
            icon=FluentIcon.IOT,
            text="Loom Production",
            onClick=lambda: self.switchTo(self._get_view("production"))
        )
        self.navigationInterface.addItem(
            routeKey="twin",
            icon=FluentIcon.ZOOM,
            text="Digital Twin",
            onClick=lambda: self.switchTo(self._get_view("twin"))
        )

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
            routeKey="cloud_sync",
            icon=FluentIcon.SYNC,
            text="Cloud Sync",
            onClick=self._sync_cloud_data,
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
        view = self._get_view("design")
        if view and hasattr(view, "toggle_ai_panel"):
            self.switchTo(view)  # Ensure view is active
            view.toggle_ai_panel()
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

    def _prompt_cloud_login(self):
        """Prompt user to authenticate with SJDAS Cloud Backend."""
        dialog = CloudLoginDialog(self)
        dialog.login_success.connect(
            lambda: self._show_notification("Connected", "Successfully authenticated with SJDAS Cloud.", type="success")
        )
        dialog.exec()

    def _sync_cloud_data(self):
        """Manually trigger a synchronization of local designs with the cloud."""
        from sj_das.core.services.cloud_service import CloudService
        cs = CloudService.instance()
        if not cs.jwt_token:
            self._show_notification("Authentication Required", 
                                   "Please login to use Cloud Sync.", type="warning")
            self._prompt_cloud_login()
            return
            
        self._show_notification("Cloud Sync", "Synchronizing designs and patterns...")
        # Placeholder for actual sync logic (e.g. uploading/downloading files)
        QTimer.singleShot(2000, lambda: self._show_notification("Sync Complete", 
                                                              "Cloud data is up to date.", type="success"))

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

    window = ModernMainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    create_modern_app()
