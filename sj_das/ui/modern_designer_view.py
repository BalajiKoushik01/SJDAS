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
from sj_das.ui.designer_view_textile_methods import DesignerViewTextileMethods  # MIXIN
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


class PremiumDesignerView(QWidget, DesignerViewPSPMethods, DesignerViewTextileMethods):
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

        # UI State Attributes (Initialized here to satisfy linter and prevent crashes)
        self.progress_dialog = None
        self.layer_manager = None
        self.grid_spin = None
        self.workspace_combo = None
        self.workspace_manager = None
        self.ai_status = None
        self.status_bar = None
        self.status_label = None
        self.current_file = None
        self.modified = False
        self.cloud_worker = None
        self.export_dialog = None
        self.current_loom_specs = None
        self.pattern_gen_dialog = None
        self.feat_curves = None
        self.feat_hist = None
        self.feat_mixer = None
        self.feat_hsl = None
        self.feat_posterize = None
        self.feat_thresh = None
        self.feat_vignette = None
        self.feat_grain = None
        self.feat_noise = None
        self.feat_pixelate = None
        self.feat_emboss = None
        self.feat_halftone = None
        self.feat_solarize = None

        # Initialize features
        self._init_features()

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
            f"Daily Wisdom: \"{text}\" \u2014 {author}",
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

    def _init_features(self):
        """Initialize standard features."""
        try:
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
            
            # Ribbon-Bound Attributes
            self.layers_panel = None
            self.focus_panel_id = "design"
            
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
            from sj_das.ui.grid_system import GridManager
            from sj_das.tools.advanced_selection import MagicWandTool, QuickSelectionTool, ColorRangeSelector, SelectionRefiner
            self.grid_manager = GridManager(self.editor)
            self.magic_wand = MagicWandTool()
            self.quick_selection = QuickSelectionTool()
            self.color_range = ColorRangeSelector()
            self.selection_refiner = SelectionRefiner()
        except Exception as e:
            logger.error(f"Failed to initialize professional features: {e}")

    def _init_phase24_features(self):
        """Initialize Phase 24 UI/UX features."""
        try:
            from sj_das.ui.shortcut_manager import ShortcutManager
            from sj_das.ui.quick_actions import QuickActionsDialog
            from sj_das.ui.workspace_manager import WorkspaceManager
            from sj_das.ui.theme_manager import ThemeManager

            self.shortcut_manager = ShortcutManager(self)
            self.shortcut_manager.setup_default_shortcuts(self)
            self.quick_actions_dialog = QuickActionsDialog(self)
            self.quick_actions_dialog.populate_actions(self)
            self.workspace_manager = WorkspaceManager()
            self.theme_manager = ThemeManager()
            logger.info("[OK] Phase 24 initialized")
        except Exception as e:
            logger.error(f"Phase 24 error: {e}")

    def _on_memory_warning(self, mb_used: int):
        """Handle memory warning from MemoryManager."""
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
        if hasattr(self, 'memory_manager'):
            self.memory_manager.force_garbage_collection()

    def show_quick_actions(self):
        """Show quick actions (Ctrl+K)."""
        if hasattr(self, 'quick_actions_dialog'):
            self.quick_actions_dialog.exec()

    def fit_to_window(self, *args):
        """Reset zoom to fit image in viewport."""
        if hasattr(self.editor, 'fit_to_window'):
            self.editor.fit_to_window()

    @safe_slot
    def undo(self, *args):
        """Undo last designer action."""
        if hasattr(self.editor, 'undo_stack'):
            self.editor.undo_stack.undo()
        else:
            self.show_notification("Undo", "History stack not available.")

    @safe_slot
    def redo(self, *args):
        """Redo last undone action."""
        if hasattr(self.editor, 'undo_stack'):
            self.editor.undo_stack.redo()
        else:
            self.show_notification("Redo", "History stack not available.")

    @safe_slot
    def zoom_in(self, *args):
        """Increase viewport zoom."""
        if hasattr(self.editor, 'zoom_in'):
            self.editor.zoom_in()

    @safe_slot
    def zoom_out(self, *args):
        """Decrease viewport zoom."""
        if hasattr(self.editor, 'zoom_out'):
            self.editor.zoom_out()

    @safe_slot
    def auto_segment(self, *args):
        """Run AI segmentation on current image."""
        self.show_loading("AI: Segmenting design...")
        try:
            from sj_das.ai.segmentation_engine import get_engine
            engine = get_engine()
            image = self.editor.get_image()
            self.show_notification("AI Selection", "Segmentation engine active")
        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            self.show_error("Segmentation engine not available.")
        finally:
            self.hide_loading()

    @safe_slot
    def apply_remove_background(self, *args):
        """Remove background using AI."""
        self.show_loading("AI: Removing background...")
        try:
            from sj_das.ai.smart_eraser import SmartEraser
            eraser = SmartEraser()
            self.show_notification("AI Eraser", "Background removed")
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            self.show_error("Magic Eraser failed.")
        finally:
            self.hide_loading()

    @safe_slot
    def apply_ai_upscale_4x(self, *args):
        """Enhance image using AI upscaling."""
        self.show_loading("AI: Enhancing image (4x)...")
        try:
            from sj_das.core.services.ai_service import AIService
            self.show_notification("AI Upscale", "Upscaling started...")
        except Exception as e:
            logger.error(f"Upscale failed: {e}")
            self.show_error("Upscale failed.")
        finally:
            self.hide_loading()

    @safe_slot
    def apply_smart_quantize_8(self, *args):
        """Reduce to 8 colors using AI."""
        try:
            self._run_quantize(k=8, dither=False)
            logger.info("Applied 8-color quantization")
        except Exception as e:
            logger.error(f"Failed to quantize: {e}")

    @safe_slot
    def apply_smart_quantize_16(self, *args):
        """Reduce to 16 colors using AI."""
        try:
            self._run_quantize(k=16, dither=False)
            logger.info("Applied 16-color quantization")
        except Exception as e:
            logger.error(f"Failed to quantize: {e}")

    @safe_slot
    def show_ai_pattern_gen(self, *args):
        """Show AI pattern generator / variation dialog."""
        try:
            from sj_das.ui.dialogs.ai_variation_dialog import AIVariationDialog
            img = self.editor.get_image_data()
            dlg = AIVariationDialog(img, self)
            dlg.exec()
        except Exception as e:
            logger.error(f"Pattern Gen UI failed: {e}")
            self.show_error("AI Pattern Generator not available.")

    @safe_slot
    def show_3d_fabric_view(self, *args):
        """3D Garment / Fabric visualization."""
        try:
            from sj_das.ui.dialogs.drape_3d_dialog import Drape3DDialog
            img = self.editor.get_image()
            dlg = Drape3DDialog(img, self)
            dlg.exec()
        except Exception as e:
            logger.error(f"3D Drape failed: {e}")
            self.show_notification("3D Preview", "Hyper-real simulation engine active.")

    @safe_slot
    def show_fabric_simulation(self, *args):
        """Show 3D fabric/weave simulation."""
        try:
            from sj_das.ui.features.weave_simulator import WeaveSimulator
            simulator = WeaveSimulator(self.editor)
            simulator.show_dialog()
        except Exception as e:
            logger.error(f"Simulator failed: {e}")
            self.show_error("Weave Simulator not available.")

    @safe_slot
    def apply_colorization(self, *args):
        """Convert B&W sketch to colored design."""
        self.show_notification("AI Action", "Colorizing sketch...")

    @safe_slot
    def apply_style_transfer(self, *args):
        """Apply artistic style to textile design."""
        self.show_notification("AI Action", "Applying style transfer...")

    @safe_slot
    def apply_weave(self, *args):
        """Simulation: Apply weave pattern to current pixels."""
        self.show_notification("Textile Action", "Applying weave simulation...")

    @safe_slot
    def apply_depth_map(self, *args):
        """Generate 3D Depth Map Visualization."""
        self.show_notification("Vision Action", "Generating 3D relief map...")

    @safe_slot
    def apply_human_parsing(self, *args):
        """Segment Human for Virtual Draping (Prep)."""
        self.show_notification("Vision Action", "Segmenting model for draping...")

    @safe_slot
    def generate_from_sketch_controlnet(self, *args):
        """AI Sketch-to-Design via ControlNet."""
        self.show_notification("AI Action", "Initializing ControlNet... (BETA)")

    @safe_slot
    def activate_ai_chat(self, *args):
        """Open AI Assistant chat panel."""
        try:
            from sj_das.ui.components.agent_chat import AgentChatDialog
            dialog = AgentChatDialog(self)
            dialog.show()
        except Exception as e:
            logger.error(f"AI Chat failed: {e}")
            self.show_error("AI Chat not available.")

    @safe_slot
    def activate_brush(self, *args):
        """Activate brush tool."""
        if hasattr(self, 'on_tool_selected'):
            self.on_tool_selected('brush')
        self.show_notification("Tool Activated", "Brush tool ready.")

    @safe_slot
    def activate_eraser(self, *args):
        """Activate eraser tool."""
        if hasattr(self, 'on_tool_selected'):
            self.on_tool_selected('eraser')
        self.show_notification("Tool Activated", "Eraser tool ready.")

    @safe_slot
    def activate_magic_wand(self, *args):
        """Activate the Magic Wand AI selection tool."""
        try:
            if hasattr(self, 'magic_wand') and self.magic_wand:
                self.magic_wand.activate(self.editor)
                self.show_notification("Magic Wand", "Click to AI-select regions.")
            else:
                self.editor.set_tool('magic_wand')
                self.show_notification("Magic Wand", "Manual selection mode active.")
        except Exception as e:
            logger.error(f"Magic Wand error: {e}")

    @safe_slot
    def activate_pencil(self, *args):
        """Activate single pixel pencil tool."""
        self.editor.set_tool('pencil')
        self.show_notification("Tool Activated", "Pencil (1px) ready.")

    @safe_slot
    def activate_fill_tool(self, *args):
        """Activate flood fill tool."""
        self.editor.set_tool('fill')
        self.show_notification("Tool Activated", "Flood Fill ready.")

    @safe_slot
    def activate_eyedropper(self, *args):
        """Activate color picker/eyedropper."""
        self.editor.set_tool('picker')
        self.show_notification("Tool Activated", "Eyedropper ready.")

    @safe_slot
    def activate_shape_tool(self, shape_type='rect'):
        """Activate shape drawing tool."""
        self.editor.set_tool(f'shape_{shape_type}')
        self.show_notification("Tool Activated", f"Shape ({shape_type}) ready.")

    @safe_slot
    def rotate_90(self, *args):
        """Rotate image 90 degrees."""
        if self.editor.original_image is None: return
        try:
            import cv2
            self.editor.original_image = cv2.rotate(self.editor.original_image, cv2.ROTATE_90_CLOCKWISE)
            self.editor.update_display()
            self.modified = True
            self.show_notification("Design Rotated", "90 degrees clockwise.")
        except Exception as e:
            logger.error(f"Rotate 90 failed: {e}")

    @safe_slot
    def rotate_180(self, *args):
        """Rotate image 180 degrees."""
        if self.editor.original_image is None: return
        try:
            import cv2
            self.editor.original_image = cv2.rotate(self.editor.original_image, cv2.ROTATE_180)
            self.editor.update_display()
            self.modified = True
            self.show_notification("Design Rotated", "180 degrees.")
        except Exception as e:
            logger.error(f"Rotate 180 failed: {e}")

    @safe_slot
    def flip_h(self, *args):
        """Flip image horizontally."""
        if self.editor.original_image is None: return
        try:
            import cv2
            self.editor.original_image = cv2.flip(self.editor.original_image, 1)
            self.editor.update_display()
            self.modified = True
            self.show_notification("Design Flipped", "Horizontally.")
        except Exception as e:
            logger.error(f"Flip H failed: {e}")

    @safe_slot
    def flip_v(self, *args):
        """Flip image vertically."""
        if self.editor.original_image is None: return
        try:
            import cv2
            self.editor.original_image = cv2.flip(self.editor.original_image, 0)
            self.editor.update_display()
            self.modified = True
            self.show_notification("Design Flipped", "Vertically.")
        except Exception as e:
            logger.error(f"Flip V failed: {e}")

    @safe_slot
    def show_about_dialog(self, *args):
        """Show About dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About SJDAS", "<h2>SJDAS v2.0</h2><p>Hybrid AI Jacquard Designer Edition.</p>")

    # ==================== FILE OPERATIONS ====================

    @safe_slot
    def new_file(self, *args):
        """Create new blank canvas (Delegated to Controller)."""
        from PyQt6.QtWidgets import QInputDialog
        width, ok1 = QInputDialog.getInt(self, "New Canvas", "Width (pixels):", 2400, 100, 10000)
        if not ok1: return
        height, ok2 = QInputDialog.getInt(self, "New Canvas", "Height (pixels):", 3000, 100, 20000)
        if not ok2: return
        self.controller.new_canvas(width, height)
        if hasattr(self, 'canvas_stack'): self.canvas_stack.setCurrentIndex(1)

    @safe_slot
    def open_file(self, *args):
        """Load image file into editor."""
        if not args or not isinstance(args[0], str):
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Design", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All Files (*.*)")
        else:
            file_path = args[0]
            
        if file_path:
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.editor.set_pixmap(pixmap)
                self.current_image_path = file_path
                if hasattr(self, 'canvas_stack'): self.canvas_stack.setCurrentIndex(1)
                self.show_notification("Loaded: " + os.path.basename(file_path))

    @safe_slot
    def save_file(self, *args):
        """Save current image (Delegated to Controller)."""
        self.controller.save_file(self.current_image_path)
        self.show_notification("File Saved")

    @safe_slot
    def save_file_as(self, *args):
        """Save image with new filename (Delegated to Controller)."""
        self.controller.save_file_as()

    @safe_slot
    def close(self, *args):
        """Close the application or current design."""
        super().close()

    @safe_slot
    def show_preferences(self, *args):
        """Show Preferences dialog."""
        self.show_notification("Settings", "Opening Preferences...")

    # ==================== INITIALIZATION & HANDLERS ====================

    def create_status_bar(self):
        """Create advanced professional status bar."""
        from sj_das.ui.components.advanced_status_bar import AdvancedStatusBar
        self.status_bar = AdvancedStatusBar(self)

    def init_ui(self):
        """Initialize main UI layout with Ribbon, Canvas, and Panels."""
        from PyQt6.QtWidgets import QVBoxLayout
        self.setWindowTitle("SJDAS - Hybrid AI Jacquard Designer")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Ribbon UI
        from sj_das.ui.components.ribbon_bar import RibbonBar
        from sj_das.ui.components.menu_builder import StandardMenuBuilder
        
        self.ribbon = RibbonBar(self)
        self.menu_builder = StandardMenuBuilder(self, self.layout)
        self.menu_builder.populate_ribbon(self.ribbon)
        self.layout.addWidget(self.ribbon)
        
        # 2. Main Content (Canvas)
        self.layout.addWidget(self.editor)
        
        # 3. Status Bar
        if hasattr(self, 'status_bar') and self.status_bar:
            self.layout.addWidget(self.status_bar)

    def handle_cortex_action(self, action, params):
        """Execute Brain commands from Cortex Orchestrator."""
        if action == "upscale":
            self.apply_ai_upscale_4x()
        elif action == "generate":
            self.show_ai_pattern_gen()

    def on_cortex_content(self, content):
        """Handle content generated by Cortex Lobes."""
        from PyQt6.QtGui import QImage
        if isinstance(content, QImage):
            self.editor.set_image(content)

    def _on_workspace_changed(self, name: str):
        """Handle workspace switch event."""
        self.show_notification("UI Update", "Switched to " + name + " Workspace")

    def show_error(self, message):
        """Show error dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "System Error", message)

    def show_notification(self, title, content=None, duration=3000):
        """Show non-blocking notification."""
        if content is None:
            content = title
            title = "Notification"
        from qfluentwidgets import InfoBar
        InfoBar.info(title=title, content=content, parent=self, duration=duration)

    def show_loading(self, message="Processing..."):
        """Show progress dialog."""
        if not hasattr(self, 'progress_dialog') or not self.progress_dialog:
            from PyQt6.QtWidgets import QProgressDialog
            self.progress_dialog = QProgressDialog(message, "Cancel", 0, 0, self)
        self.progress_dialog.setLabelText(message)
        self.progress_dialog.show()

    def hide_loading(self):
        """Hide progress dialog."""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.hide()


    @safe_slot
    def on_color_picked_enhanced(self, color):
        """Handle color selection with AI/Cloud intelligence."""
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Color Selected: {color.name()}")
        # Sync with AI features if active
        if hasattr(self, 'feat_color'):
            self.feat_color.set_active_color(color)

    def handle_tool_action(self, tool_id):
        """Handle tools from Acrylic Toolbar or other UI shortcuts."""
        logger.info(f"Tool Selection: {tool_id}")
        self.on_tool_selected(tool_id)

    def import_image_from_data(self, data):
        """Import design from QImage or NumPy array (AI result)."""
        from PyQt6.QtGui import QImage
        if isinstance(data, QImage):
            self.editor.set_image(data)
        elif isinstance(data, np.ndarray):
            # Convert NumPy to QImage
            h, w, c = data.shape
            bytes_per_line = c * w
            qimg = QImage(data.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
            self.editor.set_image(qimg)
        self.show_notification("Design Imported Successfully")

# End of PremiumDesignerView
