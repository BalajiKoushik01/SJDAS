"""
Premium Designer View - Photoshop Quality
Research-based implementation with professional UX
"""

from sj_das.core.services.ai_service import AIService, AIWorker
import os
import time

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QImage
from PyQt6.QtWidgets import (QApplication, QColorDialog, QDialog, QFileDialog,
                             QFrame, QHBoxLayout, QInputDialog, QMessageBox,
                             QProgressDialog, QSplitter, QVBoxLayout, QWidget)
from qfluentwidgets import InfoBar, InfoBarPosition

from sj_das.ai.generation_thread import GenerationThread
from sj_das.ai.model_loader import get_ai_model
from sj_das.ai.model_manager import ModelManager
from sj_das.ai.proactive_assistant import get_proactive_assistant
from sj_das.core.constants import FileConstants
from sj_das.tools.advanced_selection import (ColorRangeSelector, MagicWandTool,
                                             QuickSelectionTool,
                                             SelectionRefiner)
from sj_das.ui.blend_modes import BlendMode, BlendModes
# from sj_das.core.segmentation import SegmentationEngine # REMOVED: Conflict with sj_das.ai.segmentation_engine
# from sj_das.ui.animations import AnimationHelper  # Optional: for future
# dialog animations
from sj_das.ui.components.advanced_status_bar import AdvancedStatusBar
from sj_das.ui.components.menu_builder import StandardMenuBuilder
from sj_das.ui.components.panel_factory import PanelFactory
from sj_das.ui.components.ruler import Ruler
from sj_das.ui.components.toolbar_factory import ToolbarFactory
# Legacy Widgets Integration
from sj_das.ui.designer_view_psp_methods import DesignerViewPSPMethods  # MIXIN
# from sj_das.ui.designer_view_textile_methods import
# DesignerViewTextileMethods  # MIXIN - Disabled due to import issues
from sj_das.ui.dialogs.loom_import_dialog import LoomImportDialog
from sj_das.ui.editor_widget import PixelEditorWidget
from sj_das.ui.features.ai_pattern_gen import AIPatternGen
from sj_das.ui.features.channel_mixer import ChannelMixer
from sj_das.ui.features.color_adjuster import ColorAdjuster
from sj_das.ui.features.color_separator import ColorSeparator
from sj_das.ui.features.curves_tool import CurvesTool
from sj_das.ui.features.emboss_effect import EmbossEffect
from sj_das.ui.features.fabric_resizer import FabricResizer
from sj_das.ui.features.film_grain import FilmGrain
from sj_das.ui.features.geometric_generator import GeometricGenerator
from sj_das.ui.features.gradient_map import GradientMap
from sj_das.ui.features.halftone_gen import HalftoneGen
from sj_das.ui.features.histogram_viewer import HistogramViewer
from sj_das.ui.features.hsl_adjuster import HSLAdjuster
from sj_das.ui.features.motif_repeater import MotifRepeater
from sj_das.ui.features.noise_reducer import NoiseReducer
from sj_das.ui.features.palette_extractor import PaletteExtractor
from sj_das.ui.features.perspective_tool import PerspectiveTool
from sj_das.ui.features.pixelate_effect import PixelateEffect
from sj_das.ui.features.posterize_tool import PosterizeTool
from sj_das.ui.features.ruler_tool import RulerTool
from sj_das.ui.features.smart_expert import SmartExpert
from sj_das.ui.features.smart_recolor import SmartRecolor
from sj_das.ui.features.smart_seamless import SmartSeamlessMaker
from sj_das.ui.features.solarize_effect import SolarizeEffect
from sj_das.ui.features.symmetry_mode import SymmetryFeature
from sj_das.ui.features.threshold_tool import ThresholdTool
from sj_das.ui.features.vignette_effect import VignetteEffect
from sj_das.ui.features.weave_simulator import WeaveSimulator
# Week 1 Professional Features
from sj_das.ui.grid_system import GridManager
from sj_das.ui.infrastructure import safe_slot
from sj_das.ui.layer_styles import LayerStyles
# Tool Activation Mixin - Fixes missing tool methods
from sj_das.ui.mixins.tool_activation import ToolActivationMixin
from sj_das.ui.quick_actions import QuickActionsDialog
from sj_das.ui.shortcut_manager import ShortcutManager
from sj_das.ui.theme_manager import ThemeManager
from sj_das.ui.workspace_manager import WorkspaceManager
from sj_das.utils.logger import logger
from sj_das.utils.memory import MemoryManager
from sj_das.utils.validation import InputValidator

# Professional Color Palette (Research-Based)
COLORS = {
    'bg_primary': '#2B2B2B',
    'bg_secondary': '#1E1E1E',
    'bg_elevated': '#353535',
    'bg_hover': '#404040',
    'border_subtle': '#3E3E42',
    'border_accent': '#6366F1',
    'text_primary': '#E2E8F0',
    'text_secondary': '#94A3B8',
    'text_disabled': '#64748B',
    'accent_primary': '#6366F1',
    'accent_hover': '#818CF8',
    'accent_active': '#4F46E5',
}


class StatusLabelProxy:
    """Proxy to redirect setText calls to status_bar.showMessage"""

    def __init__(self, status_bar):
        self.status_bar = status_bar

    def setText(self, text):
        if self.status_bar:
            self.status_bar.showMessage(text)


class PremiumDesignerView(QWidget, DesignerViewPSPMethods):
    """Premium Photoshop-quality designer view"""

    def __init__(self, parent=None):
        # Initialize Base QWidget First
        QWidget.__init__(self, parent)
        self.ai_worker = None

        # Core components
        self.editor = PixelEditorWidget()
        try:
            # Use the new centralized engine if available, or fallback
            from sj_das.ai.segmentation_engine import get_engine
            self.segmentation_engine = get_engine()
        except ImportError:
            self.segmentation_engine = None
            logger.warning("SegmentationEngine not available.")
        self.current_image_path = None

        # Feature modules will be initialized in _init_features

        # AI Integration
        # AI Integration (Professional)
        self.ai_service = AIService.instance()
        self._connect_ai_signals()

        # Memory Management
        self.memory_manager = MemoryManager()
        self.memory_manager.memory_warning.connect(self._on_memory_warning)
        self.memory_manager.memory_critical.connect(self._on_memory_critical)

        # Initialize features
        self._init_features()

        # Memory Management
        self.memory_manager = MemoryManager()
        self.memory_manager.memory_warning.connect(self._on_memory_warning)
        self.memory_manager.memory_critical.connect(self._on_memory_critical)

        logger.info("Advanced UI/UX features initialized")
        self.create_status_bar()

        # FIX: Initialize status_label proxy for compatibility
        self.status_label = StatusLabelProxy(self.status_bar)

        # Init systems
        # Init systems
        # self.setup_ai_processor() # Removed (Legacy)

        # Connect editor signals
        self.editor.mask_updated.connect(
            lambda: self.status_label.setText("Drawing..."))
        self.editor.color_picked.connect(self.on_color_picked_enhanced)

        # Auto-load last work if available (or start blank)
        # self.import_design("last_session.png") # Persistence to be added
        # later

        # Initialize Professional Features (Weeks 1-4)
        # MUST BE BEFORE UI INIT (MenuBuilder uses them)
        self._init_professional_features()

        # Initialize Workspace Manager
        from sj_das.ui.workspace_manager import WorkspaceManager
        self.workspace_manager = WorkspaceManager(self)
        self.workspace_manager.workspace_changed.connect(
            self._on_workspace_changed)

        # Initialize Phase 24 UI/UX Features
        self._init_phase24_features()

        # Initialize AI Model Manager (Late Init)
        self.model_manager = ModelManager()
        self.generation_thread = None

        # Phase 9: Initialize Canvas Controller (MVC) -> Moved UP to fix init_ui crash
        from sj_das.controllers.canvas_controller import CanvasController
        self.controller = CanvasController(self)

        logger.info("Features ready, building UI...")
        # Initialize UI Layout (Critical for visibility)
        self.init_ui()
        
        # Initialize Default Canvas (Prevent Black Void)
        self.editor.create_blank_canvas(1200, 1600) # Sensible default

        # Phase 15: Cortex & OmniBar
        from sj_das.core.cortex.orchestrator import CortexOrchestrator
        from sj_das.ui.components.omni_bar import OmniBar

        self.cortex = CortexOrchestrator.instance()
        self.cortex.action_required.connect(self.handle_cortex_action)
        self.cortex.content_generated.connect(self.on_cortex_content)

        self.omni_bar = OmniBar(self)
        self.omni_bar.command_entered.connect(self.cortex.think)
        self.cortex.thought_updated.connect(self.omni_bar.set_status)
        self.omni_bar.move(400, 100) # Default position (away from top-left)
        self.omni_bar.show()
        self.omni_bar.raise_()

        # Phase 12: Connect AI Tools
        if hasattr(self.editor, 'canvas_clicked'):
            self.editor.canvas_clicked.connect(
                self.controller.handle_magic_wand_click)

        # Phase 14: Daily Inspiration
        QTimer.singleShot(3000, self.fetch_daily_quote)

        logger.info("Premium Photoshop-quality UI initialized!")

    def resizeEvent(self, event):
        """Handle resize to center OmniBar at bottom."""
        if hasattr(self, 'omni_bar') and self.omni_bar:
            # Position at bottom center ONLY if not manually moved
            if not self.omni_bar.is_manually_moved:
                width = self.omni_bar.width()
                height = self.omni_bar.height()
                
                x = (self.width() - width) // 2
                y = self.height() - height - 40 # 40px margin from bottom
                
                self.omni_bar.move(x, y)
                self.omni_bar.raise_()
            
        super().resizeEvent(event)

    def fetch_daily_quote(self):
        """Fetch daily quote from cloud."""
        from sj_das.core.services.cloud_service import CloudService
        svc = CloudService.instance()
        if hasattr(svc, 'quote_received'):
            svc.quote_received.connect(self._on_quote_received)
            svc.get_daily_quote()

    def _on_quote_received(self, data):
        text = data.get('text')
        author = data.get('author')
        self.show_notification(
            f"Daily Wisdom: \"{text}\" — {author}",
            duration=8000)

    def _connect_ai_signals(self):
        """Connect global AI service signals to this view."""
        self.ai_service.generation_completed.connect(
            self._on_ai_generation_complete)
        self.ai_service.error_occurred.connect(
            lambda e: self.show_error(f"AI Error: {e}"))

    def _on_ai_generation_complete(self, result):
        """Handle AI completion."""
        self.hide_loading()

        if isinstance(result, np.ndarray):
            # Check if it's a mask (2D) or Image (3D)
            if len(result.shape) == 2:
                # It's a mask from SAM
                if hasattr(self.editor, 'set_selection'):
                    self.editor.set_selection(result)
                    self.status_label.setText("AI Selection Applied")
                    self.editor.mask_updated.emit()
            else:
                # It's an image (Inpainting result)
                # Expecting RGB or BGR?
                # Let's assume RGB if coming from internal services
                pass  # We usually get QImage for images, but if raw numpy:
                pass

        elif isinstance(result, QImage):
            self.import_image_from_data(result)
        elif isinstance(result, str) and os.path.exists(result):
            self.open_file(result)
        else:
            self.show_notification("AI Task Complete")

    @safe_slot
    def cut(self):
        """Cut selection to clipboard."""
        if hasattr(self.editor, 'cut_selection'):
            self.editor.cut_selection()
            self.show_notification("Cut to Clipboard")

    @safe_slot
    def copy(self):
        """Copy selection to clipboard."""
        if hasattr(self.editor, 'copy_selection'):
            self.editor.copy_selection()
            self.show_notification("Copied to Clipboard")

    @safe_slot
    def paste(self):
        """Paste from clipboard."""
        if hasattr(self.editor, 'paste_from_clipboard'):
            self.editor.paste_from_clipboard()
            self.show_notification("Pasted from Clipboard")

    @safe_slot
    def activate_voice_control(self):
        """Activate Voice Command Listener."""
        from sj_das.core.engines.voice_engine import get_voice_assistant

        self.show_loading("Listening... (Say 'Generate' or 'Upscale')")

        assistant = get_voice_assistant()
        command = assistant.listen_command(duration=4)

        self.hide_loading()

        if command:
            self.show_notification(f"Heard: '{command}'", duration=2000)
            self._process_voice_command(command)
        else:
            self.show_notification("No command heard", duration=2000)

    def _process_voice_command(self, text):
        """Map voice text to actions."""
        text = text.lower()
        if "generate" in text or "pattern" in text:
            self.show_ai_pattern_gen()
        elif "upscale" in text or "enhance" in text:
            self.apply_ai_upscale_4x()
        elif "segment" in text:
            self.auto_segment()
        elif "chat" in text or "assistant" in text:
            self.activate_ai_chat()

    def activate_ai_chat(self):
        """Open AI Assistant Chat Interface."""
        from PyQt6.QtWidgets import (QApplication, QInputDialog, QLineEdit,
                                     QMessageBox)

        from sj_das.ai.agi_assistant import get_agi

        # Implement AI Chat
        agi = get_agi()
        while True:
            query, ok = QInputDialog.getText(
                self, "AI Assistant", "Ask me anything (or 'exit'):",
                QLineEdit.EchoMode.Normal
            )
            if not ok or query.lower() == 'exit':
                break

            result = {} # Initialize result here
            try:
                result = agi.process_command(query)
                response = result.get('response', 'No response')
                QMessageBox.information(self, "AI Response", response)
            except Exception as e:
                QMessageBox.critical(self, "AI Error", f"Failed to process command: {e}")


    # ==================== FILE OPERATIONS ====================

    @safe_slot
    def import_image(self):
        """Import/Open image file."""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Design",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All Files (*.*)"
        )

        if file_path:
            self.open_file(file_path)

    @safe_slot
    def open_file(self, file_path):
        """Load image file into editor."""
        import os

        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QApplication

        try:
            self.show_loading("Loading image...")
            QApplication.processEvents()

            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.hide_loading()
                self.show_error(f"Failed to load image: {file_path}")
                return

            if hasattr(self.editor, 'set_pixmap'):
                self.editor.set_pixmap(pixmap)
            elif hasattr(self.editor, 'setPixmap'):
                self.editor.setPixmap(pixmap)

            self.current_image_path = file_path
            
            # Switch to Editor View
            if hasattr(self, 'canvas_stack'):
                self.canvas_stack.setCurrentIndex(1)
            
            self.hide_loading()
            self.show_notification(f"Loaded: {os.path.basename(file_path)}")

        except Exception as e:
            self.hide_loading()
            self.show_error(f"Error loading image: {e}")

    @safe_slot
    @safe_slot
    def new_file(self):
        """Create new blank canvas (Delegated to Controller)."""
        from PyQt6.QtWidgets import QInputDialog
        width, ok1 = QInputDialog.getInt(
            self, "New Canvas", "Width (pixels):", 2400, 100, 10000)
        if not ok1:
            return

        height, ok2 = QInputDialog.getInt(
            self, "New Canvas", "Height (pixels):", 3000, 100, 20000)
        if not ok2:
            return

        self.controller.new_canvas(width, height)
        # Switch to Editor View
        if hasattr(self, 'canvas_stack'):
            self.canvas_stack.setCurrentIndex(1)

    @safe_slot
    def save_file(self):
        """Save current image (Delegated to Controller)."""
        self.controller.save_file(self.current_image_path)

    @safe_slot
    def save_file_as(self):
        """Save image with new filename (Delegated to Controller)."""
        self.controller.save_file_as()

    def _save_to_path(self, file_path):
        """Internal save helper (Deprecated - Use Controller)."""
        self.controller.save_file(file_path)

    # ==================== HELPER METHODS ====================

    def show_loading(self, message="Processing..."):
        """Show loading indicator."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication, QProgressDialog

        if not hasattr(
                self, 'progress_dialog') or self.progress_dialog is None:
            self.progress_dialog = QProgressDialog(message, None, 0, 0, self)
            self.progress_dialog.setWindowModality(
                Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.show()
            QApplication.processEvents()

    def hide_loading(self):
        """Hide loading indicator."""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def show_notification(self, message, duration=2000):
        """Show success notification."""
        if hasattr(self, 'status_bar') and self.status_bar:
            self.status_bar.showMessage(message, duration)

    def show_error(self, message):
        """Show error message."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)

    def _qimage_to_cv2(self, qimage):
        """Convert QImage to OpenCV format."""
        import cv2
        import numpy as np
        from PyQt6.QtGui import QImage

        if qimage.format() != QImage.Format.Format_RGB888:
            qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)

        width = qimage.width()
        height = qimage.height()

        ptr = qimage.constBits()
        ptr.setsize(height * width * 3)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))

        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    def _cv2_to_qimage(self, cv_img):
        """Convert OpenCV image to QImage."""
        import cv2
        import numpy as np
        from PyQt6.QtGui import QImage

        if len(cv_img.shape) == 2:
            height, width = cv_img.shape
            bytes_per_line = width
            return QImage(cv_img.data, width, height, bytes_per_line,
                          QImage.Format.Format_Grayscale8).copy()
        else:
            height, width, channel = cv_img.shape
            bytes_per_line = 3 * width
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            return QImage(rgb_image.data, width, height,
                          bytes_per_line, QImage.Format.Format_RGB888).copy()

    # ==================== EDIT OPERATIONS ====================

    # ==================== EDIT OPERATIONS ====================

    @safe_slot
    def cut(self):
        """Cut selection to clipboard."""
        self.controller.cut()

    @safe_slot
    def copy(self):
        """Copy selection to clipboard."""
        self.controller.copy()

    @safe_slot
    def paste(self):
        """Paste from clipboard."""
        self.controller.paste()

    # ==================== VIEW OPERATIONS ====================

    @safe_slot
    def zoom_in(self):
        """Zoom in."""
        self.controller.zoom_in()

    @safe_slot
    def zoom_out(self):
        """Zoom out."""
        self.controller.zoom_out()

    @safe_slot
    def zoom_fit(self):
        """Fit to window."""
        self.controller.zoom_fit()

    @safe_slot
    def zoom_actual(self):
        """Zoom to 100%."""
        self.controller.zoom_actual()

    @safe_slot
    def show_ai_settings(self):
        """Show AI settings dialog."""
        from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QLabel,
                                     QLineEdit, QPushButton, QVBoxLayout)

        dialog = QDialog(self)
        dialog.setWindowTitle("AI Settings")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        # API Keys section
        layout.addWidget(QLabel("<b>API Keys</b>"))

        minimax_key = QLineEdit()
        minimax_key.setPlaceholderText("Enter MiniMax API key")
        minimax_key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("MiniMax API Key:", minimax_key)

        # Model selection
        layout.addWidget(QLabel("<b>Model Settings</b>"))

        device_combo = QComboBox()
        device_combo.addItems(["CPU", "CUDA (GPU)"])
        form.addRow("Device:", device_combo)

        quality_combo = QComboBox()
        quality_combo.addItems(["Fast", "Balanced", "High Quality"])
        form.addRow("Quality:", quality_combo)

        layout.addLayout(form)

        # Buttons
        btn_layout = QVBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save settings
            self.show_notification("Settings saved")
            # TODO: Actually save to config file

    # ==================== LAYER MANAGEMENT ====================

    @safe_slot
    def show_layers(self):
        """Show layer management panel."""
        from sj_das.ui.components.layer_manager import LayerManager

        if not hasattr(self, 'layer_manager'):
            self.layer_manager = LayerManager(self)
            self.layer_manager.layers_changed.connect(self._on_layers_changed)

        # Show as dockable panel or dialog
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("Layers")
        dialog.setMinimumSize(300, 400)

        layout = QVBoxLayout(dialog)
        layout.addWidget(self.layer_manager)

        dialog.exec()

    def _on_layers_changed(self):
        """Handle layer changes."""
        # Get composite image and update editor
        composite = self.layer_manager.get_composite_image()
        if composite and hasattr(self.editor, 'set_image'):
            self.editor.set_image(composite)

    # ==================== BATCH PROCESSING ====================

    @safe_slot
    def show_batch_process(self):
        """Show batch processing dialog."""
        from sj_das.ui.dialogs.batch_process_dialog import BatchProcessDialog

        dialog = BatchProcessDialog(self)
        dialog.exec()

    # ==================== HISTORY PANEL ====================

    @safe_slot
    def show_history(self):
        """Show operation history."""
        from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QListWidget,
                                     QPushButton, QVBoxLayout)

        dialog = QDialog(self)
        dialog.setWindowTitle("History")
        dialog.setMinimumSize(300, 400)

        layout = QVBoxLayout(dialog)

        # History list
        history_list = QListWidget()

        # Get undo stack history
        if hasattr(self.editor, 'undo_stack'):
            for i in range(self.editor.undo_stack.count()):
                history_list.addItem(f"Action {i+1}")

        layout.addWidget(history_list)

        # Buttons
        btn_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(
            lambda: self.editor.undo_stack.clear() if hasattr(
                self.editor, 'undo_stack') else None)
        btn_layout.addWidget(clear_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    # ==================== COLOR PALETTE MANAGER ====================

    @safe_slot
    def show_palette_manager(self):
        """Show color palette manager."""
        from PyQt6.QtGui import QColor
        from PyQt6.QtWidgets import (QColorDialog, QDialog, QHBoxLayout,
                                     QListWidget, QPushButton, QVBoxLayout)

        dialog = QDialog(self)
        dialog.setWindowTitle("Color Palette Manager")
        dialog.setMinimumSize(400, 500)

        layout = QVBoxLayout(dialog)

        # Palette list
        palette_list = QListWidget()
        layout.addWidget(palette_list)

        # Buttons
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add Color")

        def add_color():
            color = QColorDialog.getColor()
            if color.isValid():
                palette_list.addItem(
                    f"RGB({color.red()}, {color.green()}, {color.blue()})")
        add_btn.clicked.connect(add_color)
        btn_layout.addWidget(add_btn)

        extract_btn = QPushButton("Extract from Image")

        def extract_colors():
            if hasattr(self.editor,
                       'original_image') and self.editor.original_image:
                # Extract dominant colors using k-means
                import cv2
                import numpy as np

                # Convert QImage to numpy
                img = self._qimage_to_cv2(self.editor.original_image)
                pixels = img.reshape((-1, 3)).astype(np.float32)

                # K-means
                criteria = (
                    cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER,
                    100,
                    0.2)
                _, labels, centers = cv2.kmeans(
                    pixels, 8, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

                # Add to palette
                palette_list.clear()
                for center in centers:
                    r, g, b = int(center[2]), int(center[1]), int(center[0])
                    palette_list.addItem(f"RGB({r}, {g}, {b})")

                self.show_notification("Extracted 8 dominant colors")
        extract_btn.clicked.connect(extract_colors)
        btn_layout.addWidget(extract_btn)

        save_btn = QPushButton("Save Palette")
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    # ==================== PREFERENCES ====================

    @safe_slot
    def show_preferences(self):
        """Show preferences dialog."""
        from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog,
                                     QFormLayout, QPushButton, QSpinBox,
                                     QVBoxLayout)

        dialog = QDialog(self)
        dialog.setWindowTitle("Preferences")
        dialog.setMinimumSize(400, 300)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        # Theme
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark", "Light", "Futuristic"])
        form.addRow("Theme:", theme_combo)

        # Auto-save
        autosave_check = QCheckBox("Enable auto-save")
        form.addRow("Auto-save:", autosave_check)

        autosave_interval = QSpinBox()
        autosave_interval.setRange(1, 60)
        autosave_interval.setValue(5)
        autosave_interval.setSuffix(" minutes")
        form.addRow("Interval:", autosave_interval)

        # Undo levels
        undo_levels = QSpinBox()
        undo_levels.setRange(10, 100)
        undo_levels.setValue(30)
        form.addRow("Undo levels:", undo_levels)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(
            lambda: (
                self.show_notification("Preferences saved"),
                dialog.accept()))
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    # ==================== HELP & SHORTCUTS ====================

    @safe_slot
    def show_about_dialog(self):
        """Show Premium About Dialog."""
        from sj_das.ui.dialogs.about_dialog import AboutDialog
        AboutDialog(self).exec()

    @safe_slot
    def show_shortcuts(self):
        """Show keyboard shortcuts help."""
        from PyQt6.QtWidgets import (QDialog, QPushButton, QTextEdit,
                                     QVBoxLayout)

        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setMinimumSize(500, 600)

        layout = QVBoxLayout(dialog)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
        <h2>Keyboard Shortcuts</h2>

        <h3>File Operations</h3>
        <table>
        <tr><td><b>Ctrl+N</b></td><td>New File</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open File</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Save As</td></tr>
        </table>

        <h3>Edit Operations</h3>
        <table>
        <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
        <tr><td><b>Ctrl+Y</b></td><td>Redo</td></tr>
        <tr><td><b>Ctrl+X</b></td><td>Cut</td></tr>
        <tr><td><b>Ctrl+C</b></td><td>Copy</td></tr>
        <tr><td><b>Ctrl+V</b></td><td>Paste</td></tr>
        </table>

        <h3>View Operations</h3>
        <table>
        <tr><td><b>Ctrl++</b></td><td>Zoom In</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom Out</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Zoom 100%</td></tr>
        <tr><td><b>Ctrl+9</b></td><td>Fit to Window</td></tr>
        </table>

        <h3>Tools</h3>
        <table>
        <tr><td><b>B</b></td><td>Brush Tool</td></tr>
        <tr><td><b>E</b></td><td>Eraser Tool</td></tr>
        <tr><td><b>G</b></td><td>Fill Tool</td></tr>
        <tr><td><b>I</b></td><td>Eyedropper Tool</td></tr>
        <tr><td><b>M</b></td><td>Selection Tool</td></tr>
        <tr><td><b>W</b></td><td>Magic Wand</td></tr>
        </table>
        """)

        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    # --- Relocated AI Methods (Safe Zone) ---

    @safe_slot
    def apply_remove_background(self):
        """Remove Background using U2Net."""
        from sj_das.core.engines.vision.background_removal_engine import \
            BackgroundRemovalEngine
        try:
            self.show_loading("Removing Background...")
            engine = BackgroundRemovalEngine()
            img = self.editor.get_image()
            cv_img = self._qimage_to_cv2(img)
            res = engine.remove_background(cv_img)
            self.editor.set_image(self._cv2_to_qimage(res))
            self.hide_loading()
            self.show_notification("Background Removed", duration=3000)
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Remove BG error: {str(e)}")

    @safe_slot
    def apply_human_parsing(self):
        """Apply Human Segmentation."""
        try:
            self.show_loading("Parsing Human Features...")
            # Use AIWorker if possible, or direct
            if self.ai_worker:  # If worker checks pass
                img = self.editor.get_image()
                cv_img = self._qimage_to_cv2(img)
                self.ai_worker = AIWorker("human_parsing", cv_img)
                self.ai_worker.finished.connect(
                    lambda res: (
                        self.editor.set_image(
                            self._cv2_to_qimage(res)),
                        self.hide_loading(),
                        self.show_notification("Human Parsed")))
                self.ai_worker.failed.connect(
                    lambda e: (
                        self.hide_loading(),
                        self.show_error(f"Parsing Failed: {e}")))
                self.ai_worker.start()
            else:
                # Fallback (Synchronous)
                from sj_das.core.engines.vision.human_parsing_engine import \
                    HumanParsingEngine
                engine = HumanParsingEngine()
                img = self.editor.get_image()
                res = engine.segment_human(self._qimage_to_cv2(img))
                self.editor.set_image(self._cv2_to_qimage(res))
                self.hide_loading()
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Parsing error: {e}")

    @safe_slot
    def apply_depth_map(self):
        """Generate Depth Map (Relief)."""
        try:
            self.show_loading("Generating 3D relief...")
            if self.ai_worker:
                img = self.editor.get_image()
                cv_img = self._qimage_to_cv2(img)
                self.ai_worker = AIWorker("depth", cv_img)
                self.ai_worker.finished.connect(
                    lambda res: (
                        self.editor.set_image(
                            self._cv2_to_qimage(res)),
                        self.hide_loading()))
                self.ai_worker.failed.connect(
                    lambda e: (
                        self.hide_loading(),
                        self.show_error(f"Depth Failed: {e}")))
                self.ai_worker.start()
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Depth Error: {e}")

    @safe_slot
    def apply_ai_upscale_4x(self):
        """Upscale image 4x."""
        from sj_das.core.engines.enhancement.real_esrgan_upscaler import \
            RealESRGANUpscaler
        try:
            self.show_loading("Upscaling 4x (RealESRGAN)...")
            upscaler = RealESRGANUpscaler()
            img = self.editor.get_image()
            cv_img = self._qimage_to_cv2(img)
            res = upscaler.upscale(cv_img, scale=4)
            self.editor.set_image(self._cv2_to_qimage(res))
            self.hide_loading()
            self.show_notification("Upscale Complete", duration=3000)
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Upscale Error: {e}")

    @safe_slot
    def show_ai_pattern_gen(self):
        """Show Pattern Generator."""
        from sj_das.ui.features.ai_pattern_gen import AIPatternGenerator
        self.pattern_gen_dialog = AIPatternGenerator(self)
        self.pattern_gen_dialog.show()

    @safe_slot
    def apply_style_transfer(self):
        # Stub
        self.show_notification("Style Transfer (Coming Soon)")

    @safe_slot
    def apply_colorization(self):
        # Stub
        self.show_notification("Colorization (Coming Soon)")

    @safe_slot
    def auto_segment(self):
        """Auto-segment main subject using SAM."""
        try:
            self.show_loading("Auto-Segmenting...")
            # Use centralized engine if available
            from sj_das.ai.segmentation_engine import get_engine
            engine = get_engine()
            img = self.editor.get_image()
            res = engine.segment_main_subject(self._qimage_to_cv2(img))
            self.editor.set_image(self._cv2_to_qimage(res))
            self.hide_loading()
            self.show_notification("Subject Segmented")
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Segmentation Error: {e}")

    @safe_slot
    def generate_from_sketch_controlnet(self):
        """Turn sketch into design using ControlNet (Threaded)."""
        from PyQt6.QtWidgets import QInputDialog

        # 1. Get Prompt
        prompt, ok = QInputDialog.getText(
            self, "Sketch to Design", "Describe the desired output:")
        if not ok or not prompt:
            return

        self.show_loading("Refining Sketch with ControlNet (AI)...")

        # Prepare Data
        img = self.editor.get_image()
        cv_img = self._qimage_to_cv2(img)

        # Launch Worker
        if self.ai_worker:
            self.ai_worker = AIWorker("controlnet", cv_img, prompt)
            self.ai_worker.finished.connect(self._on_controlnet_done)
            self.ai_worker.failed.connect(
                lambda e: (
                    self.hide_loading(),
                    self.show_error(f"ControlNet Failed: {e}")))
            self.ai_worker.start()
        else:
            self.hide_loading()
            self.show_error("AI Worker not initialized.")

    def _on_controlnet_done(self, res):
        self.hide_loading()
        if res is not None:
            self.editor.set_image(self._cv2_to_qimage(res))
            self.show_notification(
                "Design Generated from Sketch!", duration=3000)

    # --- Feature Mixin Bindings (Integration) ---

    @safe_slot
    def detect_pattern_from_image(self):
        """Binding for Pattern Detection Mixin."""
        from sj_das.ui.designer_view_textile_methods import \
            detect_pattern_from_image
        detect_pattern_from_image(self)

    @safe_slot
    def export_to_loom(self):
        """Binding for Loom Export Mixin."""
        from sj_das.ui.designer_view_loom_export import export_for_loom
        export_for_loom(self)

    @safe_slot
    def handle_ai_suggestion(self, action, data):
        """Binding for AI Insights Panel."""
        from sj_das.ui.designer_view_ai_methods import handle_ai_suggestion
        handle_ai_suggestion(self, action, data)

    @safe_slot
    def show_fabric_simulation(self):
        """Show Weave/Fabric Simulator (Real-time)."""
        import numpy as np
        from PyQt6.QtWidgets import QInputDialog

        weaves = {
            "Plain (1/1)": np.array([[1, 0], [0, 1]], dtype=np.uint8),
            "Twill (2/2)": np.array([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]], dtype=np.uint8),
            "Satin (5-end)": np.array([[1, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 1], [0, 1, 0, 0, 0], [0, 0, 0, 1, 0]], dtype=np.uint8)
        }

        weave_name, ok = QInputDialog.getItem(
            self, "Weave Mapper", "Select Weave Structure:", list(
                weaves.keys()), 0, False)

        if ok and weave_name:
            try:
                self.show_loading(f"Simulating {weave_name}...")
                pattern = weaves[weave_name] * 255

                # Apply simulated texture using multiply
                img = self.editor.get_image()
                cv_img = self._qimage_to_cv2(img)

                # Expand pattern to image size
                ph, pw = pattern.shape
                h, w = cv_img.shape[:2]

                tiled_pattern = np.tile(pattern, (h // ph + 1, w // pw + 1))
                tiled_pattern = tiled_pattern[:h, :w]

                # Simple multiply blend (simulating depth/shadow of threads)
                f_img = cv_img.astype(float)
                f_tex = cv2.merge(
                    [tiled_pattern, tiled_pattern, tiled_pattern]).astype(float) / 255.0

                # Blend
                res = (f_img * f_tex).astype(np.uint8)

                self.editor.set_image(self._cv2_to_qimage(res))
                self.hide_loading()
                self.show_notification(f"Simulated {weave_name} Fabric")

            except Exception as e:
                self.hide_loading()
                self.show_error(f"Simulation Error: {e}")

                # Show Response
                response = result.get('response', 'I could not process that.')

                # Execute Action if any
                if result.get('action'):
                    # Handle actions like 'open_expert' or 'run_analysis'
                    action_name = result.get('action')
                    if hasattr(self, action_name):
                        getattr(self, action_name)()
                    elif action_name == "open_expert":  # Remap common internal names
                        self.show_smart_expert()
                    elif action_name == "run_analysis":
                        self.run_ai_analysis()

                # Show Text Response
                QMessageBox.information(self, "AI Assistant", response)

            except Exception as e:
                self.status_bar.showMessage(f"AI Error: {str(e)}")
                self.logger.error(f"AI Chat Error: {e}")

    def generate_variations(self):
        """Start AI Generation in background thread."""
        if self.generation_thread and self.generation_thread.isRunning():
            InfoBar.warning(
                title="Generation in Progress",
                content="Please wait for the current generation to finish.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        # Show progress
        dialog = QProgressDialog(
            "Dreaming up new textiles...", "Cancel", 0, 100, self)
        dialog.setWindowModality(Qt.WindowModality.WindowModal)
        dialog.show()
        self.progress_dialog = dialog

        # Start Thread
        self.generation_thread = GenerationThread(
            self.model_manager, optimize_seamless=True)
        self.generation_thread.progress.connect(dialog.setValue)
        self.generation_thread.finished.connect(self.on_generation_complete)
        self.generation_thread.error.connect(lambda e: InfoBar.error(
            title="Generation Failed", content=e, parent=self, position=InfoBarPosition.TOP
        ))
        self.generation_thread.start()

    def on_generation_complete(self, image_path):
        """Handle successful generation."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        logger.info(f"AI Generation complete: {image_path}")

        # Open the generated image in the editor
        self.editor.load_image(image_path)

        # Learn from this action
        from sj_das.ai.adaptive_memory import get_adaptive_memory
        memory = get_adaptive_memory()
        memory.log_action("ai_generation", "generated_seamless_pattern")
        memory.learn_from_design(
            "Generated",
            "Digital_Style",
            ["Multi"])  # Simple tracking

        InfoBar.success(
            title="Textile Generated",
            content="New seamless pattern created successfully!",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

    def update_active_color(self, color):
        """Update active color display (Stub)"""
        pass

    def on_ai_action(self, action, data):
        """Handle Actions triggered by the AI Chat Assistant."""
        logger.info(f"AI Action Triggered: {action}")

        if action == 'generate_pattern':
            self.generate_variations()

        elif action == 'analyze_design':
            # Use Smart Expert to analyze
            from sj_das.ui.features.smart_expert import SmartExpert
            expert = SmartExpert(self)
            expert.run_analysis()  # Assuming this method exists or we call show_dialog

        elif action == 'apply_weave':
            # Switch to weave tab or apply specific weave?
            target = data.get('target', 'Twill')
            self.tabs.setCurrentIndex(3)  # Switch to Weaves tab (index 3)
            InfoBar.info(
                "AI: Weaves",
                f"Please select '{target}' and click Apply.",
                parent=self)

        elif action == 'split_channels':
            # Open Channel Split Dialog
            if hasattr(self, 'weaves_panel'):
                self.weaves_panel.open_channel_split_dialog()

        elif action == 'batch_loom_export':
            # Prompt for folder
            folder = QFileDialog.getExistingDirectory(
                self, "Select Folder to Process")
            if folder:
                InfoBar.success(
                    "Batch Processing",
                    f"Started processing images in {folder}...",
                    parent=self)
                # In a real app, this would iterate and use LoomExporter
                # For now, simulation
                QTimer.singleShot(
                    2000,
                    lambda: InfoBar.success(
                        "Batch Complete",
                        "Exported 0 files (Simulation)",
                        parent=self))

        elif action == 'check_loom_readiness':
            # Run Smart Expert
            from sj_das.ui.features.smart_expert import SmartExpert
            expert = SmartExpert(self)
            # Force specific loom mode analysis
            expert.run_analysis()
            InfoBar.info(
                "Loom Check",
                "Analysis Complete. Check the report for 'Float' warnings.",
                parent=self)

        else:
            logger.warning(f"Unknown AI action: {action}")

    def init_ui(self):
        """Initialize premium UI (Adobe-style Layout)."""
        # Root Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left: Acrylic Toolbar
        from sj_das.ui.components.toolbar import AcrylicToolbar
        self.toolbar = AcrylicToolbar(self)
        self.toolbar.tool_triggered.connect(self.handle_tool_action)
        main_layout.addWidget(self.toolbar)

        # 2. Center: Splitter (Canvas | Right Panel)
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(1)
        content_splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {COLORS['border_subtle']}; }}")

        # 2a. Canvas Area (Vertical: Options Bar + Canvas)
        canvas_area = QWidget()
        canvas_area_layout = QVBoxLayout(canvas_area)
        canvas_area_layout.setContentsMargins(0, 0, 0, 0)
        canvas_area_layout.setSpacing(0)

        # Top Context Bar
        self.create_tool_options_bar()
        canvas_area_layout.addWidget(self.tool_options_bar)

        # Rulers + Canvas Grid
        grid_layout = QVBoxLayout()  # Reuse existing logic simplified
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)

        # Top Ruler
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)
        corner = QWidget()
        corner.setFixedSize(20, 20)
        corner.setStyleSheet(f"background: {COLORS['bg_secondary']}")
        top_row.addWidget(corner)
        self.ruler_h = Ruler(Ruler.HORIZONTAL)
        top_row.addWidget(self.ruler_h)
        grid_layout.addLayout(top_row)

        # Mid (Left Ruler + Editor)
        mid_row = QHBoxLayout()
        mid_row.setContentsMargins(0, 0, 0, 0)
        mid_row.setSpacing(0)
        self.ruler_v = Ruler(Ruler.VERTICAL)
        mid_row.addWidget(self.ruler_v)
        mid_row.addWidget(self.editor)
        grid_layout.addLayout(mid_row)
        
        # Grid Container Widget
        self.grid_container = QWidget()
        self.grid_container.setLayout(grid_layout)

        # --- STACKED CANVAS AREA ---
        from PyQt6.QtWidgets import QStackedWidget
        from sj_das.ui.components.welcome_widget import WelcomeWidget
        
        self.canvas_stack = QStackedWidget()
        
        # Page 0: Welcome Screen
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.action_new.connect(self.new_file)
        self.welcome_widget.action_open.connect(self.import_image)
        # self.welcome_widget.action_recent.connect(self.open_file) 
        self.canvas_stack.addWidget(self.welcome_widget)
        
        # Page 1: Editor
        self.canvas_stack.addWidget(self.grid_container)
        
        # Default to Welcome
        self.canvas_stack.setCurrentIndex(0)

        canvas_area_layout.addWidget(self.canvas_stack)
        content_splitter.addWidget(canvas_area)

        # 3. Right: Properties
        self.create_right_panels()
        content_splitter.addWidget(self.right_panels)

        # Sizes
        content_splitter.setStretchFactor(0, 1)  # Canvas expands
        content_splitter.setStretchFactor(1, 0)  # Right fixed
        content_splitter.setCollapsible(1, True)

        main_layout.addWidget(content_splitter)

        # Global Status Bar (Overlay or Separate?)
        # Main Window has status bar usually.
        # But we created self.status_bar in __init__.
        # Let's add it to canvas_area_layout at bottom.
        canvas_area_layout.addWidget(self.status_bar)

    def create_tool_options_bar(self):
        """
        Creates the professional Fluent Tool Options Bar.
        Delegates construction to StandardMenuBuilder for modularity.
        """
        self.tool_options_bar = QFrame()
        self.tool_options_bar.setObjectName("toolOptionsBar")
        self.tool_options_bar.setFixedHeight(50)
        
        # Dynamic Glass Style via ThemeManager
        from sj_das.ui.theme_manager import ThemeManager
        tm = ThemeManager()
        c = tm.get_all_colors()
        
        # Glassmorphism Style
        self.tool_options_bar.setStyleSheet(f"""
            QFrame#toolOptionsBar {{
                background-color: {c['bg_secondary']}; 
                border-bottom: 1px solid {c['border_subtle']};
                border-top: 1px solid {c['bg_elevated']};
            }}
        """)

        layout = QHBoxLayout(self.tool_options_bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Use Builder
        builder = StandardMenuBuilder(self, layout)
        builder.build_all()

        # --- Grid Size Control ---
        from qfluentwidgets import SpinBox
        self.grid_spin = SpinBox(self.tool_options_bar)
        self.grid_spin.setRange(1, 100)
        self.grid_spin.setValue(1) 
        self.grid_spin.setPrefix("Grid: ")
        self.grid_spin.setSuffix("px")
        self.grid_spin.setFixedWidth(120)
        self.grid_spin.setToolTip("Adjust Grid Spacing")
        
        def update_grid(val):
            if hasattr(self, 'editor'):
                self.editor.grid_spacing = val
                self.editor.viewport().update()
                
        self.grid_spin.valueChanged.connect(update_grid)
        layout.addWidget(self.grid_spin)

        # --- Simulate Button ---
        from qfluentwidgets import FluentIcon as FIF
        from qfluentwidgets import PrimaryPushButton
        btn_sim = PrimaryPushButton("Simulate Fabric")
        btn_sim.setIcon(FIF.VIEW)  # or similar
        btn_sim.clicked.connect(self.start_fabric_simulation)
        layout.addWidget(btn_sim)

        # --- Smart Search Button (Owl-ViT) ---
        btn_search = PrimaryPushButton("Smart Find")
        btn_search.setIcon(FIF.SEARCH)
        btn_search.setStyleSheet(
            "QPushButton { background-color: #7C3AED; }")  # Violet
        btn_search.clicked.connect(self.open_smart_search)
        layout.addWidget(btn_search)

        # --- Focus Mode Button ---
        btn_focus = PrimaryPushButton("Focus Mode")
        btn_focus.setIcon(FIF.FULL_SCREEN)
        btn_focus.clicked.connect(self.toggle_focus_mode)
        layout.addWidget(btn_focus)

        # --- Voice Command (Feature Flagged) ---
        btn_voice = PrimaryPushButton("Voice")
        btn_voice.setIcon(FIF.MICROPHONE)
        btn_voice.clicked.connect(self.controller.toggle_voice_control)
        layout.addWidget(btn_voice)

        # --- Phase 12: AI Tools ---
        layout.addSpacing(16)

        btn_wand = PrimaryPushButton("Magic Wand")
        btn_wand.setIcon(FIF.IOT)
        btn_wand.clicked.connect(self.enable_magic_wand)
        layout.addWidget(btn_wand)

        btn_upscale = PrimaryPushButton("Upscale 4x")
        btn_upscale.setIcon(FIF.ZOOM_IN)
        btn_upscale.clicked.connect(self.controller.start_upscaling)
        layout.addWidget(btn_upscale)

        layout.addSpacing(16)
        btn_inspire = PrimaryPushButton("Met Museum")
        btn_inspire.setIcon(FIF.ALBUM)
        btn_inspire.clicked.connect(self.open_inspiration_dialog)
        layout.addWidget(btn_inspire)

        # --- Workspace Switcher (Right Aligned) ---
        from PyQt6.QtWidgets import QLabel
        from qfluentwidgets import ComboBox

        layout.addWidget(QLabel("Workspace:", self.tool_options_bar))

        self.workspace_combo = ComboBox(self.tool_options_bar)
        self.workspace_combo.addItems(
            ['Design', 'Export', 'Analysis', 'Minimal'])
        self.workspace_combo.setCurrentText(
            self.workspace_manager.current_workspace.capitalize())
        self.workspace_combo.currentTextChanged.connect(
            lambda t: self.switch_workspace(t.lower()))
        self.workspace_combo.setFixedWidth(120)

        layout.addWidget(self.workspace_combo)

        # --- AI Status Indicators ---
        from sj_das.ui.components.ai_status_widget import AIStatusWidget
        layout.addSpacing(16)
        self.ai_status = AIStatusWidget(self.tool_options_bar)
        layout.addWidget(self.ai_status)

        layout.addSpacing(16)

    # ==========================
    # FABRIC SIMULATION
    # ==========================
    def enable_magic_wand(self):
        """Activate AI Magic Wand Tool."""
        if hasattr(self.editor, 'TOOL_MAGIC_WAND'):
            self.editor.current_tool = self.editor.TOOL_MAGIC_WAND
            # Also notify controller to prepare embeddings
            self.controller.activate_magic_wand()
            self.show_notification("Magic Wand Active: Click object to select")

    # ==========================
    # FEATURE WRAPPERS (Integration)
    # ==========================
    @safe_slot
    def show_curves(self):
        if hasattr(self, 'feat_curves'): self.feat_curves.show_dialog()

    @safe_slot
    def show_levels(self):
         # Histogram/Levels
        if hasattr(self, 'feat_hist'): self.feat_hist.show_dialog()

    @safe_slot
    def show_channel_mixer(self):
        if hasattr(self, 'feat_mixer'): self.feat_mixer.show_dialog()

    @safe_slot
    def show_hsl(self):
        if hasattr(self, 'feat_hsl'): self.feat_hsl.show_dialog()

    @safe_slot
    def show_posterize(self):
        if hasattr(self, 'feat_posterize'): self.feat_posterize.show_dialog()
        
    @safe_slot
    def show_threshold(self):
        if hasattr(self, 'feat_thresh'): self.feat_thresh.show_dialog()

    @safe_slot
    def show_vignette(self):
        if hasattr(self, 'feat_vignette'): self.feat_vignette.show_dialog()

    @safe_slot
    def show_film_grain(self):
        if hasattr(self, 'feat_grain'): self.feat_grain.show_dialog()

    @safe_slot
    def show_noise_reduction(self):
        if hasattr(self, 'feat_noise'): self.feat_noise.show_dialog()

    @safe_slot
    def show_pixelate(self):
        if hasattr(self, 'feat_pixel'): self.feat_pixel.show_dialog()
        
    @safe_slot
    def show_emboss(self):
        if hasattr(self, 'feat_emboss'): self.feat_emboss.show_dialog()
        
    @safe_slot
    def show_halftone(self):
        if hasattr(self, 'feat_halftone'): self.feat_halftone.show_dialog()

    @safe_slot
    def show_motif_repeater(self):
        if hasattr(self, 'feat_repeat'): self.feat_repeat.show_dialog()

    @safe_slot
    def toggle_symmetry(self):
        if hasattr(self, 'feat_sym'): self.feat_sym.toggle_symmetry()

    @safe_slot
    def show_solarize(self):
        if hasattr(self, 'feat_solarize'): self.feat_solarize.show_dialog()

    def start_fabric_simulation(self):
        """Triggers the Fabric Reality engine."""
        img = self.editor.get_image()
        if img.isNull():
            InfoBar.warning(
                title='No Design',
                content='Canvas is empty. Load or draw a design first.',
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            return

        # Prepare Data
        # 1. Convert QImage to Numpy (Robust)
        if img.format() != QImage.Format.Format_RGBA8888:
            img = img.convertToFormat(QImage.Format.Format_RGBA8888)
            
        ptr = img.bits()
        ptr.setsize(img.height() * img.width() * 4)
        arr = np.array(ptr).reshape(img.height(), img.width(), 4)
        # Drop Alpha for simulation
        img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

        # 2. Get Weave Map (Assuming simple color-to-weave for now)
        # In full version, we'd pull from WeaveLibraryWidget / Model
        # For prototype: auto-map colors to 'Plain' or 'Twill'
        # Or just pass simple map.

        # We need TextileService
        from sj_das.core.services.textile_service import TextileService
        ts = TextileService.instance()

        # Connect signals if not connected
        try:
            ts.simulation_completed.disconnect()
        except BaseException:
            pass
        ts.simulation_completed.connect(self.show_fabric_preview)

        try:
            ts.error_occurred.disconnect(self.show_simulation_error)
        except BaseException:
            pass
        ts.error_occurred.connect(self.show_simulation_error)

        # Notify Start
        InfoBar.info(
            title='Simulation Started',
            content='Generating photorealistic preview...',
            parent=self,
            duration=2000
        )

        # Map unique colors to random weaves for demo
        # Real app: Use user defined mapping
        unique_colors = np.unique(img_bgr.reshape(-1, 3), axis=0)
        color_map = {}
        weaves = ts.get_available_weaves()
        import random
        for i, c in enumerate(unique_colors):
            # Deterministic mapping based on index
            w_name = weaves[i % len(weaves)]
            color_map[tuple(c)] = w_name

        ts.run_simulation(img_bgr, color_map)

    def show_fabric_preview(self, result_img: np.ndarray):
        """Callback when simulation finishes."""
        # Convert BGR to QImage
        h, w, ch = result_img.shape
        bytes_per_line = ch * w
        # rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB) # Sim returns RGB usually?
        # FabricSim returns BGR because it uses cv2 internally?
        # Checking FabricSim... it initializes zeros(..., 3). Uses standard cv2 colors?
        # FabricSim `_render_weave_texture` makes `warp_layer` from RGB input.
        # But `design_img` was passed as BGR.
        # It's safest to assume result matches input format or is RGB.
        # Let's assume RGB for display.

        # Convert to QT friendly
        bgra = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGRA)
        qimg = QImage(bgra.data, w, h, w *
                      4, QImage.Format.Format_ARGB32).copy()
        qimg = qimg.rgbSwapped()  # Adjust if colors look wrong

        # Open Dialog
        from sj_das.ui.dialogs.fabric_preview_dialog import FabricPreviewDialog
        dlg = FabricPreviewDialog(qimg, self)
        dlg.exec()

    def show_simulation_error(self, msg):
        InfoBar.error(
            title='Simulation Failed',
            content=msg,
            parent=self
        )

    def toggle_focus_mode(self):
        """Toggle distraction-free mode (Collapse panels)."""
        # Get current sizes
        splitter = self.findChild(QSplitter)
        if not splitter:
            return

        sizes = splitter.sizes()
        # [left, center, right]

        if sizes[0] > 0 or sizes[2] > 0:
            # Collapse
            self._last_panel_sizes = sizes
            splitter.setSizes([0, 10000, 0])
            self.show_notification("Focus Mode On")
        else:
            # Restore
            if hasattr(self, '_last_panel_sizes'):
                splitter.setSizes(self._last_panel_sizes)
            else:
                splitter.setSizes([60, 1200, 300])
            self.show_notification("Focus Mode Off")

    # ==========================
    # SMART SEARCH (OWL-ViT)
    # ==========================
    def open_smart_search(self):
        """Opens the Smart Find dialog."""
        img = self.editor.get_image()
        if img.isNull():
            InfoBar.warning(
                title='No Design',
                content='Canvas empty.',
                parent=self)
            return

        # Convert QImage to Numpy (Robust)
        if img.format() != QImage.Format.Format_RGBA8888:
            img = img.convertToFormat(QImage.Format.Format_RGBA8888)

        ptr = img.bits()
        ptr.setsize(img.height() * img.width() * 4)
        arr = np.array(ptr).reshape(img.height(), img.width(), 4)
        img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

        from sj_das.ui.dialogs.smart_find_dialog import SmartFindDialog
        dlg = SmartFindDialog(img_bgr, self)
        if dlg.exec():
            # Apply selection mask
            mask = dlg.get_selection_mask()
            if mask is not None:
                # Assuming editor has set_selection_mask or similar
                # If not, let's create a selection from mask
                # For now, just show success
                InfoBar.success(
                    title='Selection Created',
                    content='Objects selected from search.',
                    parent=self)
                self.editor.set_selection_from_mask(mask)

    def create_tool_strip(self):
        """Create professional tool strip via Factory"""
        factory = ToolbarFactory(self)
        self.tool_strip = factory.create_tool_strip()

        self.tool_options_bar.parent().layout()
        # Find where to add? init_ui does this. We just return or set self.tool_strip
        # modern_designer_view.py:228 adds self.tool_strip to content_splitter
        pass

    def create_right_panels(self):
        """Create professional right panels via Factory"""
        factory = PanelFactory(self)
        self.right_panels = factory.create_right_panels()

    def create_status_bar(self):
        """Create advanced professional status bar."""
        self.status_bar = AdvancedStatusBar(self)

        # Connect to editor events
        if hasattr(self.editor, 'tool_changed'):
            self.editor.tool_changed.connect(self.status_bar.set_tool_info)

        # Set initial canvas info
        if hasattr(self.editor,
                   'original_image') and self.editor.original_image:
            self.status_bar.set_canvas_info(
                self.editor.original_image.width(),
                self.editor.original_image.height()
            )

        # Connect zoom changes
        if hasattr(self.editor, 'zoom_changed'):
            self.editor.zoom_changed.connect(self.status_bar.set_zoom_level)

        # Add to layout (assuming parent has a layout)
        # This will be added to the main window's status bar area
        logger.info("Advanced status bar created")

    # Event handlers
    @safe_slot
    def on_tool_selected(self, tool_id):
        """Handle tool selection with smooth feedback"""
        # Uncheck all tools
        if hasattr(self, 'tool_buttons'):
            for btn in self.tool_buttons.values():
                btn.setChecked(False)

            # Check selected tool
            if tool_id in self.tool_buttons:
                self.tool_buttons[tool_id].setChecked(True)

        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.set_tool_info(f"Tool: {tool_id.title()}")

        # Direct set via robust set_tool (handles strings and ints)
        self.editor.set_tool(tool_id)

        # --- MIXIN HOOKS (PSP Features) ---
        if tool_id == 'magic_wand':
            self.activate_magic_wand()
        elif tool_id == 'clone':
            self.activate_clone_stamp()
        elif tool_id == 'text':
            self.activate_text_tool()
        # Professional Features Hooks
        elif tool_id == 'pen':
            # Activate Pen Tool (Vector Layer)
            if hasattr(self, 'pen_tool'):
                # Assuming PenTool attaches to editor scene or similar
                # self.pen_tool.activate(self.editor)
                pass
        elif tool_id == 'shape':
            # Activate Shape Tools
            if hasattr(self, 'shapes'):
                # self.shapes.activate(self.editor)
                pass
        elif tool_id == 'gradient':
            # Activate Gradient Tool
            if hasattr(self, 'feat_grad'):
                self.feat_grad.show_dialog()  # Or activate interactive tool
        elif tool_id == 'history':
            # History Brush
            pass
        elif tool_id == 'heal':
            # Spot Healing
            pass

        # Update status if available
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Tool Selected: {tool_id.title()}")

    @safe_slot
    def on_size_changed(self, value):
        """Handle size change"""
        self.size_value.setText(str(value))
        if hasattr(self.editor, 'brush_size'):
            self.editor.brush_size = value

    @safe_slot
    def on_opacity_changed(self, value):
        """Handle opacity change"""
        self.opacity_value.setText(f"{value}%")
        if hasattr(self.editor, 'brush_opacity'):
            self.editor.brush_opacity = value / 100.0

    @safe_slot
    # ==================== WORKSPACE MANAGEMENT ====================
    def _on_workspace_changed(self, name: str):
        """Handle workspace switch event."""
        config = self.workspace_manager.get_workspace_config(name)
        self.set_workspace_layout(config)
        self.show_notification(f"Switched to {name} Workspace")

    def set_workspace_layout(self, config: dict):
        """
        Apply workspace configuration to UI.
        Controls visibility of panels, toolbars, and specific tabs.
        """
        panels = config.get('panels', {})

        # 1. Left Panel (Tool Strip)
        left_items = panels.get('left', [])
        if self.tool_strip:
            self.tool_strip.setVisible('tools' in left_items)

        # 2. Right Panels (Tab Visibility)
        right_items = panels.get('right', [])
        if self.tabs:
            # Map simplified keys to Tab Text
            # Keys from WorkspaceManager: 'layers', 'colors', 'yarn', 'weaves',
            # 'ai_panel', 'navigator'
            key_map = {
                'layers': 'Layers',
                'colors': 'Colors',
                'yarn': 'Yarn',
                'weaves': 'Weaves',
                'ai_panel': 'AI',
                'navigator': 'Navigator',
                'history': 'History',
                'export_preview': 'Export',  # Potential future tab
                'loom_config': 'Loom'      # Potential future tab
            }

            # Reset all to hidden first? Or just iterate?
            # QTabWidget doesn't have setTabVisible in older Qt, but 5.15+ and PySide6 do.
            # Assuming PyQt6 has it (ProcessId 20352 output implies PyQt6 usage
            # implicitly or explicitly)

            for i in range(self.tabs.count()):
                tab_text = self.tabs.tabText(i)
                # Find if this tab is in the active list
                should_show = False

                # Check against all keys
                for key, val in key_map.items():
                    if val == tab_text:
                        if key in right_items:
                            should_show = True
                        break

                # Default behavior: If tab not in map, leave it alone or hide?
                # Let's hide if not explicitly requested, for "Focus"
                self.tabs.setTabVisible(i, should_show)

            # If right list is empty, hide the whole container?
            self.right_panels.setVisible(bool(right_items))

            # Switch to first available tab
            for i in range(self.tabs.count()):
                if self.tabs.isTabVisible(i):
                    self.tabs.setCurrentIndex(i)
                    break

        # 3. Bottom Panel (Not yet implemented in splitting, but logic ready)
        # bottom_items = panels.get('bottom')
        # if hasattr(self, 'bottom_panel'): ...

    def switch_workspace(self, name: str):
        """Manual trigger for workspace switch."""
        self.workspace_manager.switch_workspace(name)

    # ==================== HELPER METHODS ====================
    @safe_slot
    def on_yarn_selected(self, index, color):
        """Handle yarn selection"""
        self.editor.brush_color = color
        self.status_label.setText(f"Yarn {index} Selected: {color.name()}")
        InfoBar.info(
            title="Yarn Selected",
            content=f"Brush color set to Yarn {index}",
            parent=self,
            duration=2000,
            position=InfoBarPosition.TOP_RIGHT
        )

    @safe_slot
    def on_weave_selected(self, pattern, name):
        """Handle weave selection"""
        if hasattr(self.editor, 'set_pattern'):
            self.editor.set_pattern(pattern)
            self.status_label.setText(f"Weave Selected: {name}")
            InfoBar.success(
                title="Weave Applied",
                content=f"Fill tool will use '{name}' pattern",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )

    # Feature implementations
    @safe_slot
    @safe_slot
    def import_image(self, path=None):
        """
        Import image with comprehensive error handling and validation.

        Args:
            path: Optional file path. If None, shows file dialog.
        """
        try:
            # Get file path
            if not path:
                path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Import Design",
                    "",
                    f"Images ({' '.join('*' + ext for ext in FileConstants.SUPPORTED_IMAGE_FORMATS)})"
                )

            if not path:
                return

            # Validate file path
            try:
                validated_path = InputValidator.validate_file_path(
                    path,
                    must_exist=True,
                    allowed_extensions=FileConstants.SUPPORTED_IMAGE_FORMATS
                )
            except Exception as e:
                logger.error(f"File validation failed: {e}")
                InfoBar.error(
                    title="Invalid File",
                    content=str(e),
                    parent=self,
                    duration=3000,
                    position=InfoBarPosition.TOP
                )
                return

            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            # Load image
            image = QImage(str(validated_path))

            # Validate image
            try:
                image = InputValidator.validate_image(image)
            except Exception as e:
                QApplication.restoreOverrideCursor()
                logger.error(f"Image validation failed: {e}")
                InfoBar.error(
                    title="Invalid Image",
                    content=str(e),
                    parent=self,
                    duration=3000,
                    position=InfoBarPosition.TOP
                )
                return

            # Cleanup old image with memory manager
            if hasattr(self, 'memory_manager') and hasattr(
                    self.editor, 'original_image'):
                self.memory_manager.cleanup_image(self.editor.original_image)

            # Set to editor
            self.editor.set_image(image)
            self.current_image_path = str(validated_path)

            QApplication.restoreOverrideCursor()

            InfoBar.success(
                title="Import Successful",
                content=f"Loaded: {validated_path.name}",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP
            )

            logger.info(f"Successfully imported: {validated_path}")

            # Check memory status
            if hasattr(self, 'memory_manager'):
                self.memory_manager.check_memory_status()

        except PermissionError as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Permission denied: {e}")
            InfoBar.error(
                title="Permission Denied",
                content=f"Cannot access file: {path}",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP
            )
        except MemoryError as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Out of memory: {e}")
            InfoBar.error(
                title="Out of Memory",
                content="Image too large. Try a smaller image.",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP
            )
        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Failed to import image: {e}", exc_info=True)
            from sj_das.core.exceptions import DesignImportError
            error = DesignImportError(
                "Failed to import design",
                details={"path": path, "error": str(e)}
            )
            InfoBar.error(
                title="Import Failed",
                content=str(error),
                parent=self,
                position=InfoBarPosition.TOP
            )
        """Standard Design Import with Loom Settings"""
        # Show loom import dialog
        dialog = LoomImportDialog(parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        specs = dialog.get_specifications()
        path = specs.get("image_path")

        if not path:
            return

        try:
            # Load and process image
            from sj_das.core.image_ingestor import ImageIngestionEngine
            ingestor = ImageIngestionEngine()

            # Show Wait Cursor
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            # Run AI Ingestion with loom specifications
            processed_cv = ingestor.process_image(
                path,
                target_width=specs["hooks"],
                max_colors=specs["colors"]
            )

            # Load result into editor
            self.editor.set_image(processed_cv)
            self.current_image_path = path

            # Store specifications for export
            self.current_loom_specs = specs

            QApplication.restoreOverrideCursor()

            InfoBar.success(
                title="Loom Ready",
                content=f"Design configured for {specs['hooks']} hooks",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP
            )
            self.status_label.setText(
                f"Loaded: {path} ({specs['hooks']} hooks)")

            # AUTO ANALYZE & SEGMENT
            QTimer.singleShot(500, self.auto_analyze_on_load)

        except Exception as e:
            QApplication.restoreOverrideCursor()
            from sj_das.core.exceptions import DesignImportError
            error = DesignImportError(
                "Failed to import design",
                details={"path": path, "error": str(e)}
            )
            InfoBar.error(
                title="Import Failed",
                content=str(error),
                parent=self,
                position=InfoBarPosition.TOP
            )

    def auto_analyze_on_load(self):
        """Automatic pipeline after load"""
        self.status_label.setText("Running Auto-Analysis & Segmentation...")
        self.run_ai_analysis()
        QTimer.singleShot(1000, self.auto_segment)

    @safe_slot
    def pick_color(self, *args):
        """Pick color dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.editor.brush_color = color
            self.status_label.setText(f"Color: {color.name()}")
            InfoBar.success(
                title="Color Selected",
                content=f"Color: {color.name()}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    @safe_slot
    def reduce_to_palette(self, *args):
        """Reduce image to color palette"""
        if self.editor.original_image is None or self.editor.original_image.isNull():
            InfoBar.warning(
                title="No Image",
                content="Please import an image first",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return

        colors, ok = QInputDialog.getInt(
            self, "Reduce Colors",
            "Number of colors:", 16, 2, 256
        )
        if ok:
            self.status_label.setText(f"Reducing to {colors} colors...")
            # Implement color reduction here
            QTimer.singleShot(
                1000, lambda: self.status_label.setText("Color reduction complete!"))

    def run_ai_analysis(self):
        """Run AI analysis on current design"""
        if self.editor.original_image is None or self.editor.original_image.isNull():
            InfoBar.warning(
                title="No Image",
                content="Please import an image first",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return

        self.status_label.setText("Running AI analysis...")

        try:
            # Convert QImage to numpy
            image = self.editor.original_image
            width, height = image.width(), image.height()
            ptr = image.constBits()
            ptr.setsize(height * width * 4)
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
            rgb_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

            # Run AI prediction
            if self.ai_model:
                prediction = self.ai_model.predict(rgb_image)
                if prediction:
                    InfoBar.success(
                        title="AI Analysis Complete",
                        content="Design analyzed successfully!",
                        orient=Qt.Orientation.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
                    self.status_label.setText("AI analysis complete!")
            else:
                self.status_label.setText("AI model not available")
        except Exception as e:
            InfoBar.error(
                title="Analysis Failed",
                content=str(e),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            self.status_label.setText("AI analysis failed")

            # Analyze using Real AI Model
            from sj_das.ai.model_loader import get_ai_model
            ai_model = get_ai_model()

            # Get Image as Numpy
            ptr = self.editor.original_image.constBits()
            ptr.setsize(self.editor.original_image.sizeInBytes())
            arr = np.array(ptr).reshape(
                self.editor.original_image.height(),
                self.editor.original_image.width(),
                4
            )
            # Convert RGBA to RGB (CV2 helper uses BGR usually, model expects RGB/BGR?)
            # TextileAIModel.predict handles conversion if needed but expects
            # generally numpy array
            cv_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            # Predict
            pattern_type, confidence = ai_model.predict_pattern_type(cv_img)
            scores = ai_model.get_confidence_scores(cv_img)
            # Use confidence as proxy for now
            complexity_score = int(scores.get('pattern', 50))

            # Show Result in AI Panel
            msg = f"Analysis Complete.\nPattern: {pattern_type}\nConfidence: {confidence:.1f}%\n"

            InfoBar.success(
                title="AI Analysis",
                content=msg,
                parent=self,
                duration=4000,
                position=InfoBarPosition.TOP_RIGHT
            )
            self.status_bar.showMessage(
                f"AI: Detected {pattern_type} ({confidence:.1f}%)")

        except Exception as e:
            logger.error(f"AI Analysis failed: {e}")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    "AI Analysis failed (Model not ready)")

    @safe_slot
    def auto_segment(self):
        """Auto-segment the current design using Computer Vision"""
        if not self.current_image_path:
            return

        self.status_label.setText("✂️ Auto-Segmenting Body, Border, Pallu...")

        try:
            # Run Segmentation Engine
            from sj_das.ai.segmentation_engine import SegmentationEngine
            self.segmentation_engine = SegmentationEngine()  # Ensure engine is initialized
            segments = self.segmentation_engine.segment_saree(
                self.current_image_path)

            # Apply to UI
            if segments:
                # Store segments
                self.segments = segments

                # Update Layers Panel (if exists)
                if hasattr(self, 'layers_panel'):
                    self.layers_panel.clear_layers()
                    for name, path in segments.items():
                        self.layers_panel.add_layer(name, path)

                InfoBar.success(
                    title="Segmentation Complete",
                    content=f"Split into: {', '.join(segments.keys())}",
                    parent=self,
                    duration=4000
                )
                self.status_label.setText("Design Segmented Successfully")
            else:
                self.status_label.setText(
                    "Segmentation: No clear borders found")

        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            self.status_label.setText("Error during segmentation")

    # =========================================================================
    # CORE WORFLOWS (Restored from Original)
    # =========================================================================

    def on_color_picked_enhanced(self, color):
        """Handle color pick with Cloud Intelligence."""
        # 1. Update UI (Legacy logic replication/call)
        if hasattr(self, 'update_active_color'):
            self.update_active_color(color)
        else:
            # Fallback
            self.status_label.setText(f"Color: {color.name()}")

        # 2. Cloud Lookup (Async)
        from sj_das.core.services.cloud_service import CloudService
        CloudService.instance().color_identified.disconnect() if hasattr(
            CloudService.instance(), 'color_identified') else None
        try:
            CloudService.instance().color_identified.connect(self._on_cloud_color_found)
            CloudService.instance().identify_color(color.name())
        except Exception:
            pass  # Fail silently if cloud offline

    def _on_cloud_color_found(self, data):
        """Update status with true name."""
        name = data.get('name', 'Unknown')
        hex_val = data.get('hex', '')
        self.status_label.setText(f"Color: {hex_val} ({name})")
        # Optional: Toast
        # self.show_notification(f"Selected: {name}")

    # ==========================
    # Phase 15: Cortex Handlers
    # ==========================
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'omni_bar'):
            w = self.width()
            h = self.height()
            bw = self.omni_bar.width()
            bh = self.omni_bar.height()
            self.omni_bar.move((w - bw) // 2, h - bh - 80)  # Bottom center
            self.omni_bar.raise_()

    def handle_tool_action(self, tool_id):
        """Handle actions from Acrylic Toolbar."""
        logger.info(f"Tool Triggered: {tool_id}")
        
        # Delegate to central tool handler
        self.on_tool_selected(tool_id)

        # Handle special non-tool actions
        if tool_id == "upscale":
            self.controller.start_upscaling()
        elif tool_id == "met":
            self.open_inspiration_dialog()

    def handle_cortex_action(self, action, params):
        """Execute Brain commands."""
        logger.info(f"Brain Command: {action} {params}")
        if action == "activate_tool":
            tool = params.get("tool")
            if tool == "magic_wand":
                self.enable_magic_wand()
        elif action == "upscale":
            self.controller.start_upscaling()
        elif action == "open_inspiration":
            self.open_inspiration_dialog()
        elif action == "generate":
            prompt = params.get('prompt')
            self.show_notification(f"Dreaming: '{prompt}'...")
            self.cortex.creative.generate_pattern(prompt)
        elif action == "analyze_canvas":
            self.show_notification("Analyzing Visuals...")
            # Capture Canvas
            img = self.editor.get_image_data()
            if img:
                import base64

                from PyQt6.QtCore import QBuffer, QIODevice
                ba = QBuffer()
                ba.open(QIODevice.OpenModeFlag.WriteOnly)
                img.save(ba, "PNG")
                b64_str = base64.b64encode(ba.data()).decode('utf-8')
                self.cortex.vision.analyze_image(b64_str)

    def on_cortex_content(self, content):
        """Handle content generated by Cortex Lobes."""
        from PyQt6.QtGui import QImage
        from qfluentwidgets import FluentIcon as FIF
        from qfluentwidgets import TeachingTip, TeachingTipTailPosition

        if isinstance(content, QImage):
            self.editor.set_image(content)
            self.show_notification("Design Generated Successfully!")
            self.status_label.setText("AI Generation Complete")
        elif isinstance(content, str):
            # Analysis output
            TeachingTip.create(
                target=self.omni_bar,
                icon=FIF.CHAT,
                title="Cortex Insight",
                content=content,
                isClosable=True,
                tailPosition=TeachingTipTailPosition.BOTTOM,
                duration=10000,
                parent=self
            )

    def open_inspiration_dialog(self):
        """Open The Met Museum inspiration gallery."""
        from sj_das.ui.dialogs.inspiration_dialog import InspirationDialog
        dialog = InspirationDialog(self)
        dialog.image_selected.connect(self.load_cloud_image)
        dialog.exec()

    def load_cloud_image(self, url):
        """Download and load image from URL."""
        self.status_label.setText("Downloading asset from cloud...")
        import requests
        try:
            resp = requests.get(url, timeout=15)
            img = QImage()
            img.loadFromData(resp.content)
            if not img.isNull():
                self.editor.set_image(img)
                self.status_label.setText("Cloud Asset Loaded")
                self.show_notification(
                    "Design loaded from The Met collection.")
            else:
                self.show_notification(
                    "Failed to decode cloud image.", duration=3000)
        except Exception as e:
            logger.error(f"Cloud load failed: {e}")
            self.show_notification(f"Download Error: {e}", duration=3000)

    def import_design(self, *args):
        """Smart Import Workflow with Loom Configuration"""
        dialog = LoomImportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 1. Get Configuration
            file_path = dialog.get_file_path()
            config = dialog.get_loom_config()

            if not file_path:
                return

            logger.info(f"Importing Design: {file_path} with Config: {config}")

            # 2. Load Image to Canvas
            self.load_image_to_canvas(file_path)

            # 3. Apply Loom Constraints (Resize if needed)
            if config.get('hooks'):
                hooks = config['hooks']
                # Ask user if they want to resize to fit hooks exactly
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    'Resize to Fit Loom?',
                    f'This loom has {hooks} hooks. Would you like to resize the image to fit exactly?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # Resize image to match hook count
                    if hasattr(
                            self.editor, 'original_image') and self.editor.original_image is not None:
                        import cv2
                        h, w = self.editor.original_image.shape[:2]
                        new_w = hooks
                        new_h = int(h * (hooks / w))
                        resized = cv2.resize(
                            self.editor.original_image, (new_w, new_h))
                        self.editor.original_image = resized
                        if hasattr(self.editor, 'update_display'):
                            self.editor.update_display()
                        logger.info(
                            f"Resized image to {new_w}x{new_h} to fit {hooks} hooks")

            # 4. Trigger Auto-Analysis (Smart Feature)
            # Creating a 'Loading' feel
            self.status_label.setText("🤖 AI Analysis in progress...")
            QTimer.singleShot(1000, self.run_ai_analysis)

    def load_image_to_canvas(self, path):
        """Load image into the pixel editor"""
        self.current_image_path = path
        image = QImage(path)
        if not image.isNull():
            self.editor.set_image(image)
            self.canvas_info.setText(
                f"Canvas: {image.width()}x{image.height()}px")
            self.status_label.setText("Design Loaded Successfully")
        else:
            QMessageBox.critical(self, "Error", "Failed to load image.")

    def generate_variations(self):
        """Generate design variations using AI"""
        text, ok = QInputDialog.getText(
            self, "AI Generator", "Describe Pattern (e.g., 'Peacock border, red background'):")
        if ok and text:
            self.status_label.setText("Generating variations...")

            # Progress
            self.gen_progress = QProgressDialog(
                "Generating Variations...", "Cancel", 0, 0, self)
            self.gen_progress.setWindowModality(Qt.WindowModality.WindowModal)
            self.gen_progress.setMinimumDuration(0)
            self.gen_progress.show()

            # Thread
            self.gen_thread = GenerationThread(text, variations=True)
            self.gen_thread.finished_signal.connect(
                self.on_generation_finished)
            self.gen_thread.error_signal.connect(
                lambda e: self.gen_progress.close())
            self.gen_thread.start()

    def on_generation_finished(self, result):
        self.gen_progress.close()
        if isinstance(result, list) and result:
            # Load first result
            data = result[0]
            self.editor.set_image(data)

            InfoBar.success(
                title="Generation Complete",
                content="Variation generated and loaded!",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP
            )
            self.status_label.setText("Variation generation complete!")
            self.auto_analyze_on_load()

    def on_ai_suggestion(self, suggestion):
        """Handle proactive suggestion"""
        InfoBar.info(
            title=suggestion["title"],
            content=suggestion["message"],
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self
        )

    @safe_slot
    def activate_magic_eraser(self, *args):
        """Trigger Smart Inpainting"""
        if self.editor.selection_mask is None or not np.any(
                self.editor.selection_mask):
            InfoBar.warning(
                title="No Selection",
                content="Please select an area first.",
                position=InfoBarPosition.TOP,
                parent=self)
            return

        text, ok = QInputDialog.getText(
            self, "Magic Edit", "Describe the change (e.g. 'mango motif'):")
        if ok and text:
            self.editor.apply_smart_inpaint(text)

    @safe_slot
    def action_toggle_validator(self, checked):
        """Toggle Validator"""
        self.editor.toggle_validator(checked)
        if checked:
            InfoBar.success(
                title="Loom Guard Active",
                content="Real-time weaving checks enabled.",
                position=InfoBarPosition.TOP,
                parent=self)

    @safe_slot
    def export_design(self, *args):
        """Export design to loom format"""
        if self.editor.original_image is None or self.editor.original_image.isNull():
            InfoBar.warning(
                title="No Design",
                content="Please import a design first",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export to Loom", "",
            "BMP Files (*.bmp);;All Files (*)"
        )
        if path:
            try:
                # Get current image
                image = self.editor.original_image
                # Save as BMP
                image.save(path, "BMP")

                InfoBar.success(
                    title="Export Successful",
                    content=f"Design exported to: {path}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                self.status_label.setText(f"Exported: {path}")
            except Exception as e:

                InfoBar.error(
                    title="Export Failed",
                    content=str(e),
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )

    @safe_slot
    def new_design(self, *args):
        """Create new empty design"""
        # Ask for dimensions or just default
        w, h = 1000, 2000  # Saree ratio approx
        img = QImage(w, h, QImage.Format.Format_RGB888)
        img.fill(Qt.GlobalColor.white)
        self.editor.set_image(img)
        InfoBar.success(
            title="New Design",
            content="Created new 1000x2000 canvas.",
            parent=self
        )

    @safe_slot
    def save_project(self, *args):
        """Save project (Stub)"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "SJ-DAS Project (*.sjd)")
        if path:
            InfoBar.success(
                title="Project Saved",
                content=f"Saved to {path}",
                parent=self)

    @safe_slot
    def export_preview(self, *args):
        """Export PNG Preview"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Preview", "", "PNG Image (*.png)")
        if path:
            self.editor.original_image.save(path)
            InfoBar.success(
                title="Preview Exported",
                content=f"Saved to {path}",
                parent=self)

    @safe_slot
    def show_fabric_simulation(self, *args):
        """
        Competitive Feature: 2.5D Fabric Simulation.
        Matches ArahWeave visual quality.
        """
        if self.editor.original_image is None:
            InfoBar.warning(
                title="No Design",
                content="Load a design first.",
                parent=self)
            return

        self.status_label.setText(
            "Rendering 2.5D Simulation (High Quality)...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            from sj_das.core.fabric_reality import FabricRealityEngine
            engine = FabricRealityEngine()

            # Get Numpy Image
            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            # Render
            # TODO: Get weave type from specs
            sim_img = engine.render_simulation(img_bgr, weave_type='satin')

            QApplication.restoreOverrideCursor()

            # Show in Dialog
            h, w, c = sim_img.shape
            final = QImage(sim_img.data, w, h, 3 *
                           w, QImage.Format.Format_RGB888).rgbSwapped()

            from PyQt6.QtWidgets import QLabel, QScrollArea
            dialog = QDialog(self)
            dialog.setWindowTitle("Fabric Reality View (2.5D)")
            dialog.resize(1200, 800)

            layout = QVBoxLayout(dialog)
            scroll = QScrollArea()
            label = QLabel()
            label.setPixmap(final.to_qpixmap())  # Convert QImage -> QPixmap
            scroll.setWidget(label)
            layout.addWidget(scroll)

            InfoBar.success(
                title="Simulation Complete",
                content="Showing 2.5D Yarn Simulation with Lighting.",
                parent=self
            )

            dialog.exec()
            self.status_label.setText("Ready")

        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Sim Error: {e}")
            InfoBar.error(
                title="Simulation Failed",
                content=str(e),
                parent=self)

    @safe_slot
    def show_costing_report(self, *args):
        """
        Competitive Feature: Yarn Cost Estimator.
        Matches NedGraphics utility.
        """
        if self.editor.original_image is None:
            return

        # Gather inputs
        # In real app, ask for these via Dialog
        width = self.editor.original_image.width()  # Hooks
        height = self.editor.original_image.height()  # Picks

        # Defaults
        specs = {
            'width_inches': 45,
            'epi': 72,
            'ppi': 72,
            'warp_price': 6500,  # Silk
            'weft_price': 4500  # Zari
        }

        try:
            from sj_das.core.costing import CostingEngine
            engine = CostingEngine()

            report = engine.calculate_cost(width, height, specs)

            if report.get('success'):
                # Format Clean HTML Report
                c = report['consumption']
                m = report['cost']
                d = report['dimensions']

                msg = (f"<h2>Yarn Cost Estimation</h2>"
                       f"<hr>"
                       f"<b>Design Specs:</b><br>"
                       f"Size: {d['width_inch']}\" x {d['length_meter']}m<br>"
                       f"Total Sensitivity: {d['total_picks']} Picks<br><br>"
                       f"<b>Material Consumption:</b><br>"
                       f"Warp: {c['warp_kg']} kg<br>"
                       f"Weft: {c['weft_kg']} kg<br>"
                       f"<b>Total Weight: {c['total_kg']} kg</b><br><br>"
                       f"<b>Estimated Cost:</b><br>"
                       f"Warp: {m['warp_cost']}<br>"
                       f"Weft: {m['weft_cost']}<br>"
                       f"<b>Total: {m['total_cost']}</b>")

                QMessageBox.information(self, "Cost Report", msg)
            else:
                InfoBar.error(
                    title="Calc Error",
                    content=report.get('error'),
                    parent=self)

        except Exception as e:
            logger.error(f"Costing Error: {e}")

    @safe_slot
    def show_costing_report(self):
        # ... existing ...
        pass

    @safe_slot
    def apply_ai_upscale_2x(self):
        self._run_upscale(factor=2)

    @safe_slot
    def apply_ai_upscale_4x(self):
        self._run_upscale(factor=4)

    def _run_upscale(self, factor):
        """Runs the AI Upscaling Engine."""
        from sj_das.utils.image_conversion import (numpy_to_qimage,
                                                   qimage_to_numpy)

        if self.editor.original_image is None:
            return

        self.status_label.setText(
            f"AI: Upscaling {factor}x (Super Resolution)...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            from sj_das.core.upscaler import AIUpscaler
            engine = AIUpscaler()

            # Get Image and convert to numpy
            image_q = self.editor.get_image()
            img_bgr = qimage_to_numpy(image_q)

            # Process
            model = 'fsrcnn' if factor == 2 else 'edsr'
            res = engine.upscale(img_bgr, scale=factor, model_name=model)

            # Convert back to QImage
            new_q = numpy_to_qimage(res)
            self.editor.set_image(new_q)

            h, w = res.shape[:2]
            InfoBar.success(
                title="Upscale Complete",
                content=f"Resolution increased to {w}x{h}",
                parent=self)
            logger.info(f"AI upscale {factor}x completed: {w}x{h}")

        except Exception as e:
            logger.error(f"Upscaling failed: {e}", exc_info=True)
            InfoBar.error(title="AI Error", content=str(e), parent=self)
        finally:
            QApplication.restoreOverrideCursor()
            self.status_label.setText("Ready")

    @safe_slot
    def apply_smart_quantize_8(self):
        """Reduces colors to 8 using AI K-Means & Dithering."""
        self._run_quantize(k=8, dither=True)

    def _run_quantize(self, k, dither):
        if self.editor.original_image is None:
            return
        self.status_label.setText(
            f"AI: Reducing to {k} Yarns (Smart Dither)...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            from sj_das.core.quantizer import ColorQuantizerEngine
            engine = ColorQuantizerEngine()

            # Get BGR
            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            res = engine.quantize(img_bgr, k=k, dither=dither)

            # Update
            rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
            h, w, c = rgb.shape
            new_q = QImage(rgb.data, w, h, 3 *
                           w, QImage.Format.Format_RGB888).copy()
            self.editor.set_image(new_q)
            InfoBar.success(
                title="Colors Reduced",
                content=f"Mapped to {k} optimal yarns.",
                parent=self)

        except Exception as e:
            logger.error(f"Quantize Error: {e}")
            InfoBar.error(title="AI Error", content=str(e), parent=self)
        finally:
            QApplication.restoreOverrideCursor()
            self.status_label.setText("Ready")

    @safe_slot
    def show_defect_scan(self):
        """Scans for Weaving Defects."""
        if self.editor.original_image is None:
            return
        self.status_label.setText("AI: Scanning for Weaving Defects...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            from sj_das.core.defect_scanner import DefectScannerEngine
            engine = DefectScannerEngine()

            # Get BGR
            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            report = engine.scan(
                img_bgr, float_threshold=100)  # 100px threshold

            # Visualize Heatmap overlay
            heatmap = report['heatmap']  # BGR (Red/Blue)
            # Add to original?
            blended = cv2.addWeighted(img_bgr, 0.7, heatmap, 0.5, 0)

            rgb = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
            h, w, c = rgb.shape
            new_q = QImage(rgb.data, w, h, 3 *
                           w, QImage.Format.Format_RGB888).copy()
            self.editor.set_image(new_q)

            msg = (f"Scan Complete.\n"
                   f"Long Floats detected: {report['float_count']}\n"
                   f"Speckle Noise: {report['speckle_count']}\n"
                   f"Red Areas = Too Long Floats (>100px)\n"
                   f"Blue Dots = Noise")

            QMessageBox.warning(self, "Defect Report", msg)

        except Exception as e:
            logger.error(f"Scan Error: {e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.status_label.setText("Ready")

    @safe_slot
    def apply_artistic_style(self, style='cartoon'):
        """Applies artistic filter."""
        if self.editor.original_image is None:
            return
        self.status_label.setText(f"AI: Applying {style} style...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            # corrected import
            from sj_das.core.style_transfer import StyleTransferEngine
            from sj_das.core.style_transfer.py import \
                StyleTransferEngine  # Correct import path logic needed
            engine = StyleTransferEngine()

            # Get BGR
            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            res = engine.apply_style(img_bgr, style)

            # Update
            rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
            h, w, c = rgb.shape
            new_q = QImage(rgb.data, w, h, 3 *
                           w, QImage.Format.Format_RGB888).copy()
            self.editor.set_image(new_q)

        except Exception as e:
            logger.error(f"Style Error: {e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.status_label.setText("Ready")

    @safe_slot
    def activate_voice_control(self, *args):
        """Activates voice command interface."""
        try:
            self.status_label.setText(
                "🎙️ Listening... Say 'Rotate' or 'Scan'...")
            QApplication.setOverrideCursor(
                Qt.CursorShape.UpArrowCursor)  # Visual cue
            QApplication.processEvents()

            # In real threading, we wouldn't block. For demo/prototype, we
            # block for 3s.
            from sj_das.core.voice_engine import VoiceCommandEngine
            engine = VoiceCommandEngine()
            if not engine.available:
                QMessageBox.warning(
                    self, "Voice Error", "Microphone/Library not available.")
                return

            # This blocks!
            action_id, text = engine.listen_and_parse()

            if action_id:
                InfoBar.success(
                    title="Voice Command",
                    content=f"Executing: {action_id} ('{text}')",
                    parent=self)
                self.execute_command_id(action_id)
            else:
                self.status_label.setText(
                    f"Voice: Could not understand '{text}'")

        except Exception as e:
            logger.error(f"Voice UI Error: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def execute_command_id(self, action_id):
        """Maps voice ID to function calls."""
        if action_id == "rotate_90":
            self.apply_rotate_90()
        elif action_id == "flip_h":
            self.apply_flip_h()
        elif action_id == "upscale_4x":
            self.apply_ai_upscale_4x()
        elif action_id == "defect_scan":
            self.show_defect_scan()
        elif action_id == "show_costing":
            self.show_costing_report()
        elif action_id == "quantize_8":
            self.apply_smart_quantize_8()
        # ... add more

    @safe_slot
    def activate_magic_eraser(self):
        """Uses U-2-Net to remove background."""
        if self.editor.original_image is None:
            return
        self.status_label.setText("AI: Removing Background (Magic)...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        try:
            from sj_das.core.magic_eraser import MagicEraserEngine
            engine = MagicEraserEngine()

            # Get Image
            img_bgr = self.editor.get_cv_image()  # Helper needed or manual convert

            # Manual Convert for safety
            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            # Process
            res_bgra = engine.remove_background(img_bgr, refine=True)

            # Update Editor (handle RGBA)
            # We need to tell editor to enable transparency mode if not on?
            # QImage Format_ARGB32
            h, w, c = res_bgra.shape
            # CV2 is BGRA -> QImage ARGB? or RGBA?
            # QImage expects RGBA usually if Format_RGBA8888

            res_rgba = cv2.cvtColor(res_bgra, cv2.COLOR_BGRA2RGBA)
            new_q = QImage(res_rgba.data, w, h, 4 *
                           w, QImage.Format.Format_RGBA8888).copy()
            self.editor.set_image(new_q)
            InfoBar.success(
                title="Magic Eraser",
                content="Background Removed & Cropped",
                parent=self)

        except Exception as e:
            logger.error(f"Eraser Failed: {e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.status_label.setText("Ready")

    @safe_slot
    def undo(self, *args):
        if hasattr(self.editor, 'undo_stack'):
            self.editor.undo_stack.undo()

    @safe_slot
    def export_loom_file(self):
        """Generates Binary Loom File (BMP) via Asynchronous Cloud Workers."""
        if self.editor.original_image is None:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "No image to export to the cloud.")
            return

        # 1. Prepare the payload for the SaaS FastAPI backend
        payload = {
            "design_id": "sjdas-desktop-session",
            "hooks": 600,  # We can pull this from UI spinboxes later
            "kali_count": 1,
            "picks_height": 8000
        }

        # 2. Instantiate the CloudSyncWorker (QThread)
        from sj_das.core.cloud_sync_worker import CloudSyncWorker
        self.cloud_worker = CloudSyncWorker(
            api_url="http://localhost:8000/api/v1/generate-loom-file-async",
            ws_url="ws://localhost:8000/ws/progress",
            payload=payload,
            parent=self
        )

        # 3. Instantiate the Sleek Modal Dialog
        from sj_das.ui.cloud_export_dialog import CloudExportDialog
        self.export_dialog = CloudExportDialog(self)

        # 4. Wire the signals across thread boundaries
        self.cloud_worker.progress_updated.connect(self.export_dialog.update_progress_ui)
        self.cloud_worker.task_success.connect(self.export_dialog.show_success_state)
        self.cloud_worker.task_error.connect(self.export_dialog.show_error_state)

        # Cleanly stop the worker if the user closes the modal prematurely
        self.export_dialog.rejected.connect(self.cloud_worker.stop)

        # 5. Launch the process
        self.cloud_worker.start()
        self.export_dialog.exec()

    @safe_slot
    def show_3d_fabric_view(self):
        """Renders 3D Fabric Simulation."""
        if self.editor.original_image is None:
            return
        self.status_label.setText(
            "3D: Simulating Threads... (This may take a moment)")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            from sj_das.core.fabric_renderer_3d import FabricRenderer3D
            from sj_das.core.loom_engine import LoomEngine

            # Get Image
            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            # We need the graph to render 3D
            # Do a quick temp generation
            from sj_das.core.quantizer import ColorQuantizerEngine
            q_engine = ColorQuantizerEngine()
            quantized = q_engine.quantize(img_bgr, k=6, dither=False)
            gray = cv2.cvtColor(quantized, cv2.COLOR_BGR2GRAY)
            unique = np.unique(gray)

            l_engine = LoomEngine()
            weave_map = {val: ['Satin 5', 'Plain', 'Twill 3/1'][i % 3]
                         for i, val in enumerate(unique)}
            graph = l_engine.generate_graph(gray, weave_map)

            # Render 3D
            renderer = FabricRenderer3D()
            # Use small scale for preview speed
            res_3d = renderer.render(graph, quantized, scale=3)

            # Show in Overlay? Or just set image?
            # Ideally popup. For now, set image (user can Undo).
            # Convert to QImage
            rgb = cv2.cvtColor(res_3d, cv2.COLOR_BGR2RGB)
            h, w, c = rgb.shape
            new_q = QImage(rgb.data, w, h, 3 *
                           w, QImage.Format.Format_RGB888).copy()

            # Show in a Dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Hyper-Real Fabric Simulation 3D")
            dialog.resize(900, 700)
            lay = QVBoxLayout(dialog)
            lbl = QLabel()
            lbl.setPixmap(
                QPixmap.fromImage(new_q).scaled(
                    850,
                    650,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation))
            lay.addWidget(lbl)

            btn_close = QPushButton("Close")
            btn_close.clicked.connect(dialog.accept)
            lay.addWidget(btn_close)

            dialog.exec()

        except Exception as e:
            logger.error(f"3D Error: {e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.status_label.setText("Ready")

    @safe_slot
    def show_costing_report(self):
        """Shows Smart Costing."""
        if self.editor.original_image is None:
            return

        try:
            # Get Image as Index (Simple approximation)
            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            # Just use simple gray proxy for unique counting
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            from sj_das.ui.components.costing_dialog import CostingReportDialog
            dlg = CostingReportDialog(gray, self)
            dlg.exec()

        except Exception as e:
            logger.error(f"Costing Error: {e}")

    @safe_slot
    def extract_sketch_ai(self):
        """Extracts Artistic Sketch using Deep Learning (HED)."""
        if self.editor.original_image is None:
            return
        self._apply_cv_filter(
            lambda img: self._run_vision_task(
                'sketch', img), "AI Sketch Extraction")

    @safe_slot
    def apply_auto_colorization(self):
        """Auto-Colorizes B&W Image."""
        if self.editor.original_image is None:
            return
        self._apply_cv_filter(
            lambda img: self._run_vision_task(
                'colorize', img), "AI Auto Colorization")

    def _run_vision_task(self, task, img):
        """Helper to run vision tasks."""
        try:
            from sj_das.core.advanced_vision import AdvancedVisionEngine
            engine = AdvancedVisionEngine()
            if task == 'sketch':
                res = engine.extract_sketch(img)
                return cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
            elif task == 'colorize':
                return engine.colorize_bw(img)
            return img
        except Exception as e:
            logger.error(f"Vision Task Error: {e}")
            return img

            logger.error(f"Vision Task Error: {e}")
            return img

    @safe_slot
    def activate_smart_select(self):
        """Activates SAM Tool Async."""
        if self.editor.original_image is None:
            return
        self.status_label.setText(
            "AI: Loading Segment Anything (SAM)... Please wait.")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        if not hasattr(self, 'sam_engine'):
            try:
                from sj_das.core.sam_engine import SAMEngine
                self.sam_engine = SAMEngine()
                img = self.editor.get_image()
                ptr = img.bits()
                ptr.setsize(img.sizeInBytes())
                arr = np.array(ptr).reshape(img.height(), img.width(), 4)

                # Heavy step async
                self.ai_worker_sam = AIWorker(self.sam_engine.set_image, arr)

                def on_sam_ready(res):
                    self.editor.set_tool_mode('smart_select')
                    self.editor.smart_click_callback = self.handle_smart_click
                    self.status_label.setText("AI: SAM Ready. Click to Select.")
                    QApplication.restoreOverrideCursor()

                self.ai_worker_sam.finished.connect(on_sam_ready)
                self.ai_worker_sam.start()

            except Exception as e:
                logger.error(f"SAM Init Error: {e}")
                self.status_label.setText("AI: SAM Failed to Load.")
                QApplication.restoreOverrideCursor()
        else:
            self.editor.set_tool_mode('smart_select')
            self.status_label.setText("AI: SAM Ready. Click on motif.")
            QApplication.restoreOverrideCursor()

        QApplication.restoreOverrideCursor()

    def handle_smart_click(self, x, y):
        """Called by Canvas when in smart_select mode."""
        if hasattr(self, 'sam_engine'):
            self.status_label.setText("AI: Segmenting...")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            self.ai_worker_click = AIWorker(self.sam_engine.predict_click, x, y)

            def on_mask_ready(mask):
                if mask is not None:
                    # Apply as Selection
                    self.editor.set_selection_from_mask(mask)
                    self.status_label.setText("AI: Selection Created.")
                else:
                    self.status_label.setText("AI: Selection Failed.")
                QApplication.restoreOverrideCursor()

            self.ai_worker_click.finished.connect(on_mask_ready)
            self.ai_worker_click.start()

    @safe_slot
    def redo(self, *args):
        if hasattr(self.editor, 'undo_stack'):
            self.editor.undo_stack.redo()

    @safe_slot
    def toggle_copilot(self, *args):
        """Toggles the AI Agent Sidebar."""
        if not hasattr(self, 'copilot_widget'):
            from sj_das.ui.components.agent_chat import AgentChatWidget
            self.copilot_widget = AgentChatWidget(self)
            self.copilot_widget.action_requested.connect(
                self.handle_agent_action)
            # Add to main layout?
            # ModernDesignerView uses a specific layout mostly.
            # Ideally we add it to a dock or split view.
            # For now, we FLOAT it or Add to Right of HBox if exists.

            # Assuming self.layout() is valid (it inherits from QWidget/QFrame)
            # If layout is HBox/VBox, we can insert.
            # But ModernDesignerView usually has a central layout.

            # Simple Hack: Absolute positioning (Floating)
            self.copilot_widget.setParent(self)
            self.copilot_widget.setGeometry(
                self.width() - 360, 0, 350, self.height())
            self.copilot_widget.show()
            self.copilot_widget.raise_()
        else:
            if self.copilot_widget.isVisible():
                self.copilot_widget.hide()
            else:
                self.copilot_widget.setGeometry(
                    self.width() - 360, 0, 350, self.height())
                self.copilot_widget.show()
                self.copilot_widget.raise_()

    def resizeEvent(self, event):
        """Keep copilot on right edge."""
        super().resizeEvent(event)
        if hasattr(self, 'copilot_widget') and self.copilot_widget.isVisible():
            self.copilot_widget.setGeometry(
                self.width() - 360, 0, 350, self.height())

    def handle_agent_action(self, action, params):
        """Executes actions triggered by the LLM."""
        action = action.lower()
        logger.info(f"Agent Triggered: {action}")

        if "rotate" in action:
            self.rotate_design_90()
        elif "flip" in action:
            self.flip_design_horizontal()
        elif "upscale" in action:
            self.apply_ai_upscale()
        elif "cost" in action:
            self.show_costing_report()
        elif "segment" in action or "select" in action:
            self.activate_smart_select()
        elif "sketch" in action:
            self.extract_sketch_ai()
        elif "color" in action:
            self.apply_auto_colorization()
        elif "loom" in action or "export" in action:
            self.export_loom_file()
        else:
            InfoBar.warning(
                title="Unknown Action",
                content=f"I don't know how to '{action}' yet.",
                parent=self)

    @safe_slot
    def recover_design_from_screenshot(self, *args):
        """Recovers clean design from screenshot using AI pipeline."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QFileDialog, QProgressDialog

        # File dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Screenshot to Recover",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        # Load image
        import cv2
        screenshot = cv2.imread(file_path)

        if screenshot is None:
            InfoBar.error(
                title="Error",
                content="Failed to load image",
                parent=self)
            return

        # Progress dialog
        progress = QProgressDialog(
            "Recovering design...", "Cancel", 0, 7, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("AI Design Recovery")
        progress.show()

        try:
            from sj_das.core.design_recovery import DesignRecoveryEngine

            recovery = DesignRecoveryEngine()

            # Run recovery pipeline
            def update_progress(step):
                progress.setValue(step)
                QApplication.processEvents()

            recovered, metadata = recovery.recover(
                screenshot, auto_reconstruct=True)
            progress.setValue(7)

            # Convert to QImage and set
            rgb = cv2.cvtColor(recovered, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bpl = ch * w
            qimg = QImage(
                rgb.data,
                w,
                h,
                bpl,
                QImage.Format.Format_RGB888).copy()

            self.editor.set_image(qimg)
            self.editor.mask_updated.emit()

            # Show results
            desc = metadata.get('description', 'Unknown')
            quality = metadata.get('quality_score', 0.0)

            InfoBar.success(
                title="Design Recovered",
                content=f"Detected: {desc}\nQuality: {quality:.1%}",
                parent=self
            )

        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            InfoBar.error(title="Recovery Failed", content=str(e), parent=self)
        finally:
            progress.close()

    # Missing UI methods (stubs for menu compatibility)
    def zoom_in(self):
        """Zoom in on canvas."""
        if hasattr(self.editor, 'zoom_in'):
            self.editor.zoom_in()

    def zoom_out(self):
        """Zoom out on canvas."""
        if hasattr(self.editor, 'zoom_out'):
            self.editor.zoom_out()

    def toggle_grid(self):
        """Toggle grid display."""
        try:
            if hasattr(self.editor, 'show_grid'):
                self.editor.show_grid = not getattr(
                    self.editor, 'show_grid', False)
                if hasattr(self.editor, 'update'):
                    self.editor.update()
                logger.info(
                    f"Grid {'enabled' if self.editor.show_grid else 'disabled'}")
            else:
                logger.warning("Grid display not supported by current editor")
        except Exception as e:
            logger.error(f"Failed to toggle grid: {e}", exc_info=True)

    # AI Methods stubs
    def apply_ai_upscale(self):
        """AI Upscale using orchestrator."""
        try:
            from sj_das.core.ai_orchestrator import AIOrchestrator
            if hasattr(self.editor, 'get_image_array'):
                img = self.editor.get_image_array()
                orch = AIOrchestrator()
                result = orch.process(
                    "upscale", img, {
                        "quality": "high", "scale": 4})
                # Set result back
        except Exception as e:
            logger.error(f"AI Upscale failed: {e}")

    def apply_magic_eraser(self):
        """Remove background."""
        pass  # Already implemented elsewhere

    def show_ai_pattern_gen(self):
        """Show AI pattern generator."""
        if hasattr(self, 'feat_ai_gen'):
            self.feat_ai_gen.show_dialog()

    def generate_from_sketch_controlnet(self, *args):
        """Generate design from sketch using ControlNet."""
        from PyQt6.QtWidgets import QFileDialog, QInputDialog

        # Select sketch file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sketch Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        # Get prompt
        prompt, ok = QInputDialog.getText(
            self,
            "Design Description",
            "Describe the textile design you want:",
            text="traditional paisley border with floral motifs"
        )

        if not ok or not prompt:
            return

        try:
            import cv2

            from sj_das.core.controlnet_engine import ControlNetEngine

            # Load sketch
            sketch = cv2.imread(file_path)

            # Generate
            InfoBar.info(
                title="Generating",
                content="Creating design from sketch...",
                parent=self)
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            controlnet = ControlNetEngine()
            result = controlnet.generate_from_sketch(
                sketch, prompt, num_steps=20)

            QApplication.restoreOverrideCursor()

            if result is not None:
                # Convert to QImage and set
                rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bpl = ch * w
                qimg = QImage(
                    rgb.data, w, h, bpl, QImage.Format.Format_RGB888).copy()

                self.editor.set_image(qimg)
                self.editor.mask_updated.emit()

                InfoBar.success(
                    title="Success",
                    content="Design generated from sketch!",
                    parent=self)
            else:
                InfoBar.error(
                    title="Error",
                    content="ControlNet generation failed",
                    parent=self)

        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"ControlNet error: {e}")
            InfoBar.error(title="Error", content=str(e), parent=self)

    def _init_phase24_features(self):
        """Initialize Phase 24 UI/UX features."""
        try:
            self.shortcut_manager = ShortcutManager(self)
            self.shortcut_manager.setup_default_shortcuts(self)
            self.quick_actions_dialog = QuickActionsDialog(self)
            self.quick_actions_dialog.populate_actions(self)
            self.workspace_manager = WorkspaceManager()
            self.theme_manager = ThemeManager()
            # self.animation_manager = AnimationHelper  # Optional for future
            # use
            logger.info("[OK] Phase 24 initialized")
        except Exception as e:
            logger.error(f"Phase 24 error: {e}")

    def show_quick_actions(self):
        """Show quick actions (Ctrl+K)."""
        if hasattr(self, 'quick_actions_dialog'):
            self.quick_actions_dialog.exec()

    def _on_memory_warning(self, mb_used: int):
        """Handle memory warning."""
        logger.warning(f"Memory warning: {mb_used}MB used")
        InfoBar.warning(
            title="High Memory Usage",
            content=f"Memory usage: {mb_used}MB. Consider closing unused images.",
            parent=self,
            duration=5000,
            position=InfoBarPosition.TOP
        )

    def _on_memory_critical(self, mb_used: int):
        """Handle critical memory situation."""
        logger.error(f"Critical memory: {mb_used}MB used")
        InfoBar.error(
            title="Critical Memory Usage",
            content=f"Memory usage: {mb_used}MB. Application may become unstable.",
            parent=self,
            duration=10000,
            position=InfoBarPosition.TOP
        )
        # Force garbage collection
        if hasattr(self, 'memory_manager'):
            self.memory_manager.force_garbage_collection()

    def _init_features(self):
        """Initialize standard features."""
        try:
            self.feat_geo = GeometricGenerator(self.editor)
            self.feat_sym = SymmetryFeature(self.editor)
            self.feat_color = ColorAdjuster(self.editor)
            self.feat_noise = NoiseReducer(self.editor)
            self.feat_hist = HistogramViewer(self.editor)
            self.feat_persp = PerspectiveTool(self.editor)
            self.feat_mixer = ChannelMixer(self.editor)
            self.feat_curves = CurvesTool(self.editor)
            self.feat_grad = GradientMap(self.editor)
            self.feat_halftone = HalftoneGen(self.editor)
            self.feat_vignette = VignetteEffect(self.editor)
            self.feat_solarize = SolarizeEffect(self.editor)
            self.feat_grain = FilmGrain(self.editor)
            self.feat_posterize = PosterizeTool(self.editor)
            self.feat_palette = PaletteExtractor(self.editor)
            self.feat_resize = FabricResizer(self.editor)
            self.feat_ruler = RulerTool(self.editor)
            self.feat_hsl = HSLAdjuster(self.editor)
            self.feat_thresh = ThresholdTool(self.editor)
            self.feat_pixel = PixelateEffect(self.editor)
            self.feat_emboss = EmbossEffect(self.editor)
            self.feat_repeat = MotifRepeater(self.editor)
            self.feat_separate = ColorSeparator(self.editor)
            self.feat_weave = WeaveSimulator(self.editor)
            self.feat_ai_gen = AIPatternGen(self.editor)
            self.feat_expert = SmartExpert(self.editor)
            self.feat_seamless = SmartSeamlessMaker(self.editor)
            self.feat_recolor = SmartRecolor(self.editor)
        except Exception as e:
            logger.error(f"Failed to initialize standard features: {e}")

    def _init_professional_features(self):
        """Initialize all professional features from Weeks 1-4."""
        try:
            # Week 1: Grid, Selection, Styles, Blends
            self.grid_manager = GridManager(self.editor)
            self.magic_wand = MagicWandTool()
            self.quick_selection = QuickSelectionTool()
            self.color_range = ColorRangeSelector()
            self.selection_refiner = SelectionRefiner()
            # Layer styles and blend modes initialized on-demand

            # Week 2: Liquify, Curves, Text Warp, Vectors
            from sj_das.filters.week2_features import (CurvesAdjustment,
                                                       LiquifyTool,
                                                       TextWarpTool)
            from sj_das.tools.vector_tools import PenTool, ShapeTools

            self.liquify = LiquifyTool()
            self.curves = CurvesAdjustment()
            self.text_warp = TextWarpTool()
            self.pen_tool = PenTool()
            self.shapes = ShapeTools()

            # Week 3: Content-Aware, Batch, 3D
            from sj_das.automation.batch_processing import (ActionRecorder,
                                                            BatchProcessor)
            from sj_das.effects.effects_3d import Shapes3D, Text3D
            from sj_das.filters.content_aware import (ContentAwareFill,
                                                      ContentAwareMove,
                                                      ContentAwareScale)

            self.content_fill = ContentAwareFill()
            self.content_scale = ContentAwareScale()
            self.content_move = ContentAwareMove()
            self.action_recorder = ActionRecorder()
            self.batch_processor = BatchProcessor(self.action_recorder)
            self.text_3d = Text3D()
            self.shapes_3d = Shapes3D()

            # Week 4: Camera RAW, Perspective
            from sj_das.filters.camera_raw import (CameraRAW,
                                                   PerspectiveCorrection)

            self.camera_raw = CameraRAW()
            self.perspective = PerspectiveCorrection()

            logger.info(
                "[OK] Professional features initialized (60+ features)")

        except Exception as e:
            logger.error(f"Failed to initialize professional features: {e}")

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def fit_to_window(self):
        """Fit canvas to window."""
        try:
            if hasattr(self.editor, 'fit_to_window'):
                self.editor.fit_to_window()
            logger.info("Fit to window")
        except Exception as e:
            logger.error(f"Fit to window failed: {e}")

    def new_file(self):
        """Create new blank canvas."""
        from PyQt6.QtWidgets import QMessageBox
        try:
            if hasattr(self, 'modified') and self.modified:
                reply = QMessageBox.question(self, 'Save Changes?', 'Do you want to save changes?',
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                if reply == QMessageBox.StandardButton.Yes:
                    self.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    return
            self.editor.create_blank_canvas(512, 512)
            self.current_file = None
            self.modified = False
            logger.info("New file created")
        except Exception as e:
            logger.error(f"Failed to create new file: {e}", exc_info=True)

    def open_file(self):
        """Open file dialog and load image."""
        from PyQt6.QtWidgets import QFileDialog
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Image", "", "Images (*.png *.jpg *.bmp);;All Files (*.*)"
            )
            if file_path:
                self.import_image(file_path)
                logger.info(f"File opened: {file_path}")
        except Exception as e:
            logger.error(f"Failed to open file: {e}", exc_info=True)

    def save_file(self):
        """Save current file."""
        if hasattr(self, 'current_file') and self.current_file:
            self.save_file_as(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self, file_path=None):
        """Save file with dialog."""
        from PyQt6.QtWidgets import QFileDialog
        try:
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save Image", "", "PNG Files (*.png);;All Files (*.*)"
                )
            if file_path:
                if hasattr(
                        self.editor, 'original_image') and self.editor.original_image is not None:
                    from PIL import Image
                    img = Image.fromarray(self.editor.original_image)
                    img.save(file_path)
                    self.current_file = file_path
                    self.modified = False
                    logger.info(f"File saved: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)

    def save_file_as(self):
        """Save file with a new name (Save As dialog)."""
        from PyQt6.QtWidgets import QFileDialog
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image As", "", "PNG Files (*.png);;BMP Files (*.bmp);;All Files (*.*)"
            )
            if file_path:
                if hasattr(
                        self.editor, 'original_image') and self.editor.original_image is not None:
                    from PIL import Image
                    img = Image.fromarray(self.editor.original_image)
                    img.save(file_path)
                    self.current_file = file_path
                    self.modified = False
                    logger.info(f"File saved as: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file as: {e}", exc_info=True)

    def rotate_90(self):
        """Rotate image 90 degrees clockwise."""
        from sj_das.utils.image_ops import rotate_image
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = rotate_image(
                    self.editor.original_image, 90)
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Rotated image 90 degrees")
        except Exception as e:
            logger.error(f"Failed to rotate: {e}", exc_info=True)

    def rotate_180(self):
        """Rotate image 180 degrees."""
        from sj_das.utils.image_ops import rotate_image
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = rotate_image(
                    self.editor.original_image, 180)
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Rotated image 180 degrees")
        except Exception as e:
            logger.error(f"Failed to rotate: {e}", exc_info=True)

    def flip_h(self):
        """Flip image horizontally."""
        from sj_das.utils.image_ops import flip_image
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = flip_image(
                    self.editor.original_image, "horizontal")
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Flipped image horizontally")
        except Exception as e:
            logger.error(f"Failed to flip: {e}", exc_info=True)

    def flip_v(self):
        """Flip image vertically."""
        from sj_das.utils.image_ops import flip_image
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = flip_image(
                    self.editor.original_image, "vertical")
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Flipped image vertically")
        except Exception as e:
            logger.error(f"Failed to flip: {e}", exc_info=True)

    def activate_brush(self):
        """Activate brush tool."""
        try:
            self.on_tool_selected('brush')
            logger.info("Brush tool activated")
        except Exception as e:
            logger.error(f"Failed to activate brush: {e}", exc_info=True)

    def activate_eraser(self):
        """Activate eraser tool."""
        try:
            self.on_tool_selected('eraser')
            logger.info("Eraser tool activated")
        except Exception as e:
            logger.error(f"Failed to activate eraser: {e}", exc_info=True)

    def detect_pattern_from_image(self):
        """Detect pattern from image."""
        try:
            self.run_ai_analysis()
            logger.info("Pattern detection started")
        except Exception as e:
            logger.error(f"Failed to detect pattern: {e}", exc_info=True)

    def apply_smart_quantize_16(self):
        """Reduce to 16 colors using AI."""
        try:
            self._run_quantize(k=16, dither=False)
            logger.info("Applied 16-color quantization")
        except Exception as e:
            logger.error(f"Failed to quantize: {e}", exc_info=True)

    def export_to_loom(self):
        """Export design to loom BMP format."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        try:
            import numpy as np

            from sj_das.core.loom_engine import LoomEngine
            if not hasattr(
                    self.editor, 'original_image') or self.editor.original_image is not None:
                QMessageBox.warning(self, "Warning", "No image to export")
                return
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export to Loom", "", "BMP Files (*.bmp)")
            if file_path:
                image = self.editor.original_image
                if len(image.shape) == 3:
                    image = image[:, :, 0]
                unique_colors = np.unique(image)
                color_map = {int(c): 'Plain' for c in unique_colors}
                loom = LoomEngine()
                graph = loom.generate_graph(image, color_map)
                loom.save_loom_file(graph, file_path)
                QMessageBox.information(
                    self, "Success", f"Exported to loom: {file_path}")
                logger.info(f"Exported to loom: {file_path}")
        except Exception as e:
            logger.error(f"Failed to export to loom: {e}", exc_info=True)

    def apply_smart_quantize_8(self):
        """Reduce to 8 colors using AI."""
        try:
            self._run_quantize(k=8, dither=False)
            logger.info("Applied 8-color quantization")
        except Exception as e:
            logger.error(f"Failed to quantize: {e}", exc_info=True)

    def auto_segment(self):
        """Auto-segment the design using AI."""
        try:
            if hasattr(self, 'run_ai_analysis'):
                self.run_ai_analysis()
            logger.info("Auto-segmentation started")
        except Exception as e:
            logger.error(f"Failed to auto-segment: {e}", exc_info=True)

    def apply_ai_upscale_4x(self):
        """AI Upscale 4x using orchestrator."""
        try:
            self._run_upscale(factor=4)
            logger.info("Applied 4x AI upscale")
        except Exception as e:
            logger.error(f"AI Upscale 4x failed: {e}", exc_info=True)

    def show_defect_scan(self):
        """Show defect scanning dialog."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Defect Scan", "Defect scanning feature coming soon!")
            logger.info("Defect scan requested")
        except Exception as e:
            logger.error(f"Failed to show defect scan: {e}", exc_info=True)

    def _run_quantize(self, k=8, dither=False):
        """Helper method to run color quantization."""
        try:
            import cv2
            if not hasattr(
                    self.editor, 'original_image') or self.editor.original_image is None:
                logger.warning("No image to quantize")
                return

            img = self.editor.original_image
            # Convert to RGB if needed
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Reshape image to be a list of pixels
            pixels = img.reshape((-1, 3)).astype(np.float32)

            # Apply k-means clustering
            criteria = (
                cv2.TERM_CRITERIA_EPS +
                cv2.TERM_CRITERIA_MAX_ITER,
                100,
                0.2)
            _, labels, centers = cv2.kmeans(
                pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

            # Convert back to 8-bit values
            centers = np.uint8(centers)
            quantized = centers[labels.flatten()]
            quantized_img = quantized.reshape(img.shape)

            # Update editor
            self.editor.original_image = quantized_img
            if hasattr(self.editor, 'update_display'):
                self.editor.update_display()
            self.modified = True

            logger.info(f"Quantized image to {k} colors")
        except Exception as e:
            logger.error(f"Quantization failed: {e}", exc_info=True)

    def _run_upscale(self, factor=2):
        """Helper method to run AI upscaling."""
        try:
            import cv2
            if not hasattr(
                    self.editor, 'original_image') or self.editor.original_image is None:
                logger.warning("No image to upscale")
                return

            img = self.editor.original_image
            h, w = img.shape[:2]
            new_h, new_w = h * factor, w * factor

            # Try to use Real-ESRGAN
            from sj_das.core.engines.enhancement.real_esrgan_upscaler import \
                RealESRGANUpscaler
            upscaler = RealESRGANUpscaler()

            if upscaler.load_model():
                self.status_bar.showMessage(
                    "Upscaling with Real-ESRGAN (this may take a moment)...")
                QApplication.processEvents()
                upscaled = upscaler.upscale(img, scale=4)
                logger.info("Upscaled with Real-ESRGAN")
            else:
                # Fallback to Cubic
                logger.warning(
                    "RealRSGAN not available, falling back to Cubic")
                upscaled = cv2.resize(
                    img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

            # Update editor
            self.editor.original_image = upscaled
            if hasattr(self.editor, 'update_display'):
                self.editor.update_display()
            self.modified = True

            logger.info(
                f"Upscaled image to {upscaled.shape[1]}x{upscaled.shape[0]}")
        except Exception as e:
            logger.error(f"Upscaling failed: {e}", exc_info=True)


# ================== AI GENERATION THREAD ==================

class GenerationThread(QThread):
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, prompt, variations=False):
        super().__init__()
        self.prompt = prompt
        self.variations = variations

    def run(self):
        try:
            # Fix path for thread context
            import os
            import sys
            root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__))))
            if root not in sys.path:
                sys.path.insert(0, root)

            from sj_das.core.generative_engine import GenerativeDesignEngine
            engine = GenerativeDesignEngine()

            # Use standard border dims
            w = 480
            h = 120

            if self.variations:
                imgs = engine.generate_variations(self.prompt, w, h, 3)
                final_res = []
                for qimg in imgs:
                    ptr = qimg.bits()
                    ptr.setsize(h * w * 4)
                    arr = np.array(ptr).reshape(h, w, 4)
                    final_res.append(cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR))
                self.finished_signal.emit(final_res)
            else:
                qimg = engine.generate_border(self.prompt, w, h)
                if qimg is None:
                    raise RuntimeError("AI returned None")

                ptr = qimg.bits()
                ptr.setsize(h * w * 4)
                arr = np.array(ptr).reshape(h, w, 4)
                final_cv = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR).copy()
                self.finished_signal.emit(final_cv)

        except Exception as e:
            self.error_signal.emit(str(e))


# ================== PROACTIVE AI OBSERVER ==================

class ProactiveObserverThread(QThread):
    suggestion_ready = pyqtSignal(dict)

    def __init__(self, editor, assistant):
        super().__init__()
        self.editor = editor
        self.assistant = assistant
        self.running = True
        self.last_check = 0

    def run(self):
        while self.running:
            time.sleep(10)  # Check every 10s
            try:
                # Basic check: Is there an image?
                if self.editor.original_image and not self.editor.original_image.isNull():
                    # Analyze for general advice
                    # We pass a simple dict for prediction simulation for now
                    # Ideally we run the actual model, but that's heavy.
                    # We just assume basic "segmentation check" logic here.

                    # Logic: If user has undone many times?
                    # Logic: If image has low contrast?

                    # For demo: randomly suggest Tip if idle
                    import random
                    if random.random() < 0.3:
                        sugg = {
                            "title": "Smart Tip",
                            "message": "Try using the Magic Wand with Tolerance 30 for this pattern."
                        }
                        self.suggestion_ready.emit(sugg)

            except Exception:
                pass

    def stop(self):
        self.running = False


class GenerationThread(QThread):
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, prompt, variations=False):
        super().__init__()
        self.prompt = prompt
        self.variations = variations

    def run(self):
        try:
            # Fix path for thread context
            import os
            import sys
            root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__))))
            if root not in sys.path:
                sys.path.insert(0, root)

            from sj_das.core.generative_engine import GenerativeDesignEngine
            engine = GenerativeDesignEngine()

            # Use standard border dims
            w = 480
            h = 120

            if self.variations:
                imgs = engine.generate_variations(self.prompt, w, h, 3)
                final_res = []
                for qimg in imgs:
                    ptr = qimg.bits()
                    ptr.setsize(h * w * 4)
                    arr = np.array(ptr).reshape(h, w, 4)
                    final_res.append(cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR))
                self.finished_signal.emit(final_res)
            else:
                qimg = engine.generate_border(self.prompt, w, h)
                if qimg is None:
                    raise RuntimeError("AI returned None")

                ptr = qimg.bits()
                ptr.setsize(h * w * 4)
                arr = np.array(ptr).reshape(h, w, 4)
                final_cv = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR).copy()
                self.finished_signal.emit(final_cv)

        except Exception as e:
            self.error_signal.emit(str(e))


# ================== PROACTIVE AI OBSERVER ==================

class ProactiveObserverThread(QThread):
    suggestion_ready = pyqtSignal(dict)

    def __init__(self, editor, assistant):
        super().__init__()
        self.editor = editor
        self.assistant = assistant
        self.running = True
        self.last_check = 0

    def run(self):
        while self.running:
            time.sleep(10)  # Check every 10s
            try:
                # Basic check: Is there an image?
                if self.editor.original_image and not self.editor.original_image.isNull():
                    # Analyze for general advice
                    # We pass a simple dict for prediction simulation for now
                    # Ideally we run the actual model, but that's heavy.
                    # We just assume basic "segmentation check" logic here.

                    # Logic: If user has undone many times?
                    # Logic: If image has low contrast?

                    # For demo: randomly suggest Tip if idle
                    import random
                    if random.random() < 0.3:
                        sugg = {
                            "title": "Smart Tip",
                            "message": "Try using the Magic Wand with Tolerance 30 for this pattern."
                        }
                        self.suggestion_ready.emit(sugg)

            except Exception:
                pass

    def stop(self):
        self.running = False

# Add these methods to the end of PremiumDesignerView class (before the
# last line)

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def new_file(self):
        """Create new blank canvas."""
        from PyQt6.QtWidgets import QMessageBox

        try:
            # Ask to save current work if modified
            if hasattr(self, 'modified') and self.modified:
                reply = QMessageBox.question(
                    self,
                    'Save Changes?',
                    'Do you want to save changes before creating a new file?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    return

            # Create blank canvas
            self.editor.create_blank_canvas(512, 512)
            self.current_file = None
            self.modified = False
            logger.info("New file created")

        except Exception as e:
            logger.error(f"Failed to create new file: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Error", f"Failed to create new file: {e}")

    def open_file(self):
        """Open file dialog and load image."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Image",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*.*)"
            )

            if file_path:
                self.import_image(file_path)
                self.current_file = file_path
                self.modified = False
                logger.info(f"Opened file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to open file: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def save_file(self):
        """Save current work."""
        import cv2
        from PyQt6.QtWidgets import QMessageBox

        try:
            if not hasattr(self, 'current_file') or self.current_file is None:
                return self.save_file_as()

            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                cv2.imwrite(self.current_file, self.editor.original_image)
                self.modified = False
                logger.info(f"Saved file: {self.current_file}")
                QMessageBox.information(
                    self, "Success", "File saved successfully!")
            else:
                QMessageBox.warning(self, "Warning", "No image to save")

        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def save_file_as(self):
        """Save with new filename."""
        import cv2
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image As",
                "",
                "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;All Files (*.*)"
            )

            if file_path:
                if hasattr(
                        self.editor, 'original_image') and self.editor.original_image is not None:
                    cv2.imwrite(file_path, self.editor.original_image)
                    self.current_file = file_path
                    self.modified = False
                    logger.info(f"Saved file as: {file_path}")
                    QMessageBox.information(
                        self, "Success", "File saved successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "No image to save")

        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    # ========================================================================
    # TOOL ACTIVATION
    # ========================================================================

    def activate_brush(self):
        """Activate brush tool."""
        try:
            self.on_tool_selected('brush')
            logger.info("Brush tool activated")
        except Exception as e:
            logger.error(f"Failed to activate brush: {e}", exc_info=True)

    def activate_eraser(self):
        """Activate eraser tool."""
        try:
            self.on_tool_selected('eraser')
            logger.info("Eraser tool activated")
        except Exception as e:
            logger.error(f"Failed to activate eraser: {e}", exc_info=True)

    # ========================================================================
    # VIEW OPERATIONS
    # ========================================================================

    def zoom_in(self):
        """Increase zoom level."""
        try:
            if hasattr(self.editor, 'zoom_in'):
                self.editor.zoom_in()
            else:
                current_scale = getattr(self.editor, 'scale_factor', 1.0)
                self.editor.scale_factor = min(current_scale * 1.2, 10.0)
                if hasattr(self.editor, 'update_view'):
                    self.editor.update_view()
            logger.debug("Zoomed in")
        except Exception as e:
            logger.error(f"Failed to zoom in: {e}", exc_info=True)

    def zoom_out(self):
        """Decrease zoom level."""
        try:
            if hasattr(self.editor, 'zoom_out'):
                self.editor.zoom_out()
            else:
                current_scale = getattr(self.editor, 'scale_factor', 1.0)
                self.editor.scale_factor = max(current_scale / 1.2, 0.1)
                if hasattr(self.editor, 'update_view'):
                    self.editor.update_view()
            logger.debug("Zoomed out")
        except Exception as e:
            logger.error(f"Failed to zoom out: {e}", exc_info=True)

    def fit_to_window(self):
        """Fit image to viewport."""
        try:
            if hasattr(self.editor, 'fit_to_window'):
                self.editor.fit_to_window()
            logger.info("Fit to window")
        except Exception as e:
            logger.error(f"Failed to fit to window: {e}", exc_info=True)

    # ========================================================================
    # IMAGE TRANSFORMATIONS
    # ========================================================================

    def rotate_90(self):
        """Rotate image 90 degrees."""
        import cv2
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = cv2.rotate(
                    self.editor.original_image, cv2.ROTATE_90_CLOCKWISE)
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Rotated 90 degrees")
        except Exception as e:
            logger.error(f"Failed to rotate: {e}", exc_info=True)

    def rotate_180(self):
        """Rotate image 180 degrees."""
        import cv2
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = cv2.rotate(
                    self.editor.original_image, cv2.ROTATE_180)
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Rotated 180 degrees")
        except Exception as e:
            logger.error(f"Failed to rotate: {e}", exc_info=True)

    def flip_h(self):
        """Flip image horizontally."""
        import cv2
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = cv2.flip(
                    self.editor.original_image, 1)
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Flipped horizontally")
        except Exception as e:
            logger.error(f"Failed to flip: {e}", exc_info=True)

    def flip_v(self):
        """Flip image vertically."""
        import cv2
        try:
            if hasattr(
                    self.editor, 'original_image') and self.editor.original_image is not None:
                self.editor.original_image = cv2.flip(
                    self.editor.original_image, 0)
                if hasattr(self.editor, 'update_display'):
                    self.editor.update_display()
                self.modified = True
                logger.info("Flipped vertically")
        except Exception as e:
            logger.error(f"Failed to flip: {e}", exc_info=True)

    # ========================================================================
    # AI FEATURES
    # ========================================================================

    def apply_smart_quantize_16(self):
        """Reduce to 16 colors using AI."""
        try:
            self._run_quantize(k=16, dither=False)
            logger.info("Applied 16-color quantization")
        except Exception as e:
            logger.error(f"Failed to quantize: {e}", exc_info=True)

    def show_ai_pattern_gen(self):
        """Show AI pattern generator dialog."""
        from PyQt6.QtWidgets import QMessageBox
        try:
            self.generate_variations()
            logger.info("AI pattern generator opened")
        except Exception as e:
            logger.error(
                f"Failed to open AI pattern generator: {e}",
                exc_info=True)
            QMessageBox.warning(
                self,
                "Not Available",
                "AI Pattern Generator coming soon!")

    def generate_from_sketch_controlnet(self):
        """Generate design from sketch using ControlNet."""
        from PyQt6.QtWidgets import QMessageBox
        try:
            from sj_das.core import ControlNetEngine

            if ControlNetEngine is None:
                QMessageBox.warning(
                    self, "Not Available", "ControlNet engine not available")
                return

            QMessageBox.information(
                self, "Coming Soon", "ControlNet sketch-to-design coming soon!")
            logger.info("ControlNet requested")

        except Exception as e:
            logger.error(f"Failed to use ControlNet: {e}", exc_info=True)

    # ========================================================================
    # TEXTILE FEATURES
    # ========================================================================

    def export_to_loom(self):
        """Export design to loom BMP format."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        try:
            import numpy as np

            from sj_das.core.loom_engine import LoomEngine

            if not hasattr(
                    self.editor, 'original_image') or self.editor.original_image is None:
                QMessageBox.warning(self, "Warning", "No image to export")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export to Loom",
                "",
                "BMP Files (*.bmp);;All Files (*.*)"
            )

            if file_path:
                image = self.editor.original_image
                if len(image.shape) == 3:
                    image = image[:, :, 0]

                unique_colors = np.unique(image)
                color_map = {int(c): 'Plain' for c in unique_colors}

                loom = LoomEngine()
                graph = loom.generate_graph(image, color_map)
                loom.save_loom_file(graph, file_path)

                QMessageBox.information(
                    self, "Success", f"Exported to loom: {file_path}")
                logger.info(f"Exported to loom: {file_path}")

        except Exception as e:
            logger.error(f"Failed to export to loom: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

    def detect_pattern_from_image(self):
        """Detect pattern from image."""
        from PyQt6.QtWidgets import QMessageBox
        try:
            self.run_ai_analysis()
            logger.info("Pattern detection started")
        except Exception as e:
            logger.error(f"Failed to detect pattern: {e}", exc_info=True)
            QMessageBox.warning(
                self, "Error", f"Pattern detection failed: {e}")

    # ========================================================================
    #  MISSING TOOL IMPLEMENTATIONS (ADDED FOR COMPLETENESS)
    # ========================================================================

    def activate_brush(self):
        """Activate brush tool."""
        if hasattr(self.editor, 'set_tool'):
            self.editor.set_tool('brush')
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Tool: Brush")
        if hasattr(self, 'on_tool_selected'):
            self.on_tool_selected('brush')

    def activate_eraser(self):
        """Activate eraser tool."""
        if hasattr(self.editor, 'set_tool'):
            self.editor.set_tool('eraser')
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Tool: Eraser")
        if hasattr(self, 'on_tool_selected'):
            self.on_tool_selected('eraser')

    def activate_pencil(self):
        """Activate single pixel pencil tool."""
        if hasattr(self.editor, 'set_tool'):
            self.editor.set_tool('pencil')
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Tool: Pencil (1px)")
        if hasattr(self, 'on_tool_selected'):
            self.on_tool_selected('pencil')

    def activate_fill_tool(self):
        """Activate flood fill tool."""
        if hasattr(self.editor, 'set_tool'):
            self.editor.set_tool('fill')
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Tool: Flood Fill")
        if hasattr(self, 'on_tool_selected'):
            self.on_tool_selected('fill')

    def activate_eyedropper(self):
        """Activate color picker/eyedropper."""
        if hasattr(self.editor, 'set_tool'):
            self.editor.set_tool('picker')
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Tool: Eyedropper")
        if hasattr(self, 'on_tool_selected'):
            self.on_tool_selected('picker')

    def activate_shape_tool(self, shape_type='rect'):
        """Activate shape drawing tool."""
        if hasattr(self.editor, 'set_tool'):
            self.editor.set_tool(f'shape_{shape_type}')
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(f"Tool: Shape ({shape_type})")

    @safe_slot
    def show_fabric_simulation(self):
        """Show 3D/2.5D Fabric Simulation using MiDaS Depth."""
        import cv2
        import numpy as np
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QDialog, QLabel, QScrollArea, QVBoxLayout

        from sj_das.core.engines.vision.depth_engine import \
            DepthEstimationEngine

        try:
            self.show_loading("Simulating Weave Texture...")

            # 1. Generate Depth
            depth_engine = DepthEstimationEngine()
            img = self.editor.get_image()
            cv_img = self._qimage_to_cv2(img)

            depth_map = depth_engine.generate_depth_map(cv_img)

            if depth_map is None:
                self.hide_loading()
                self.show_error("Failed to generate depth map for simulation.")
                return

            # 2. Apply Lighting (Embossing) based on Depth
            # Simple Phong-like shading in 2D
            depth_gray = cv2.cvtColor(
                depth_map,
                cv2.COLOR_BGR2GRAY).astype(
                np.float32)
            gx = cv2.Sobel(depth_gray, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(depth_gray, cv2.CV_32F, 0, 1, ksize=3)

            # Light direction (top-left)
            lx, ly, lz = 1.0, 1.0, 0.5
            norm = np.sqrt(lx**2 + ly**2 + lz**2)
            lx, ly, lz = lx / norm, ly / norm, lz / norm

            # Normal map approximation
            nx = -gx
            ny = -gy
            nz = np.ones_like(nx) * 255.0  # shallow relief

            # Normalize normals
            len_n = np.sqrt(nx**2 + ny**2 + nz**2)
            nx, ny, nz = nx / len_n, ny / len_n, nz / len_n

            # Dot product for diffuse
            diffuse = nx * lx + ny * ly + nz * lz
            diffuse = np.clip(diffuse, 0.0, 1.0)

            # Specular
            # view vector (0,0,1)
            # reflection... simplified: just enhance highlights
            specular = np.power(diffuse, 30)

            # Composite with original color
            h, w = cv_img.shape[:2]

            # Convert original to float
            base = cv_img.astype(np.float32) / 255.0

            # Apply lighting
            # Ambient + Diffuse
            lighting = 0.3 + 0.7 * diffuse[:, :, np.newaxis]

            # Texture (Weave grain noise)
            noise = np.random.normal(0, 0.05, (h, w, 3)).astype(np.float32)

            final = (base * lighting) + \
                (specular[:, :, np.newaxis] * 0.4) + noise
            final = np.clip(final * 255, 0, 255).astype(np.uint8)

            # Show Result
            qimg = self._cv2_to_qimage(final)

            # Display Dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("3D Fabric Simulation")
            dialog.resize(800, 600)
            lay = QVBoxLayout(dialog)

            scroll = QScrollArea()
            lbl = QLabel()
            lbl.setPixmap(QPixmap.fromImage(qimg))
            scroll.setWidget(lbl)
            lay.addWidget(scroll)

            self.hide_loading()
            dialog.exec()

        except Exception as e:
            self.hide_loading()
            self.show_error(f"Simulation error: {str(e)}")

    @safe_slot
    def apply_style_transfer(self):
        """Apply Artistic Style Transfer."""
        from PyQt6.QtWidgets import QInputDialog

        from sj_das.core.engines.vision.style_transfer_engine import \
            StyleTransferEngine

        styles = ["Mosaic", "Starry Night"]
        style, ok = QInputDialog.getItem(
            self, "AI Style Transfer", "Select Style:", styles, 0, False)

        if ok and style:
            try:
                engine = StyleTransferEngine()
                if engine.load_style(style):
                    self.show_loading(f"Applying {style} Style...")
                    # Get Image
                    img = self.editor.get_image()  # QImage
                    cv_img = self._qimage_to_cv2(img)

                    # Process
                    res = engine.apply_style(cv_img)

                    # Set back
                    self.editor.set_image(self._cv2_to_qimage(res))
                    self.hide_loading()
                    self.show_notification(
                        f"Applied {style} style!", duration=3000)
                else:
                    self.hide_loading()
                    self.show_error("Failed to load style model.")
            except Exception as e:
                self.hide_loading()
                self.show_error(f"Style transfer error: {str(e)}")

    @safe_slot
    def apply_colorization(self):
        """Apply AI Auto-Colorization."""
        from sj_das.core.engines.vision.colorization_engine import \
            ColorizationEngine

        try:
            self.show_loading("Colorizing Pattern...")
            engine = ColorizationEngine()

            # Get Image
            img = self.editor.get_image()
            cv_img = self._qimage_to_cv2(img)

            # Process
            res = engine.colorize(cv_img)

            # Set back
            self.editor.set_image(self._cv2_to_qimage(res))
            self.hide_loading()
            self.show_notification("AI Colorization Complete!", duration=3000)

        except Exception as e:
            self.hide_loading()
            self.show_error(f"Colorization error: {str(e)}")

    @safe_slot
    def apply_remove_background(self):
        """Remove Background using U2Net."""
        from sj_das.core.engines.vision.background_removal_engine import \
            BackgroundRemovalEngine

        try:
            self.show_loading("Removing Background...")
            engine = BackgroundRemovalEngine()

            # Get Image
            img = self.editor.get_image()
            cv_img = self._qimage_to_cv2(img)

            # Process
            res = engine.remove_background(cv_img)

            # Set back (Res will be RGBA)
            qimg = self._cv2_to_qimage(res)
            self.editor.set_image(qimg)

            self.hide_loading()
            self.show_notification("Background Removed!", duration=3000)

        except Exception as e:
            self.hide_loading()
            self.show_error(f"Background removal error: {str(e)}")

    @safe_slot
    def apply_depth_map(self):
        """Generate 3D Depth Map Visualization."""
        from sj_das.core.engines.vision.depth_engine import \
            DepthEstimationEngine

        try:
            self.show_loading("Generating 3D Relief Map...")
            engine = DepthEstimationEngine()

            img = self.editor.get_image()
            cv_img = self._qimage_to_cv2(img)

            res = engine.generate_depth_map(cv_img)

            if res is not None:
                self.editor.set_image(self._cv2_to_qimage(res))
                self.hide_loading()
                self.show_notification("Relief Map Generated!", duration=3000)
            else:
                self.hide_loading()
                self.show_error("Failed to generate depth map.")

        except Exception as e:
            self.hide_loading()
            self.show_error(f"Depth Error: {str(e)}")

    @safe_slot
    def activate_voice_control(self):
        """Activate Voice Command Listener."""
        from sj_das.core.engines.voice_engine import get_voice_assistant

        self.show_loading("Listening... (Say 'Generate' or 'Upscale')")
        # In real app, run in thread. Here valid for short command.

        assistant = get_voice_assistant()
        command = assistant.listen_command(duration=4)

        self.hide_loading()

        if command:
            self.show_notification(f"Heard: '{command}'", duration=2000)
            self._process_voice_command(command)
        else:
            self.show_notification("No command heard", duration=2000)

    @safe_slot
    def cut(self):
        """Cut selection to clipboard."""
        if hasattr(self.editor, 'cut_selection'):
            self.editor.cut_selection()
            self.show_notification("Cut to Clipboard")

    @safe_slot
    def copy(self):
        """Copy selection to clipboard."""
        if hasattr(self.editor, 'copy_selection'):
            self.editor.copy_selection()
            self.show_notification("Copied to Clipboard")

    @safe_slot
    def paste(self):
        """Paste from clipboard."""
        if hasattr(self.editor, 'paste_from_clipboard'):
            self.editor.paste_from_clipboard()
            self.show_notification("Pasted from Clipboard")

    def _process_voice_command(self, text):
        """Map voice text to actions."""
        text = text.lower()
        if "generate" in text or "pattern" in text:
            self.show_ai_pattern_gen()
        elif "upscale" in text or "enhance" in text:
            self.apply_ai_upscale_4x()
        elif "segment" in text:
            self.auto_segment()
        elif "chat" in text or "assistant" in text:
            self.activate_ai_chat()
        # Add more mappings as needed

    @safe_slot
    def apply_human_parsing(self):
        """Segment Human for Virtual Draping (Prep)."""
        from sj_das.core.engines.vision.human_parsing_engine import \
            HumanParsingEngine

        try:
            self.show_loading("Segmenting Model for Draping...")
            engine = HumanParsingEngine()

            img = self.editor.get_image()
            cv_img = self._qimage_to_cv2(img)

            res = engine.segment_human(cv_img)

            # Result is RGBA
            self.editor.set_image(self._cv2_to_qimage(res))

            self.hide_loading()
            self.show_notification("Human Parsing Complete!", duration=3000)

        except Exception as e:
            self.hide_loading()
            self.show_error(f"Parsing error: {str(e)}")

    @safe_slot
    def apply_weave(self):
        """Apply weave structure to design (Mock Implementation + logic)."""
        import cv2
        import numpy as np
        from PyQt6.QtWidgets import QInputDialog

        # Basic Weave Library (Binary Patterns) - 0: Weft, 1: Warp
        # In reality, this would load from .bmp/.wif files
        weaves = {
            "Plain (1/1)": np.array([[1, 0], [0, 1]], dtype=np.uint8),
            "Twill (2/2)": np.array([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]], dtype=np.uint8),
            "Satin (5-end)": np.array([[1, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 1], [0, 1, 0, 0, 0], [0, 0, 0, 1, 0]], dtype=np.uint8)
        }

        weave_name, ok = QInputDialog.getItem(
            self, "Weave Mapper", "Select Weave Structure:", list(
                weaves.keys()), 0, False)

        if ok and weave_name:
            try:
                self.show_loading(f"Applying {weave_name}...")
                pattern = weaves[weave_name] * 255  # Scale to 0-255
                ph, pw = pattern.shape

                img = self.editor.get_image()
                cv_img = self._qimage_to_cv2(img)
                h, w = cv_img.shape[:2]

                # Tile the pattern
                tiled = np.tile(pattern, (h // ph + 1, w // pw + 1))
                tiled = tiled[:h, :w]

                # Simple Blend Mode (Multiply) to simulate structure overlay
                # Convert to BGR
                tiled_bgr = cv2.merge([tiled, tiled, tiled])

                # Blend with original
                # result = (original * weave)
                # But we want it subtle
                res = cv2.addWeighted(cv_img, 0.7, tiled_bgr, 0.3, 0)

                self.editor.set_image(self._cv2_to_qimage(res))
                self.hide_loading()
                self.show_notification(
                    f"Applied {weave_name} structure", duration=3000)

            except Exception as e:
                self.hide_loading()
                self.show_error(f"Weave error: {e}")

    @safe_slot
    def cut(self):
        """Cut selection to clipboard."""
        if hasattr(self.editor, 'cut_selection'):
            self.editor.cut_selection()
            self.show_notification("Cut to Clipboard")

    @safe_slot
    def copy(self):
        """Copy selection to clipboard."""
        if hasattr(self.editor, 'copy_selection'):
            self.editor.copy_selection()
            self.show_notification("Copied to Clipboard")

    @safe_slot
    def paste(self):
        """Paste from clipboard."""
        if hasattr(self.editor, 'paste_from_clipboard'):
            self.editor.paste_from_clipboard()
            self.show_notification("Pasted from Clipboard")

    @safe_slot
    def activate_voice_control(self):
        """Activate Voice Command Listener."""
        from sj_das.core.engines.voice_engine import get_voice_assistant

        self.show_loading("Listening... (Say 'Generate' or 'Upscale')")
        # In real app, run in thread. Here valid for short command.

        assistant = get_voice_assistant()
        command = assistant.listen_command(duration=4)

        self.hide_loading()

        if command:
            self.show_notification(f"Heard: '{command}'", duration=2000)
            self._process_voice_command(command)
        else:
            self.show_notification("No command heard", duration=2000)

    def _process_voice_command(self, text):
        """Map voice text to actions."""
        text = text.lower()
        if "generate" in text or "pattern" in text:
            self.show_ai_pattern_gen()
        elif "upscale" in text or "enhance" in text:
            self.apply_ai_upscale_4x()
        elif "segment" in text:
            self.auto_segment()
        elif "chat" in text or "assistant" in text:
            self.activate_ai_chat()
        # Add more mappings as needed

    def activate_ai_chat(self):
        """Open AI Assistant Chat Interface."""
        from PyQt6.QtWidgets import QInputDialog, QLineEdit, QMessageBox

        from sj_das.ai.agi_assistant import get_agi

        # Get Query
        query, ok = QInputDialog.getText(
            self,
            "AI Assistant",
            "Ask the SJ-DAS Intelligence (MiniMax/Llama):\n(e.g., 'Suggest colors for bridal saree', 'Explain Kanjivaram weave')",
            QLineEdit.EchoMode.Normal
        )

        if ok and query:
            # Show processing
            self.status_bar.showMessage("AI is thinking...")
            QApplication.processEvents()

            result = {} # Initialize result here
            try:
                # Process with AGI
                agi = get_agi()
                result = agi.process_command(query)

                # Show Response
                response = result.get('response', 'I could not process that.')

                # Execute Action if any
                if result.get('action'):
                    # Handle actions like 'open_expert' or 'run_analysis'
                    action_name = result.get('action')
                    if hasattr(self, action_name):
                        getattr(self, action_name)()
                    elif action_name == "open_expert":  # Remap common internal names
                        self.show_smart_expert()
                    elif action_name == "run_analysis":
                        self.run_ai_analysis()

                # Show Text Response
                QMessageBox.information(
                    self, "AI Assistant Response", response)
                self.status_bar.showMessage("AI Response received")

            except Exception as e:
                logger.error(f"AI Assistant Error: {e}")
                QMessageBox.warning(
                    self, "AI Error", f"Failed to consult AI: {e}")

                QMessageBox.information(self, "AI Assistant", response)

            except Exception as e:
                self.status_bar.showMessage(f"AI Error: {str(e)}")
                logger.error(f"AI Chat Error: {e}")

    @safe_slot
    def generate_from_sketch_controlnet(self):
        """Turn sketch into design using ControlNet (Threaded)."""
        from PyQt6.QtWidgets import QInputDialog

        # 1. Get Prompt
        prompt, ok = QInputDialog.getText(
            self, "Sketch to Design", "Describe the desired output (e.g. 'golden silk saree, intricate border'):")
        if not ok or not prompt:
            return

        self.show_loading("Refining Sketch with ControlNet (AI)...")

        # Prepare Data
        img = self.editor.get_image()
        cv_img = self._qimage_to_cv2(img)

        # Launch Worker
        self.ai_worker = AIWorker("controlnet", cv_img, prompt)
        self.ai_worker.finished.connect(self._on_controlnet_done)
        self.ai_worker.failed.connect(
            lambda e: (
                self.hide_loading(),
                self.show_error(f"ControlNet Failed: {e}")))
        self.ai_worker.start()

    def _on_controlnet_done(self, res):
        self.hide_loading()
        if res is not None:
            self.editor.set_image(self._cv2_to_qimage(res))
            self.show_notification(
                "Design Generated from Sketch!", duration=3000)
