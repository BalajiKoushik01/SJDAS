
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
        """
        A comprehensive, categorized AI Toolbox panel.
        Every implemented AI method in modern_designer_view.py is wired here.
        """
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QScrollArea, QSizePolicy
        from qfluentwidgets import (FluentIcon as FIF,
                                     PrimaryPushButton, PushButton,
                                     SubtitleLabel, TitleLabel)

        container = QWidget()
        container.setObjectName("aiToolboxPanel")
        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(44)
        header.setObjectName("panelHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)
        lbl = SubtitleLabel("🤖  AI Toolbox")
        lbl.setObjectName("panelTitle")
        header_layout.addWidget(lbl)
        outer_layout.addWidget(header)

        # Scrollable area for all buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        inner = QWidget()
        inner.setObjectName("aiToolboxInner")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        v = self.view  # shorthand

        # ── GENERATION ────────────────────────────────────────────────
        layout.addWidget(self._section_label("Generation"))

        btn = PrimaryPushButton("✨  AI Pattern Generator")
        btn.setIcon(FIF.ROBOT)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.show_ai_pattern_gen)
        layout.addWidget(btn)

        btn = PushButton("↗️  Generate Variations")
        btn.setIcon(FIF.TILES)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.generate_variations)
        layout.addWidget(btn)

        btn = PushButton("✏️  Sketch → Design (ControlNet)")
        btn.setIcon(FIF.PENCIL_INK)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.generate_from_sketch_controlnet)
        layout.addWidget(btn)

        # ── SEGMENTATION & SELECTION ──────────────────────────────────
        layout.addWidget(self._section_label("Segmentation & Selection"))

        btn = PrimaryPushButton("🧩  Auto-Segment (SAM2)")
        btn.setIcon(FIF.PHOTO)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.auto_segment)
        layout.addWidget(btn)

        btn = PushButton("🪄  Smart Select (Click)")
        btn.setIcon(FIF.IOT)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.activate_smart_select)
        layout.addWidget(btn)

        btn = PushButton("🔍  Smart Find (OWL-ViT)")
        btn.setIcon(FIF.SEARCH)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.open_smart_search)
        layout.addWidget(btn)

        btn = PushButton("🧹  Magic Eraser (AI)")
        btn.setIcon(FIF.DELETE)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.activate_magic_eraser)
        layout.addWidget(btn)

        btn = PushButton("🚫  Remove Background")
        btn.setIcon(FIF.CUT)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_remove_background)
        layout.addWidget(btn)

        # ── ENHANCEMENT ───────────────────────────────────────────────
        layout.addWidget(self._section_label("Enhancement"))

        btn = PrimaryPushButton("⬆️  Upscale 4x (Real-ESRGAN)")
        btn.setIcon(FIF.ZOOM_IN)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_ai_upscale_4x)
        layout.addWidget(btn)

        btn = PushButton("⬆️  Upscale 2x")
        btn.setIcon(FIF.ZOOM_IN)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_ai_upscale_2x)
        layout.addWidget(btn)

        btn = PushButton("🎨  Colorize B&W")
        btn.setIcon(FIF.PALETTE)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_colorization)
        layout.addWidget(btn)

        btn = PushButton("🖼️  Style Transfer")
        btn.setIcon(FIF.BRUSH)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_style_transfer)
        layout.addWidget(btn)

        btn = PushButton("🌊  Depth Map (3D Relief)")
        btn.setIcon(FIF.GLOBE)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_depth_map)
        layout.addWidget(btn)

        # ── TEXTILE AI ─────────────────────────────────────────────────
        layout.addWidget(self._section_label("Textile AI"))

        btn = PrimaryPushButton("👗  Human Draping (Parsing)")
        btn.setIcon(FIF.PEOPLE)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_human_parsing)
        layout.addWidget(btn)

        btn = PushButton("🧵  Apply Weave Simulation")
        btn.setIcon(FIF.TILES)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.apply_weave)
        layout.addWidget(btn)

        btn = PushButton("🔬  Fabric Simulation")
        btn.setIcon(FIF.CERTIFICATE)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.show_fabric_simulation)
        layout.addWidget(btn)

        btn = PushButton("🐛  Defect Scan")
        btn.setIcon(FIF.INFO)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.show_defect_scan)
        layout.addWidget(btn)

        btn = PushButton("🔁  Detect Pattern")
        btn.setIcon(FIF.TILES)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.detect_pattern_from_image)
        layout.addWidget(btn)

        btn = PushButton("💰  Costing Report")
        btn.setIcon(FIF.MARKET)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.show_costing_report)
        layout.addWidget(btn)

        btn = PushButton("🧱  Export to Loom (.WIF)")
        btn.setIcon(FIF.SAVE)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.export_to_loom)
        layout.addWidget(btn)

        btn = PushButton("🏛  3D Fabric View")
        btn.setIcon(FIF.DEVELOPER_TOOLS)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.show_3d_fabric_view)
        layout.addWidget(btn)

        # ── VISION & ANALYSIS ──────────────────────────────────────────
        layout.addWidget(self._section_label("Vision & Analysis"))

        btn = PushButton("🧪  Run AI Analysis")
        btn.setIcon(FIF.ROBOT)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.run_ai_analysis)
        layout.addWidget(btn)

        btn = PushButton("📸  Extract Sketch (Vision)")
        btn.setIcon(FIF.PHOTO)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.extract_sketch_ai)
        layout.addWidget(btn)

        btn = PushButton("🖥️  Recover from Screenshot")
        btn.setIcon(FIF.CAMERA)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.recover_design_from_screenshot)
        layout.addWidget(btn)

        # ── ASSISTANT ─────────────────────────────────────────────────
        layout.addWidget(self._section_label("Assistant"))

        btn = PrimaryPushButton("🎤  Voice Agent")
        btn.setIcon(FIF.MICROPHONE)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.activate_voice_control)
        layout.addWidget(btn)

        btn = PushButton("💬  AI Chat Assistant")
        btn.setIcon(FIF.CHAT)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.activate_ai_chat)
        layout.addWidget(btn)

        btn = PushButton("🤝  Toggle AI Copilot")
        btn.setIcon(FIF.ROBOT)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.toggle_copilot)
        layout.addWidget(btn)

        btn = PushButton("☁️  Backup to Cloud")
        btn.setIcon(FIF.CLOUD)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(v.backup_to_cloud)
        layout.addWidget(btn)

        layout.addStretch()
        scroll.setWidget(inner)
        outer_layout.addWidget(scroll)

        return container

    @staticmethod
    def _section_label(text: str) -> QLabel:
        """Create a styled section divider label."""
        lbl = QLabel(f"  {text}")
        lbl.setFixedHeight(26)
        lbl.setStyleSheet(
            "background: #1E3A8A; color: #BAE6FD; font-size: 11px; "
            "font-weight: 700; letter-spacing: 0.8px; "
            "border-radius: 4px; padding-left: 6px; "
            "text-transform: uppercase;"
        )
        return lbl

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
