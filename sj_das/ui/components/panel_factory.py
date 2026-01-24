
import logging

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import PushButton as FluentPushButton
from qfluentwidgets import TabWidget

from sj_das.ui.components.layers_panel import LayersPanel
from sj_das.ui.components.panels import HistoryPanel, PalettePanel
# Components
from sj_das.ui.navigator_widget import NavigatorWidget
from sj_das.ui.palette_widget import YarnPaletteWidget
from sj_das.ui.weave_library import WeaveLibraryWidget

logger = logging.getLogger("SJ_DAS.PanelFactory")

COLORS = {
    'bg_primary': '#0F172A',
    'bg_secondary': '#1E293B',
    'border_subtle': '#334155',
    'text_primary': '#E2E8F0',
    'text_secondary': '#94A3B8',
}


class PanelFactory:
    """
    Factory to create application panels (Right Sidebar).
    Decouples UI construction from the main controller.
    """

    def __init__(self, view):
        self.view = view
        self.editor = view.editor

    def create_right_panels(self) -> QFrame:
        """Create professional right panels container"""
        from PyQt6.QtWidgets import QScrollArea
        from PyQt6.QtCore import Qt

        right_panels = QScrollArea()
        right_panels.setObjectName("rightPanelsScroll")
        right_panels.setWidgetResizable(True)
        right_panels.setFrameShape(QFrame.Shape.NoFrame)
        right_panels.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for content
        container = QFrame()
        container.setObjectName("rightPanels")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tabs
        self.view.tabs = TabWidget()  # Attach to view for accessibility if needed
        tabs = self.view.tabs
        
        # Allow Tabs to expand/shrink
        tabs.setMinimumHeight(600) # Ensure it doesn't shrink too much inside scroll

        # Create panels
        tabs.addTab(self.create_navigator_panel(), "Navigator")
        tabs.addTab(self.create_colors_panel(), "Colors")
        tabs.addTab(self.create_yarn_panel(), "Yarn")
        tabs.addTab(self.create_weaves_panel(), "Weaves")
        tabs.addTab(self.create_ai_panel(), "AI")
        tabs.addTab(self.create_layers_panel(), "Layers")
        tabs.addTab(self.create_history_panel(), "History")
        tabs.addTab(self.create_pattern_library_panel(), "Patterns")

        layout.addWidget(tabs)
        
        right_panels.setWidget(container)
        
        # Constraints are now on the ScrollArea
        right_panels.setMinimumWidth(50)   
        right_panels.setMaximumWidth(600)  
        
        return right_panels

    def create_pattern_library_panel(self):
        from sj_das.ui.components.pattern_library import PatternLibraryWidget
        self.view.pattern_library = PatternLibraryWidget(parent=self.view)
        return self.view.pattern_library

    def create_navigator_panel(self):
        self.view.navigator = NavigatorWidget(self.editor)
        return self.view.navigator

    def create_yarn_panel(self):
        from sj_das.core.services.textile_service import TextileService
        ts = TextileService.instance()

        self.view.yarn_panel = YarnPaletteWidget()
        # Inject Service
        if hasattr(self.view.yarn_panel, 'set_service'):
            self.view.yarn_panel.set_service(ts)

        self.view.yarn_panel.color_selected.connect(self.view.on_yarn_selected)
        return self.view.yarn_panel

    def create_weaves_panel(self):
        from sj_das.core.services.textile_service import TextileService
        ts = TextileService.instance()

        self.view.weaves_panel = WeaveLibraryWidget()

        # Inject Service data
        # WeaveLibraryWidget usually loads its own data.
        # We should update it to use the Service's data if possible,
        # or at least expose the service to it.
        if hasattr(self.view.weaves_panel, 'set_service'):
            self.view.weaves_panel.set_service(ts)

        self.view.weaves_panel.weave_selected.connect(
            self.view.on_weave_selected)
        return self.view.weaves_panel

    def create_ai_panel(self):
        # Professional AI Chat Interface
        from sj_das.ui.components.ai_chat_panel import AIChatPanel
        panel = AIChatPanel()
        panel.action_requested.connect(self.view.on_ai_action)

        # We can also keep the buttons if needed, wrapping them
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Chat takes most space
        layout.addWidget(panel)

        # Add quick action buttons below chat
        btn_layout = QVBoxLayout()
        btn_layout.setContentsMargins(10, 0, 10, 10)

        btn_generate = FluentPushButton("✨ Generate Variations")
        btn_generate.clicked.connect(self.view.generate_variations)
        btn_layout.addWidget(btn_generate)

        layout.addLayout(btn_layout)

        return container

    def create_layers_panel(self):
        self.view.layers_panel = LayersPanel()
        self.view.layers_panel.layer_visibility_changed.connect(
            self.editor.set_layer_visibility)
        self.view.layers_panel.layer_opacity_changed.connect(
            self.editor.set_layer_opacity)
        return self.view.layers_panel

    def create_history_panel(self):
        return HistoryPanel(self.editor)

    def create_colors_panel(self):
        return PalettePanel(self.editor)
