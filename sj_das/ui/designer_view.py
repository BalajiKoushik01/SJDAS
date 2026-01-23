import os

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow  # NEW
from PyQt6.QtWidgets import (QApplication, QCheckBox, QColorDialog, QComboBox,
                             QDialog, QDialogButtonBox, QFileDialog,
                             QFormLayout, QGroupBox, QHBoxLayout, QInputDialog,
                             QLabel, QLineEdit, QMessageBox, QProgressBar,
                             QPushButton, QSpinBox, QSplitter, QTabWidget,
                             QVBoxLayout, QWidget)

# AI Integration Imports
from sj_das.ai.model_loader import get_ai_model
from sj_das.ai.proactive_assistant import get_proactive_assistant
from sj_das.core.pattern_detection import PatternDetectionEngine
from sj_das.core.segmentation import SegmentationEngine
from sj_das.resources.icons import DASIcons
from sj_das.ui.components.toast import ToastNotification
from sj_das.ui.dialogs.card_sequence_dialog import CardSequenceDialog
from sj_das.ui.dialogs.loom_export_dialog import LoomExportDialog
from sj_das.ui.dialogs.loom_import_dialog import LoomImportDialog
# from sj_das.core.generator import TextilePatternGenerator # Deprecated
from sj_das.ui.editor_widget import PixelEditorWidget


class CanvasSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loom Configuration")
        self.setModal(True)
        self.setMinimumWidth(300)

        layout = QFormLayout(self)

        # Width (Hooks) - Support Math
        self.edit_width = QLineEdit("480")
        self.edit_width.setPlaceholderText("e.g. 480 or 240*2")
        self.edit_width.setToolTip("Enter hooks. Math allowed: 240*2, 480+480")

        # Height (Picks) - Support Math
        self.edit_height = QLineEdit("480")
        self.edit_height.setPlaceholderText("e.g. 480 or 480*3")

        # Reed (For Export Metadata)
        self.spin_reed = QSpinBox()
        self.spin_reed.setRange(1, 500)
        self.spin_reed.setValue(100)
        self.spin_reed.setSuffix(" Reed")

        # Kali (Repeats)
        self.spin_kali = QSpinBox()
        self.spin_kali.setRange(1, 20)
        self.spin_kali.setValue(1)  # Default 1 (Full width)
        self.spin_kali.setPrefix("Kali: ")

        # Locking (Overlap)
        self.spin_locking = QSpinBox()
        self.spin_locking.setRange(0, 200)
        self.spin_locking.setValue(0)
        self.spin_locking.setSuffix(" px")
        self.spin_locking.setPrefix("Locking: ")

        layout.addRow("Width (Hooks):", self.edit_width)
        layout.addRow("Height (Picks):", self.edit_height)
        layout.addRow("Reed Count:", self.spin_reed)
        layout.addRow("Kali (Repeats):", self.spin_kali)
        layout.addRow("Locking (Overlap):", self.spin_locking)

        # Helper Label
        layout.addRow(QLabel(
            "<small style='color:gray'><b>Smart Setup:</b> Enter loom specifics to auto-configure export.</small>"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.final_w = 480
        self.final_h = 480

    def eval_math(self, text):
        try:
            # Safe eval for simple math
            allowed = set("0123456789+*-/ ")
            if not set(text).issubset(allowed):
                return None
            return int(eval(text))
        except BaseException:
            return None

    def validate_and_accept(self):
        w = self.eval_math(self.edit_width.text())
        h = self.eval_math(self.edit_height.text())

        if w is None or w <= 0:
            QMessageBox.warning(
                self,
                "Invalid Width",
                "Please enter a valid number or math expression for Width.")
            return
        if h is None or h <= 0:
            QMessageBox.warning(
                self,
                "Invalid Height",
                "Please enter a valid number or math expression for Height.")
            return

        self.final_w = w
        self.final_h = h
        self.accept()

    def get_dimensions(self):
        return (
            self.final_w,
            self.final_h,
            self.spin_reed.value(),
            self.spin_kali.value(),
            self.spin_locking.value()
        )


class DesignerView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Widget)  # Embeddable

        self.segmentation_engine = SegmentationEngine()
        # self.pattern_generator = TextilePatternGenerator() # REMOVED: Using
        # GenerativeDesignEngine instead
        self.current_image_path = None
        self.current_mask = None
        self.reed_count = 100
        self.kali_count = 1
        self.locking_px = 0

        # AI Integration - Load model and assistant
        self.ai_model = get_ai_model()
        self.ai_assistant = get_proactive_assistant()
        self.ai_last_analysis = None

        self.init_ui()
        self.toast = ToastNotification(self)  # NEW

        # --- SMART AI INTEGRATION ---
        # Initialize Advanced Panels

        self.layers_panel = None

        # OLD UI ELEMENTS REMOVED - Using modern clean UI instead
        # The new UI uses:
        # - Clean menu bar (File/Edit/View/Tools/Help)
        # - Modern tool options bar
        # - Premium 6-tool left strip
        # - Clean right sidebar with tabs

        # PHASE 2: Setup Keyboard Shortcuts
        from sj_das.ui.shortcut_manager import ShortcutManager
        self.shortcut_manager = ShortcutManager(self)

    def setup_shortcuts_after_init(self):
        """Setup shortcuts after editor is fully initialized."""
        if hasattr(self, 'shortcut_manager') and hasattr(self, 'editor'):
            self.shortcut_manager.setup_all_shortcuts(self.editor, self)

    def resizeEvent(self, event):
        # Overlay removed - using clean modern UI
        super().resizeEvent(event)

    def on_color_picked(self, color):
        """Handle color picking from the editor."""
        if hasattr(self, 'editor'):
            self.editor.brush_color = color

    def _qimage_to_cv2(self, qimg):
        # Helper to convert back
        qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
        w, h = qimg.width(), qimg.height()
        ptr = qimg.bits()
        ptr.setsize(h * w * 3)
        return np.array(ptr).reshape(h, w, 3)

    def init_ui(self):
        # 1. Initialize Editor FIRST (dependencies)
        self.editor = PixelEditorWidget()
        self.editor.color_picked.connect(self.on_color_picked)

        # 2. Create Menu Bar FIRST (before central widget)
        self.create_menu_bar()

        # 3. Main Container
        # QMainWindow needs a Central Widget
        self.central_container = QWidget()
        self.setCentralWidget(self.central_container)

        main_layout = QVBoxLayout(self.central_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 4. Modern Tool Options Bar (sleek, context-sensitive)
        from sj_das.ui.components.modern_tool_options import \
            ModernToolOptionsBar
        self.tool_options_bar = ModernToolOptionsBar(self.editor, self)
        main_layout.addWidget(self.tool_options_bar)

        # 5. Canvas Area with Rulers (Professional Layout)
        from sj_das.ui.components.ruler import Ruler

        # Create canvas container with rulers
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)

        # Top ruler (horizontal)
        ruler_top_container = QWidget()
        ruler_top_layout = QHBoxLayout(ruler_top_container)
        ruler_top_layout.setContentsMargins(0, 0, 0, 0)
        ruler_top_layout.setSpacing(0)

        # Corner spacer (25x25)
        corner_spacer = QWidget()
        corner_spacer.setFixedSize(25, 25)
        corner_spacer.setStyleSheet("background-color: #252233;")
        ruler_top_layout.addWidget(corner_spacer)

        # Horizontal ruler
        self.ruler_horizontal = Ruler(Ruler.HORIZONTAL)
        ruler_top_layout.addWidget(self.ruler_horizontal)

        canvas_layout.addWidget(ruler_top_container)

        # Middle row: Vertical ruler + Canvas
        middle_container = QWidget()
        middle_layout = QHBoxLayout(middle_container)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)

        # Vertical ruler
        self.ruler_vertical = Ruler(Ruler.VERTICAL)
        middle_layout.addWidget(self.ruler_vertical)

        # Canvas
        middle_layout.addWidget(self.editor)

        canvas_layout.addWidget(middle_container)

        # 6. Workspace Area (Splitter: Canvas | Panels)
        self.workspace_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.workspace_splitter.setObjectName("workspace_splitter")
        self.workspace_splitter.setHandleWidth(
            2)  # Slightly wider for better grip

        # Modern Clean Layout (Figma-style)
        # Left: Minimal 72px Tool Strip
        from sj_das.ui.components.modern_tool_strip import ModernToolStrip
        self.modern_tool_strip = ModernToolStrip(self)
        self.modern_tool_strip.tool_selected.connect(self.on_tool_selected)
        self.modern_tool_strip.setFixedWidth(72)  # Ensure fixed width
        self.modern_tool_strip.setVisible(True)  # Explicitly make visible
        print("=" * 60)
        print("LEFT TOOLBAR CREATED - Should be 72px wide!")
        print("=" * 60)

        # Create horizontal splitter: Tool Strip | Canvas | Right Sidebar
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(1)  # Thin handle

        # Add tool strip
        content_splitter.addWidget(self.modern_tool_strip)

        # Center: Canvas with Rulers (Maximum space)
        self.workspace_splitter.addWidget(canvas_container)
        content_splitter.addWidget(self.workspace_splitter)

        # Add to main layout
        main_layout.addWidget(content_splitter)

        # Right Sidebar (Modern, Clean)
        self.create_right_panel()
        content_splitter.addWidget(self.right_panel)

        # Set splitter sizes: Tool Strip (60px) | Canvas (flex) | Right Panel
        # (320px)
        content_splitter.setStretchFactor(0, 0)  # Tool strip fixed
        content_splitter.setStretchFactor(1, 1)  # Canvas flexible
        content_splitter.setStretchFactor(2, 0)  # Right panel fixed

        # AI Assistant (no arguments)
        from sj_das.ai.proactive_assistant import ProactiveTextileAssistant
        self.ai_assistant = ProactiveTextileAssistant()

        # Status Bar (Modern, Enhanced with more info)
        from sj_das.ui.components.zoom_control import ZoomControl

        # Create zoom control
        self.zoom_control = ZoomControl(self)
        self.zoom_control.zoom_changed.connect(self.on_zoom_changed)

        # Add zoom control to status bar (right side)
        self.statusBar().addPermanentWidget(self.zoom_control)

        # Status bar styling
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #252233;
                border-top: 1px solid #3730A3;
                color: #94A3B8;
                font-size: 11px;
                padding: 4px 8px;
                min-height: 32px;
            }
        """)
        self.update_status_bar("Ready - Canvas: 1000x1000px | Tool: Select")

        # PHASE 2: Initialize keyboard shortcuts after UI is ready
        self.setup_shortcuts_after_init()

    def on_zoom_changed(self, zoom_level):
        """Handle zoom level change"""
        if hasattr(self, 'editor'):
            # Apply zoom to editor
            self.editor.setTransform(
                self.editor.transform().scale(
                    zoom_level, zoom_level))
            self.update_status_bar(f"Zoom: {int(zoom_level * 100)}%")

        # Update rulers
        if hasattr(self, 'ruler_horizontal'):
            self.ruler_horizontal.set_zoom(zoom_level)
        if hasattr(self, 'ruler_vertical'):
            self.ruler_vertical.set_zoom(zoom_level)

    def update_status_bar(self, message):
        """Update status bar with message"""
        self.statusBar().showMessage(message)

    def handle_ai_suggestion(self, action: str, data: dict):
        """Handle AI suggestion actions from AI panel."""
        if action == 'refresh_analysis':
            self.run_ai_analysis()
        elif action == 'adjust_border_width':
            suggested = data.get('suggested_width', 7)
            QMessageBox.information(
                self,
                "Border Adjustment",
                f"Suggested border width: {suggested}cm\n\nUse the selection and resize tools to adjust your border to this width."
            )
        elif action == 'extend_pallu':
            suggested = data.get('suggested_length', 100)
            QMessageBox.information(
                self,
                "Pallu Extension",
                f"Suggested pallu length: {suggested}cm\n\nConsider extending your pallu design to comply with traditional proportions."
            )
        elif action == 'apply_color_scheme':
            colors = data.get('colors', [])
            if colors:
                color_text = "\n".join(
                    [f"• {c1} with {c2}" for c1, c2 in colors[:5]])
                QMessageBox.information(
                    self,
                    "Traditional Color Combinations",
                    f"Suggested color pairs:\n{color_text}\n\nThese combinations follow cultural traditions and are proven to work well."
                )
        else:
            QMessageBox.warning(
                self,
                "AI Suggestion",
                f"Unknown AI action: {action}")

    def train_custom_model(self):
        """Opens dialog to train custom AI model."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Dataset for Training")
        if not dir_path:
            return

        try:
            from PyQt6.QtWidgets import QProgressDialog

            from sj_das.core.gan_trainer import PatternGANTrainer

            # Progress Dialog
            progress = QProgressDialog(
                "Training Custom Model...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            def update_progress(val, msg):
                progress.setValue(val)
                progress.setLabelText(msg)
                QApplication.processEvents()

            trainer = PatternGANTrainer(dir_path)
            # Run training (synchronous for now, ideally threaded)
            model_path = trainer.train(
                epochs=20, progress_callback=update_progress)

            progress.setValue(100)
            QMessageBox.information(
                self,
                "Training Complete",
                f"Model saved to:\n{model_path}")

        except Exception as e:
            QMessageBox.critical(self, "Training Error", str(e))

    def load_generated_design(self, image: np.ndarray):
        """Load a generated design from the generation panel into the editor."""
        try:
            # Assume image is a NumPy BGR array; set directly
            self.editor.set_image(image)
            print(
                f"✅ Loaded generated design: {image.shape[1]}x{image.shape[0]}")
            # Optionally run AI analysis on the new design
            self.auto_analyze_on_load()
        except Exception as e:
            print(f"Error loading generated design: {e}")
            import traceback
            traceback.print_exc()

    def run_ai_analysis(self):
        """Run AI analysis on current image."""
        if not hasattr(
                self, 'editor') or self.editor.original_image is None or self.editor.original_image.isNull():
            return

        try:
            import cv2
            import numpy as np

            # Get QImage directly
            image = self.editor.original_image
            width, height = image.width(), image.height()

            # Convert to numpy
            ptr = image.constBits()
            ptr.setsize(height * width * 4)
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

            # Convert RGBA to RGB
            rgb_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

            # Run AI prediction
            if self.ai_model:
                prediction = self.ai_model.predict(rgb_image)

                if prediction:
                    # Calculate design metrics
                    design_metrics = {
                        'width_px': width,
                        'height_px': height,
                        'has_mask': self.current_mask is not None
                    }

                    # Generate suggestions
                    if self.ai_assistant:
                        suggestions = self.ai_assistant.analyze_design(
                            prediction, design_metrics)

                        # Update UI
                        if hasattr(self, 'ai_insights_panel'):
                            self.ai_insights_panel.update_insights(
                                prediction, suggestions)

                    self.ai_last_analysis = prediction
                    print("✅ AI Analysis Complete")
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            import traceback
            traceback.print_exc()

    def auto_analyze_on_load(self):
        """Automatically run AI analysis when image is loaded."""
        # Schedule analysis after a short delay to let UI update
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.run_ai_analysis)

    def import_photo_weave(self):
        """Imports a photo and runs Photo-Weave Dithering."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            try:
                from sj_das.core.photo_weave import PhotoWeaveEngine
                engine = PhotoWeaveEngine()

                # 480 Hooks, 16 Colors (Maximum for complex photo)
                res = engine.process_photo_for_loom(path, 480, 16)

                # Convert RGB-Numpy to BGR-CV2
                res_bgr = cv2.cvtColor(res, cv2.COLOR_RGB2BGR)

                self.editor.set_image(res_bgr)
                QMessageBox.information(
                    self, "Photo Weave", "Photo Dithered & Map Ready!")
            except ImportError as e:
                QMessageBox.critical(
                    self,
                    "Missing Dependency",
                    f"Photo Engine requires PIL: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def set_tool(self, tool_id):
        """Update tool in editor and option bar."""
        self.editor.set_tool(tool_id)
        if hasattr(self, 'tool_options_bar'):
            self.tool_options_bar.set_tool(tool_id)

    def unified_import(self):
        """Unified Import Function combining Design and Photo-Weave."""
        modes = [
            "Standard Design Import (Editable)",
            "Photo-Weave AI (Direct to Loom)"]
        mode, ok = QInputDialog.getItem(
            self, "Import Mode", "Select Import Type:", modes, 0, False)

        if not ok:
            return

        if mode == modes[0]:
            self.import_image_ai()
        else:
            self.import_photo_weave()

    def import_image_ai(self):
        """Professional loom import with specifications dialog."""
        # Show loom import dialog
        dialog = LoomImportDialog(parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        specs = dialog.get_specifications()

        if not specs["image_path"]:
            QMessageBox.warning(self, "No File", "Please select an image file")
            return

        try:
            from sj_das.core.image_ingestor import ImageIngestionEngine
            ingestor = ImageIngestionEngine()

            # Show Wait Cursor
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            # Run AI Ingestion with loom specifications
            processed_cv = ingestor.process_image(
                specs["image_path"],
                target_width=specs["hooks"],
                max_colors=specs["colors"]
            )

            # Load result into editor
            self.editor.set_image(processed_cv)

            # Store specifications for export
            self.current_loom_specs = {
                "hooks": specs["hooks"],
                "reed": specs["reed"],
                "component": specs["component"]
            }

            QApplication.restoreOverrideCursor()

            QMessageBox.information(
                self,
                "Loom Ready",
                f"Design Loaded:\n"
                f"• Hooks: {specs['hooks']}\n"
                f"• Reed: {specs['reed']}\n"
                f"• Component: {specs['component']}\n"
                f"• Colors: {specs['colors']}"
            )

        except ImportError as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(
                self,
                "Missing Dependency",
                f"AI Engine requires libraries: {e}")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Import Error", str(e))

    def show_generation_dialog(self, variations=False):
        # Quick Dialog for Prototype
        from PyQt6.QtWidgets import QInputDialog, QProgressDialog
        title = "AI Variations Generator" if variations else "AI Loom Generator"
        prompt_text = "Describe Base Pattern:" if variations else "Describe Pattern:"

        text, ok = QInputDialog.getText(self, title, prompt_text)

        if ok and text:
            # Setup Progress Dialog
            task_name = "Generating 3 Variations..." if variations else "Generating Graph Paper Design..."
            self.gen_progress = QProgressDialog(
                task_name, "Cancel", 0, 0, self)
            self.gen_progress.setWindowModality(Qt.WindowModality.WindowModal)
            self.gen_progress.show()

            # Start Thread
            self.gen_thread = GenerationThread(text, variations)
            self.gen_thread.finished_signal.connect(
                self.on_generation_finished)
            self.gen_thread.error_signal.connect(self.on_generation_error)
            self.gen_thread.start()

    def on_generation_finished(self, result):
        self.gen_progress.close()
        try:
            # Result can be single img or list
            if isinstance(result, list):
                # Handle Variations
                # Ask user to pick one? Or show side-by-side?
                # Simple Prototype: Show a dialog with buttons to pick 1, 2, or
                # 3
                from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel,
                                             QPushButton, QVBoxLayout)
                d = QDialog(self)
                d.setWindowTitle("Select Variation")
                l = QHBoxLayout(d)

                selected_img = None

                def pick(img):
                    nonlocal selected_img
                    selected_img = img
                    d.accept()

                for i, img in enumerate(result):
                    v_layout = QVBoxLayout()
                    # Convert to Pixmap for display
                    h, w, c = img.shape
                    qimg = QImage(
                        img.data, w, h, w * 3, QImage.Format.Format_BGR888)
                    pix = QPixmap.fromImage(qimg).scaled(
                        200, 200, Qt.AspectRatioMode.KeepAspectRatio)

                    lbl = QLabel()
                    lbl.setPixmap(pix)
                    v_layout.addWidget(lbl)

                    btn = QPushButton(f"Select #{i+1}")
                    btn.clicked.connect(lambda checked, x=img: pick(x))
                    v_layout.addWidget(btn)

                    l.addLayout(v_layout)

                if d.exec() and selected_img is not None:
                    self.editor.set_image(selected_img)
                    QMessageBox.information(
                        self, "Success", "Variation Loaded!")
                    self.auto_analyze_on_load()
            else:
                # Single Image
                self.editor.set_image(result)
                QMessageBox.information(
                    self, "Success", "Generated Loom-Ready Graph Pattern!")
                self.auto_analyze_on_load()
                self.auto_analyze_on_load()
        except Exception as e:
            QMessageBox.critical(self, "Display Error", str(e))

    # --- PHASE 8: ADJUSTMENTS ---
    def apply_brightness_contrast(self):
        """Open simple dialog for B/C."""
        # Simple input dialogs for now, ideally a preview dialog
        b, ok1 = QInputDialog.getInt(
            self, "Brightness", "Brightness (-100 to 100):", 0, -100, 100)
        if not ok1:
            return

        c, ok2 = QInputDialog.getInt(
            self, "Contrast", "Contrast (-100 to 100):", 0, -100, 100)
        if not ok2:
            return

        self.editor.apply_adjustment("brightness_contrast", (b, c))

    def apply_hue_saturation(self):
        """Open simple dialog for H/S/L."""
        h, ok1 = QInputDialog.getInt(
            self, "Hue", "Hue Shift (-180 to 180):", 0, -180, 180)
        if not ok1:
            return

        s, ok2 = QInputDialog.getInt(
            self, "Saturation", "Saturation (-100 to 100):", 0, -100, 100)
        if not ok2:
            return

        self.editor.apply_adjustment("hue_saturation", (h, s))

    def apply_filter_gaussian_blur(self):
        self.editor.apply_filter("blur")

    def apply_filter_sharpen(self):
        self.editor.apply_filter("sharpen")
    # ---------------------------

    def on_generation_error(self, err_msg):
        self.gen_progress.close()
        QMessageBox.critical(self, "Generation Failed", f"AI Error: {err_msg}")

    def _qimage_to_cv2(self, qimg):
        # Helper to convert back
        qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
        w, h = qimg.width(), qimg.height()
        ptr = qimg.bits()
        ptr.setsize(h * w * 3)
        return np.array(ptr).reshape(h, w, 3)

    def on_tool_selected(self, tool_id_str):
        """Handle selection from ModernToolBar or CategorizedToolbar."""
        mapping = {
            # Old toolbar IDs
            "select": PixelEditorWidget.TOOL_SELECT_RECT,
            "pen": PixelEditorWidget.TOOL_BRUSH,
            "eraser": PixelEditorWidget.TOOL_ERASER,
            "fill": PixelEditorWidget.TOOL_FILL,
            "shapes": PixelEditorWidget.TOOL_RECT,
            "magic_wand": PixelEditorWidget.TOOL_MAGIC_WAND,
            "eyedropper": PixelEditorWidget.TOOL_PICKER,
            "hand": PixelEditorWidget.TOOL_PAN,
            "stamp": PixelEditorWidget.TOOL_CLONE,
            "zoom": PixelEditorWidget.TOOL_PAN,

            # New categorized toolbar IDs - Selection
            "rect_select": PixelEditorWidget.TOOL_SELECT_RECT,
            "ellipse_select": PixelEditorWidget.TOOL_SELECT_ELLIPSE,
            "lasso": PixelEditorWidget.TOOL_LASSO,
            "polygon_lasso": PixelEditorWidget.TOOL_LASSO,
            "wand": PixelEditorWidget.TOOL_MAGIC_WAND,

            # New categorized toolbar IDs - Draw
            "brush": PixelEditorWidget.TOOL_BRUSH,
            "pencil": PixelEditorWidget.TOOL_PENCIL,
            "airbrush": PixelEditorWidget.TOOL_AIRBRUSH,
            "clone": PixelEditorWidget.TOOL_CLONE,

            # New categorized toolbar IDs - Paint
            "gradient": 16,  # TOOL_GRADIENT (if implemented)
            "pattern": PixelEditorWidget.TOOL_FILL,  # Pattern fill mode

            # New categorized toolbar IDs - Shapes
            "rectangle": PixelEditorWidget.TOOL_RECT,
            "ellipse": PixelEditorWidget.TOOL_ELLIPSE,
            "circle": PixelEditorWidget.TOOL_ELLIPSE,
            "line": PixelEditorWidget.TOOL_LINE,

            # New categorized toolbar IDs - Transform
            "perspective": PixelEditorWidget.TOOL_PERSPECTIVE,
            "move": PixelEditorWidget.TOOL_SELECT_RECT,  # Move is select + drag

            # New categorized toolbar IDs - View
            "pan": PixelEditorWidget.TOOL_PAN,
        }

        if tool_id_str == "text":
            self.activate_text_tool()
            return

        tid = mapping.get(tool_id_str)
        if tid is not None:
            self.editor.current_tool = tid  # Set tool ID on editor
            # Also update cursor? Editor handles it?
            # Editor usually updates cursor on mouse event, but let's see.
            # Ideally editor.set_tool(tid) is better if it exists.
            # Looking at editor_widget.py, it assigns self.current_tool
            # directly.
            pass

            self.toast.show_message(
                f"Tool: {tool_id_str.replace('_', ' ').title()}")

    def update_history_panel(self, idx):
        """Update history panel implementation."""
        # This is a naive implementation; ideally HistoryPanel should manage itself via stack reference
        # For V1, we just re-list? No, QUndoStack doesn't expose command list easily.
        # We'll just append simple states or highlight current.
        # Actually, let's just highlight.
        if hasattr(self, 'history_dock'):
            count = self.history_dock.history_list.count()
            if idx < count:
                self.history_dock.history_list.setCurrentRow(idx)
            else:
                # New command pushed?
                cmd = self.editor.undo_stack.command(idx - 1)
                if cmd:
                    self.history_dock.add_state(cmd.text())

    def create_menu_bar(self):
        """Creates clean modern menu bar (File, Edit, View, Tools, Help)."""
        print("=" * 60)
        print("CREATING CLEAN MENU BAR - NO MORE CLUTTER!")
        print("=" * 60)

        # Create menu bar
        menu_bar = self.menuBar()
        menu_bar.setVisible(True)  # Explicitly make visible
        # Don't use native menu bar (important for Windows)
        menu_bar.setNativeMenuBar(False)
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #252233;
                color: #E2E8F0;
                border-bottom: 1px solid #3730A3;
                padding: 6px;
                font-size: 13px;
                min-height: 32px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                color: #E2E8F0;
            }
            QMenuBar::item:selected {
                background-color: #6366F1;
            }
            QMenu {
                background-color: #252233;
                color: #E2E8F0;
                border: 1px solid #3730A3;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                color: #E2E8F0;
            }
            QMenu::item:selected {
                background-color: #6366F1;
            }
        """)

        print("Menu bar styled with modern indigo theme!")

        # File Menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New", self.new_project)
        file_menu.addAction("Open...", self.unified_import)
        file_menu.addAction("Save", self.save_current_project)
        file_menu.addAction("Save As...", self.save_current_project)
        file_menu.addSeparator()
        file_menu.addAction("Export...", self.export_design)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo (Ctrl+Z)", lambda: None)
        edit_menu.addAction("Redo (Ctrl+Y)", lambda: None)
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", lambda: None)
        edit_menu.addAction("Copy", lambda: None)
        edit_menu.addAction("Paste", lambda: None)

        # View Menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction("Zoom In", lambda: None)
        view_menu.addAction("Zoom Out", lambda: None)
        view_menu.addAction("Fit to Screen", lambda: None)
        view_menu.addSeparator()
        view_menu.addAction("Show Grid", lambda: None)
        view_menu.addAction("Show Rulers", lambda: None)

        # Tools Menu (ALL tools here)
        tools_menu = menu_bar.addMenu("Tools")

        # Selection Tools
        selection_menu = tools_menu.addMenu("Selection")
        selection_menu.addAction(
            "Rectangle Select (M)",
            lambda: self.on_tool_selected("rect_select"))
        selection_menu.addAction(
            "Ellipse Select",
            lambda: self.on_tool_selected("ellipse_select"))
        selection_menu.addAction(
            "Magic Wand (W)",
            lambda: self.on_tool_selected("wand"))

        # Drawing Tools
        drawing_menu = tools_menu.addMenu("Drawing")
        drawing_menu.addAction("Brush (B)",
                               lambda: self.on_tool_selected("brush"))
        drawing_menu.addAction(
            "Pencil", lambda: self.on_tool_selected("pencil"))
        drawing_menu.addAction("Eraser (E)",
                               lambda: self.on_tool_selected("eraser"))

        # Paint Tools
        paint_menu = tools_menu.addMenu("Paint")
        paint_menu.addAction("Fill (G)", lambda: self.on_tool_selected("fill"))
        paint_menu.addAction("Gradient",
                             lambda: self.on_tool_selected("gradient"))
        paint_menu.addAction("Eyedropper (I)",
                             lambda: self.on_tool_selected("eyedropper"))

        # Shape Tools
        shape_menu = tools_menu.addMenu("Shapes")
        shape_menu.addAction("Rectangle",
                             lambda: self.on_tool_selected("rectangle"))
        shape_menu.addAction(
            "Ellipse", lambda: self.on_tool_selected("ellipse"))
        shape_menu.addAction("Line", lambda: self.on_tool_selected("line"))

        # AI Tools
        tools_menu.addSeparator()
        ai_menu = tools_menu.addMenu("AI Tools")
        ai_menu.addAction("Generate Design", self.show_generation_dialog)
        ai_menu.addAction("Pattern Detection", self.detect_pattern_from_image)
        ai_menu.addAction("Auto-Segment", self.run_segmentation)
        ai_menu.addAction("Train Model", self.train_custom_model)

        # Adjustments
        tools_menu.addSeparator()
        adj_menu = tools_menu.addMenu("Adjustments")
        adj_menu.addAction(
            "Brightness/Contrast",
            self.apply_brightness_contrast)
        adj_menu.addAction("Hue/Saturation", self.apply_hue_saturation)

        # Filters
        filter_menu = tools_menu.addMenu("Filters")
        filter_menu.addAction("Gaussian Blur", self.apply_filter_gaussian_blur)
        filter_menu.addAction("Sharpen", self.apply_filter_sharpen)
        filter_menu.addAction("Emboss", self.apply_filter_emboss)
        filter_menu.addAction("Edge Detect", self.apply_filter_edge_detect)

        # Help Menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("Documentation", lambda: None)
        help_menu.addAction("Keyboard Shortcuts", lambda: None)
        help_menu.addSeparator()
        help_menu.addAction("About SJ-DAS", lambda: None)

    def new_project(self):
        """Create new project."""
        # Implementation
        pass

    def export_design(self):
        """Export design."""
        # Implementation
        pass

    def save_current_project(self):
        if not self.editor.original_image:
            return

        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            from sj_das.core.project_manager import ProjectManager
            pm = ProjectManager()

            # Prepare Data
            meta = {
                'reed': self.reed_count,
                'kali': self.kali_count,
                'locking': self.locking_px,
                'width': self.editor.original_image.width(),
                'height': self.editor.original_image.height()
            }

            data = {
                'original': self._qimage_to_cv2(self.editor.original_image),
                'mask': self.editor.get_mask_array(),
                'meta': meta
            }

            try:
                pm.save_project(path, data)
                QMessageBox.information(
                    self, "Saved", f"Project saved to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def run_fabric_simulation(self):
        # ... (Existing Sim Logic) ...
        # (This is just context, I'm appending the method below)
        pass

    def show_quantize_dialog(self):
        """Competitor Feature: Color Reduction / Cleaning."""
        if not self.editor.mask_image:
            return

        k, ok = QInputDialog.getInt(
            self, "Color Reduction", "Target Number of Colors (Yarns):", 8, 2, 256)
        if ok:
            # Convert
            ptr = self.editor.mask_image.bits()
            ptr.setsize(self.editor.mask_image.height() *
                        self.editor.mask_image.width() * 4)
            arr = np.frombuffer(
                ptr, np.uint8).reshape(
                (self.editor.mask_image.height(), self.editor.mask_image.width(), 4))
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            from sj_das.core.quantizer import ColorQuantizer
            cq = ColorQuantizer()

            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            res_img, palette = cq.reduce_colors_kmeans(img_bgr, k)
            QApplication.restoreOverrideCursor()

            # Ask to Apply
            # Ideally show preview. For now, direct apply.
            if QMessageBox.question(
                    self, "Confirm", f"Reduced to {k} colors. Apply?") == QMessageBox.StandardButton.Yes:
                # Update Editor
                self.import_generated_image(
                    self.generative_engine._numpy_to_qimage(res_img))
                QMessageBox.information(self, "Done", "Image Quantized.")

        # Undo/Redo
        btn_undo = QPushButton()
        btn_undo.setIcon(DASIcons.get_icon("undo"))
        btn_undo.setToolTip("Undo (Ctrl+Z)")
        btn_undo.setFixedSize(32, 32)
        btn_undo.clicked.connect(self.editor.undo_stack.undo)
        layout.addWidget(btn_undo)

        btn_redo = QPushButton()
        btn_redo.setIcon(DASIcons.get_icon("redo"))
        btn_redo.setToolTip("Redo (Ctrl+Y)")
        btn_redo.setFixedSize(32, 32)
        btn_redo.clicked.connect(self.editor.undo_stack.redo)
        layout.addWidget(btn_redo)

        # Contextual Tool Settings
        layout.addSpacing(20)
        layout.addWidget(QLabel("Brush:"))
        self.spin_size = QSpinBox()
        self.spin_size.setRange(1, 200)
        self.spin_size.setValue(5)
        self.spin_size.valueChanged.connect(self.update_brush_settings)
        layout.addWidget(self.spin_size)

        layout.addWidget(QLabel("Target:"))
        self.combo_class = QComboBox()
        self.combo_class.addItems(
            ["Body (Red)", "Border (Green)", "Pallu (Blue)"])
        self.combo_class.currentIndexChanged.connect(
            self.update_brush_settings)
        layout.addWidget(self.combo_class)

        layout.addStretch()

        # View toggles
        self.chk_grid = QCheckBox("Grid")
        self.chk_grid.toggled.connect(self.toggle_grid)
        layout.addWidget(self.chk_grid)

        self.btn_export = QPushButton("Export Assembly")
        self.btn_export.clicked.connect(self.export_assembly)
        self.btn_export.setEnabled(True)
        self.btn_export.setStyleSheet(
            "background-color: #0078d4; color: white; font-weight: bold; border: none; padding: 5px 10px; border-radius: 4px;")
        layout.addWidget(self.btn_export)

        # Xerox Mode (Smart Stitch)
        self.btn_xerox = QPushButton("Xerox Stitch")
        self.btn_xerox.setToolTip("Auto-Assemble Body + Border")
        # Using copy icon as placeholder
        self.btn_xerox.setIcon(DASIcons.get_icon("copy"))
        self.btn_xerox.clicked.connect(self.run_xerox_mode)
        self.btn_xerox.setEnabled(True)
        layout.addWidget(self.btn_xerox)

        # Shortcuts Help
        btn_help = QPushButton("?")
        btn_help.setFixedSize(24, 24)
        btn_help.setStyleSheet(
            "border-radius: 12px; background: #555; color: white;")
        btn_help.clicked.connect(self.show_shortcuts_help)
        layout.addWidget(btn_help)

    def create_right_panel(self):
        """Creates the modern right sidebar with indigo theme."""
        self.right_panel = QWidget()
        self.right_panel.setFixedWidth(320)
        self.right_panel.setObjectName("right_dock")

        dock_layout = QVBoxLayout(self.right_panel)
        dock_layout.setContentsMargins(0, 0, 0, 0)
        dock_layout.setSpacing(0)

        # Create vertical splitter with modern indigo styling
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2D2A3E;
                height: 2px;
                margin: 0px;
            }
            QSplitter::handle:hover {
                background-color: #6366F1;
            }
        """)

        # 1. Top Section: Tabbed Panels (Modern indigo theme)
        top_tabs = QTabWidget()
        top_tabs.setObjectName("dock_tabs")
        top_tabs.setMinimumHeight(300)
        top_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3730A3;
                background-color: #252233;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #94A3B8;
                padding: 10px 16px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                color: #E2E8F0;
                border-bottom: 2px solid #6366F1;
            }
        """)

        # Navigator Tab
        from sj_das.ui.navigator_widget import NavigatorWidget
        self.navigator = NavigatorWidget(self.editor)
        top_tabs.addTab(self.navigator, "Navigator")

        # Color Palette Tab
        from sj_das.ui.panels.color_palette import ColorPalettePanel
        self.color_palette_panel = ColorPalettePanel(self.editor)
        self.color_palette_panel.color_selected.connect(self.on_color_picked)
        top_tabs.addTab(self.color_palette_panel, "Colors")

        # Yarn Palette Tab
        from sj_das.ui.palette_widget import YarnPaletteWidget
        self.palette_widget = YarnPaletteWidget()
        self.palette_widget.color_selected.connect(self.on_yarn_selected)
        top_tabs.addTab(self.palette_widget, "Yarn")

        # Weave Library Tab
        from sj_das.ui.weave_library import WeaveLibraryWidget
        self.weave_library = WeaveLibraryWidget()
        self.weave_library.weave_selected.connect(self.on_weave_selected)
        top_tabs.addTab(self.weave_library, "Weaves")

        splitter.addWidget(top_tabs)

        # 2. Bottom Section: Adjustments (takes remaining space)
        from sj_das.ui.panels.adjustments_panel import AdjustmentsPanel
        self.adjustments_panel = AdjustmentsPanel(self)
        self.adjustments_panel.setMinimumHeight(200)
        splitter.addWidget(self.adjustments_panel)

        # Set proportional sizes: Top 60%, Bottom 40%
        total_height = 800
        splitter.setSizes([
            int(total_height * 0.60),
            int(total_height * 0.40),
        ])

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        dock_layout.addWidget(splitter)

        # Set default tab to Colors
        top_tabs.setCurrentIndex(1)

    def set_tool(self, tool_id):
        self.editor.set_tool(tool_id)

    def toggle_grid(self, checked):
        self.editor.set_show_grid(checked)

    def update_brush_settings(self):
        size = self.spin_size.value()
        class_idx = self.combo_class.currentIndex() + 1
        colors = {
            1: QColor(255, 0, 0, 100),   # Body
            2: QColor(0, 255, 0, 100),   # Border
            3: QColor(0, 0, 255, 100)    # Pallu
        }
        self.editor.set_brush_size(size)
        self.editor.set_brush_color(
            colors.get(
                class_idx, QColor(
                    255, 255, 255)))

    def on_weave_selected(self, pattern, name):
        # Direct assignment if method missing, but editor has set_pattern
        self.editor.pattern = pattern
        self.editor.set_pattern(pattern)
        # Select Fill tool automatically when weave is picked
        self.btn_fill.click()
        # self.status_bar.showMessage(f"Active Pattern: {name}") # Need access
        # to status bar

    def on_yarn_selected(self, color):
        if color.isValid():
            self.editor.brush_color = color
            # self.btn_brush.click() # Optional auto-switch

    def on_color_picked(self, color):
        # Update palette or UI if needed
        self.editor.brush_color = color

    def on_color_picked(self, color):
        """Handle color picking from the editor."""
        # Update UI if needed (e.g., color buttons)
        if hasattr(self, 'editor'):
            self.editor.brush_color = color
            # If we had a color panel, we'd update it here
            pass

    def show_shortcuts_help(self):
        from PyQt6.QtWidgets import QMessageBox
        shortcuts = """
        <h3>Designer Shortcuts</h3>
        <table cellspacing='5'>
            <tr><td><b>V / H</b></td><td>Move / Pan</td></tr>
            <tr><td><b>M</b></td><td>Select</td></tr>
            <tr><td><b>L</b></td><td>Lasso</td></tr>
            <tr><td><b>W</b></td><td>Magic Wand</td></tr>
            <tr><td><b>B</b></td><td>Brush</td></tr>
            <tr><td><b>E</b></td><td>Eraser</td></tr>
            <tr><td><b>G</b></td><td>Fill Bucket</td></tr>
            <tr><td><b>I</b></td><td>Eyedropper</td></tr>
            <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
        </table>
        """
        QMessageBox.information(self, "Shortcut Guide", shortcuts)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Design", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            # Ask for Loom Configuration
            dialog = CanvasSizeDialog(self)
            if dialog.exec():
                w, h, reed, kali, locking = dialog.get_dimensions()

                self.reed_count = reed
                self.kali_count = kali
                self.locking_px = locking

                self.current_image_path = file_name
                img = cv2.imread(file_name)

                if img is not None:
                    inter = cv2.INTER_AREA if img.shape[1] > w or img.shape[0] > h else cv2.INTER_LINEAR

                    img = cv2.resize(img, (w, h), interpolation=inter)

                    self.editor.set_image(img)
                    self.btn_segment.setEnabled(True)
                    self.btn_export.setEnabled(True)
                    self.current_mask = None

                    msg = f"Design loaded: {w}x{h} hooks ({reed} Reed)"

                    unique_colors = np.unique(
                        img.reshape(-1, img.shape[2]), axis=0)
                    if len(unique_colors) <= 16:
                        reply = QMessageBox.question(
                            self, "Smart Import",
                            "This uses few colors. Import as Mask?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.import_mask_from_image(img)
                            msg += "\n(Imported as Mask)"

                    QMessageBox.information(self, "Image Loaded", msg)

    def import_mask_from_image(self, img):
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        mask[(r > 100) & (r > g) & (r > b)] = 1
        mask[(g > 100) & (g > r) & (g > b)] = 2
        mask[(b > 100) & (b > r) & (b > g)] = 3
        self.editor.set_mask(mask)
        self.current_mask = mask

    def run_segmentation(self):
        # Support both file-based and memory-based (generated) images
        if self.editor.original_image is None:
            return

        self.btn_segment.setEnabled(False)

        # Prefer path for speed/caching, else use buffer
        if self.current_image_path:
            inp = self.current_image_path
        else:
            # Convert QImage to CV2
            inp = self._qimage_to_cv2(self.editor.original_image)

        self.thread = SegmentationThread(self, inp, True)
        self.thread.finished.connect(self.on_segmentation_finished)
        self.thread.start()

    def on_segmentation_finished(self, mask):
        self.btn_segment.setEnabled(True)
        self.current_mask = mask
        if mask is not None:
            self.editor.set_mask(mask)

    def export_assembly(self):
        if not self.current_image_path:
            return
        dialog = AssemblyExportDialog(self.reed_count, self)
        dialog.spin_kali.setValue(self.kali_count)
        dialog.spin_locking.setValue(self.locking_px)

        if dialog.exec():
            seq, d_type, kali, locking = dialog.get_config()
            img = self.editor.get_current_image()
            mask_arr = self.editor.get_mask_array()
            if mask_arr is None or img is None:
                return

            components = {}
            body_mask = (mask_arr == 1).astype(np.uint8) * 255
            components['body'] = cv2.bitwise_and(img, img, mask=body_mask)

            border_mask = (mask_arr == 2).astype(np.uint8) * 255
            if border_mask.sum() > 0:
                components['border_l'] = cv2.bitwise_and(
                    img, img, mask=border_mask)
                components['border_r'] = components['border_l']

            pallu_mask = (mask_arr == 3).astype(np.uint8) * 255
            if pallu_mask.sum() > 0:
                components['pallu'] = cv2.bitwise_and(
                    img, img, mask=pallu_mask)

            from sj_das.core.assembler import AssemblerEngine
            engine = AssemblerEngine()
            config = {'acchu': img.shape[1], 'kali': kali, 'locking': locking}

            try:
                final = engine.assemble_saree(components, config)
                path, _ = QFileDialog.getSaveFileName(
                    self, "Save Assembly", f"{seq}_{d_type}.bmp", "BMP (*.bmp)")
                if path:
                    import cv2
                    cv2.imwrite(path, final)
                    QMessageBox.information(
                        self, "Saved", f"Exported to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def run_xerox_mode(self):
        """
        Smart 'Xerox' Mode: Auto-detects Body and Border in current canvas/masks
        and seamlessly stitches them using SmartAssembler.
        """
        if not self.current_mask is not None:
            QMessageBox.warning(
                self,
                "Xerox Mode",
                "Please segment the design first (AI Segment).")
            return

        # 1. Extract Components
        img = self.editor.get_current_image()
        mask_arr = self.editor.get_mask_array()

        body_mask = (mask_arr == 1).astype(np.uint8) * 255
        border_mask = (mask_arr == 2).astype(np.uint8) * 255

        if body_mask.sum() == 0 or border_mask.sum() == 0:
            QMessageBox.warning(
                self,
                "Missing Parts",
                "Needs both Body (Red) and Border (Green) regions.")
            return

        body = cv2.bitwise_and(img, img, mask=body_mask)
        # Crop to bounding box? For now use masked.
        border = cv2.bitwise_and(img, img, mask=border_mask)

        # 2. Smart Assemble
        from sj_das.core.smart_assembler import SmartAssembler
        assembler = SmartAssembler()

        # Basic layout assumption: Body Left, Border Right
        try:
            stitched = assembler.stitch_components(body, border, overlap=40)
            self.editor.set_image(stitched)
            QMessageBox.information(
                self,
                "Xerox Complete",
                "Seamlessly Stitched Body & Border!")
        except Exception as e:
            QMessageBox.critical(self, "Stitch Error", str(e))

    def show_resize_dialog(self):
        if not self.editor.original_image:
            return

        # Simple Dialog for Prototype
        d = QDialog(self)
        d.setWindowTitle("Resize Canvas")
        l = QVBoxLayout(d)

        # Width
        l.addWidget(QLabel("Width:"))
        sb_w = QSpinBox()
        sb_w.setRange(1, 10000)
        sb_w.setValue(self.editor.original_image.width())
        l.addWidget(sb_w)

        # Height
        l.addWidget(QLabel("Height:"))
        sb_h = QSpinBox()
        sb_h.setRange(1, 10000)
        sb_h.setValue(self.editor.original_image.height())
        l.addWidget(sb_h)

        # Anchor
        l.addWidget(QLabel("Anchor:"))
        cb_anchor = QComboBox()
        cb_anchor.addItems(["Center", "Top-Left"])
        l.addWidget(cb_anchor)

        # Scale Option
        chk_scale = QCheckBox("Scale Content (Retain Design)")
        chk_scale.setToolTip(
            "If checked, the image will be resized to fit. If unchecked, canvas is extended.")
        l.addWidget(chk_scale)

        # Buttons
        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(d.accept)
        bb.rejected.connect(d.reject)
        l.addWidget(bb)

        if d.exec():
            if chk_scale.isChecked():
                self.editor.resize_image(sb_w.value(), sb_h.value())
            else:
                anchor_map = {0: "center", 1: "top-left"}
                self.editor.extend_canvas(
                    sb_w.value(), sb_h.value(), anchor_map[cb_anchor.currentIndex()])

    def pick_brush_color(self):
        """Opens system color dialog."""
        c = QColorDialog.getColor(
            self.editor.brush_color,
            self,
            "Select Brush Color")
        if c.isValid():
            self.editor.set_brush_color(c)
            # visual feedback? maybe change button color?

    def export_loom_bmp(self):
        """Export the current design state to a Jacquard Loom BMP."""
        # Get Current Image (Not just mask, but full design)
        # We prefer the raw CV2 image if available for better resolution/colors?
        # Or self.editor.canvas?

        # If we have a 'mask_array' (segmentation), use that.
        # But 'LoomExporter' now handles color indexing intelligently.
        # Let's use the visible canvas from editor.
        if hasattr(self.editor, 'canvas') and self.editor.canvas is not None:
            image_to_export = self.editor.canvas
        elif hasattr(self.editor, 'mask_image') and not self.editor.mask_image.isNull():
            # Fallback to mask
            image_to_export = self._qimage_to_cv2(self.editor.mask_image)
        else:
            QMessageBox.warning(
                self,
                "No Design",
                "Please draw or segment the design first.")
            return

        # Extract colors for dialog
        unique_colors = []
        if len(image_to_export.shape) == 3:
            # Simple quantization or unique check for dialog preview
            pixels = image_to_export.reshape(-1, 3)
            # Limit to top 16 for UI speed
            u_colors = np.unique(pixels, axis=0)
            if len(u_colors) > 32:
                u_colors = u_colors[:32]

            for b, g, r in u_colors:
                unique_colors.append(QColor(int(r), int(g), int(b)))

        # Instantiate Dialog with Correct Signature
        dialog = LoomExportDialog(unique_colors, self)

        if dialog.exec():
            config = dialog.get_export_config()

            # Use Professional LoomExporter
            from sj_das.core.loom_exporter import LoomExporter
            exporter = LoomExporter()

            path, _ = QFileDialog.getSaveFileName(
                self, "Save Loom File", "design_loom.bmp", "BMP (*.bmp)")
            if path:
                try:
                    # Pass full config to exporter
                    success = exporter.export(
                        image=image_to_export,
                        output_path=path,
                        hooks=config['hooks'],
                        # Keep aspect or use full height
                        picks=image_to_export.shape[0],
                        reed=config['reed'],
                        component=config['component'],
                        weave_map=config['weave_map'],
                        validate_float=config['validate_float'],
                        auto_fix_floats=config['auto_fix_floats'],  # NEW
                        max_float=config['max_float'],             # NEW
                        designer=config['designer'],
                        notes=config['notes']
                    )

                    if success:
                        msg = "Export Successful!"
                        if config['auto_fix_floats']:
                            msg += "\\n\\n(Auto-Locking applied to secure floats)"
                        QMessageBox.information(self, "Success", msg)
                    else:
                        QMessageBox.critical(
                            self, "Export Failed", "Check logs for details.")

                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def activate_text_tool(self):
        try:
            from sj_das.tools.text_tool import TextTool
            if not hasattr(self, 'text_tool'):
                self.text_tool = TextTool(self.editor.scene(), self.editor)
            self.text_tool.activate()
        except Exception as e:
            QMessageBox.warning(self, "Text Tool", str(e))

    def show_grid_settings(self):
        """Show grid and snap settings dialog."""
        from sj_das.ui.dialogs.grid_settings import GridSettingsDialog
        dialog = GridSettingsDialog(self.editor, self)
        if dialog.exec():
            settings = dialog.get_settings()
            self.editor.grid_spacing = settings['grid_spacing']
            self.editor.show_grid = settings['show_grid']
            self.editor.snap_to_grid = settings['snap_to_grid']
            self.editor.snap_to_guides = settings['snap_to_guides']
            self.editor.viewport().update()  # Refresh grid display

    def apply_brightness_contrast(self):
        try:
            from sj_das.ui.dialogs.color_adjustments import (
                BrightnessContrastDialog, ColorAdjustments)
            d = BrightnessContrastDialog(self)
            if d.exec() and hasattr(self.editor, 'canvas') and self.editor.canvas is not None:
                b, c = d.get_values()
                self.editor.canvas = ColorAdjustments.adjust_brightness_contrast(
                    self.editor.canvas, b, c)
                self.editor.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def apply_hue_saturation(self):
        try:
            from sj_das.ui.dialogs.color_adjustments import (
                ColorAdjustments, HueSaturationDialog)
            d = HueSaturationDialog(self)
            if d.exec() and hasattr(self.editor, 'canvas') and self.editor.canvas is not None:
                h, s, l = d.get_values()
                self.editor.canvas = ColorAdjustments.adjust_hue_saturation(
                    self.editor.canvas, h, s, l)
                self.editor.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def apply_filter_gaussian_blur(self):
        try:
            from sj_das.core.image_filters import FilterDialogs, ImageFilters
            d = FilterDialogs.gaussian_blur_dialog(self)
            if d.exec() and hasattr(self.editor, 'canvas') and self.editor.canvas is not None:
                r = d.radius_slider.value()
                self.editor.canvas = ImageFilters.gaussian_blur(
                    self.editor.canvas, r)
                self.editor.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def apply_filter_sharpen(self):
        try:
            from sj_das.core.image_filters import FilterDialogs, ImageFilters
            d = FilterDialogs.sharpen_dialog(self)
            if d.exec() and hasattr(self.editor, 'canvas') and self.editor.canvas is not None:
                s = d.strength_slider.value() / 100.0
                self.editor.canvas = ImageFilters.sharpen(
                    self.editor.canvas, s)
                self.editor.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def apply_filter_emboss(self):
        try:
            from sj_das.core.image_filters import ImageFilters
            if hasattr(self.editor,
                       'canvas') and self.editor.canvas is not None:
                self.editor.canvas = ImageFilters.emboss(self.editor.canvas)
                self.editor.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def apply_filter_gaussian_blur(self):
        """Apply Gaussian Blur with dialog."""
        try:
            from sj_das.core.image_filters import FilterDialogs, ImageFilters
            d = FilterDialogs.gaussian_blur_dialog(self)

            # Store original for preview if needed
            original = self.editor.canvas.copy()

            # Live Preview Handler
            def update_preview(params):
                radius = params.get('radius', 5)
                preview_img = ImageFilters.gaussian_blur(original, radius)
                self.editor.canvas = preview_img
                self.editor.update_display()

            d.preview_requested.connect(update_preview)

            if d.exec():
                # Apply final
                params = d.get_parameters()
                update_preview(params)
            else:
                # Revert
                self.editor.canvas = original
                self.editor.update_display()

        except Exception as e:
            QMessageBox.warning(self, "Filter Error", str(e))

    def apply_filter_sharpen(self):
        """Apply Sharpen with dialog."""
        try:
            from sj_das.core.image_filters import FilterDialogs, ImageFilters
            d = FilterDialogs.sharpen_dialog(self)

            original = self.editor.canvas.copy()

            def update_preview(params):
                strength = params.get('strength', 1.0)
                preview_img = ImageFilters.sharpen(original, strength)
                self.editor.canvas = preview_img
                self.editor.update_display()

            d.preview_requested.connect(update_preview)

            if d.exec():
                params = d.get_parameters()
                update_preview(params)
            else:
                self.editor.canvas = original
                self.editor.update_display()

        except Exception as e:
            QMessageBox.warning(self, "Filter Error", str(e))

    def apply_filter_edge_detect(self):
        """Apply Edge Detection."""
        try:
            from sj_das.core.image_filters import ImageFilters
            if hasattr(self.editor,
                       'canvas') and self.editor.canvas is not None:
                self.editor.canvas = ImageFilters.edge_detect(
                    self.editor.canvas)
                self.editor.update_display()
        except Exception as e:
            QMessageBox.warning(self, "Filter Error", str(e))

    def apply_hue_saturation(self):
        """Adjust Hue/Saturation."""
        try:
            from sj_das.ui.dialogs.color_adjustments import (
                ColorAdjustments, HueSaturationDialog)
            d = HueSaturationDialog(self)

            original = self.editor.canvas.copy()

            if d.exec():
                h, s, v = d.get_values()
                self.editor.canvas = ColorAdjustments.adjust_hsv(
                    original, h, s, v)
                self.editor.update_display()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Adjustment Error",
                f"Not available: {str(e)}")

    def show_model_status_dialog(self):
        """Shows status of currently training models and active inference models."""
        from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QVBoxLayout

        d = QDialog(self)
        d.setWindowTitle("Unified AI Hive Mind Status")
        d.setMinimumWidth(400)

        layout = QVBoxLayout(d)

        # Active Model
        layout.addWidget(QLabel("<h3>⚡ Active Inference Model</h3>"))
        layout.addWidget(QLabel("<b>Current:</b> Progressive GAN (Standard)"))
        layout.addWidget(QLabel("<i>Optimized for speed.</i>"))

        layout.addSpacing(15)
        layout.addWidget(QLabel("<hr>"))
        layout.addSpacing(5)

        # Training Status
        layout.addWidget(
            QLabel("<h3>🧠 Background Training (LightStyleGAN)</h3>"))
        layout.addWidget(QLabel("Status: <b>RUNNING</b> (GPU: GTX 1650)"))

        # Mock Progress (Real data would come from log file)
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Epoch 137 / 600"))
        layout.addLayout(h_layout)

        pbar = QProgressBar()
        pbar.setValue(22)  # Approx 137/600
        pbar.setStyleSheet(
            "QProgressBar::chunk { background-color: #6C5CE7; }")
        layout.addWidget(pbar)

        layout.addWidget(QLabel(
            "<small>Note: System will auto-upgrade to 'World Class' upon completion.</small>"))

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(d.accept)
        layout.addWidget(btn_close)

        d.exec()

    def show_composer_dialog(self):
        """
        Smart Saree Composer UI.
        Allows user to select 3 images and stitches them perfectly.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Smart Saree Assembler")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout(dialog)

        paths = {"body": None, "border": None, "pallu": None}
        labels = {}

        def pick_file(k):
            path, _ = QFileDialog.getOpenFileName(
                self, f"Select {k.title()} Image", "", "Images (*.png *.jpg *.bmp)")
            if path:
                paths[k] = path
                labels[k].setText(f"{k.title()}: {os.path.basename(path)}")

        # Inputs
        grp = QGroupBox("Components")
        fl = QFormLayout(grp)

        for key in ["body", "border", "pallu"]:
            btn = QPushButton(f"Load {key.title()}...")
            lbl = QLabel("Not Selected")
            labels[key] = lbl
            btn.clicked.connect(lambda checked, k=key: pick_file(k))
            fl.addRow(btn, lbl)

        layout.addWidget(grp)

        # Options
        grp_opt = QGroupBox("Loom Settings")
        ol = QFormLayout(grp_opt)
        spin_w = QSpinBox()
        spin_w.setRange(100, 4800)
        spin_w.setValue(480)
        ol.addRow("Loom Width (Hooks):", spin_w)
        combo_mode = QComboBox()
        combo_mode.addItems(["double_sided", "single", "top_bottom"])
        ol.addRow("Border Mode:", combo_mode)
        layout.addWidget(grp_opt)

        # Action
        btn_run = QPushButton("⚡ Assemble Saree BMP")
        btn_run.setStyleSheet(
            "background-color: #007ACC; color: white; font-weight: bold; padding: 10px;")

        def run_assembly():
            from sj_das.core.smart_assembler import SmartAssembler

            # Load Images
            imgs = {}
            for k, p in paths.items():
                if p:
                    imgs[k] = cv2.imread(p)
                else:
                    imgs[k] = None

            if imgs["body"] is None:
                QMessageBox.warning(
                    dialog,
                    "Missing Body",
                    "Please select at least a Body image.")
                return

            assembler = SmartAssembler()
            try:
                result = assembler.assemble_saree_layout(
                    imgs["body"], imgs["border"], imgs["pallu"],
                    loom_width=spin_w.value(),
                    border_mode=combo_mode.currentText()
                )

                if result is not None:
                    self.import_generated_image(
                        self.generative_engine._numpy_to_qimage(result))
                    dialog.accept()
                    QMessageBox.information(
                        self, "Success", "Saree Assembled Successfully!")
            except Exception as e:
                QMessageBox.critical(dialog, "Assembly Error", str(e))

        btn_run.clicked.connect(run_assembly)
        layout.addWidget(btn_run)

        dialog.exec()

    def configure_ai_keys(self):
        """Allow user to input API Key for Real AI Generation."""
        from PyQt6.QtWidgets import QInputDialog
        key, ok = QInputDialog.getText(
            self, "AI Configuration", "Enter HuggingFace API Key (starts with hf_):")
        if ok and key:
            # Pass to engine
            if hasattr(self, 'generative_engine'):
                self.generative_engine.set_api_key(key)
                QMessageBox.information(
                    self, "AI Configured", "API Key Saved. 'Generate' will now use Cloud AI.")
            else:
                # Should have been initialized?
                # Wait, verify where GenerativeEngine is.
                # It's usually instantiated in show_generation_dialog context or globally.
                # Let's persist it in self.
                self.ai_api_key = key
                QMessageBox.information(
                    self, "AI Configured", "API Key Saved.")

    def on_yarn_selected(self, color_q):
        """Handle yarn palette selection."""
        # Set editor brush color
        self.editor.brush_color = color_q
        self.editor.set_tool(PixelEditorWidget.TOOL_BRUSH)

    def on_weave_selected(self, weave_name):
        """Handle weave pattern selection."""
        # For now, just log or set a 'pattern brush' state
        QMessageBox.information(
            self,
            "Weave Selected",
            f"Selected Weave: {weave_name}\n(Pattern Brush not fully active in this version)")

    def show_advanced_panels(self):
        """Show advanced panels (layers, history, palette) in main window."""
        if hasattr(self, 'parent') and hasattr(self.parent(), 'addDockWidget'):
            main_window = self.parent()

            if not self._panels_initialized:
                from PyQt6.QtCore import Qt

                from sj_das.ui.panels import (ColorPalettePanel, HistoryPanel,
                                              LayersPanel)

                # Create panels
                self.layers_panel = LayersPanel(main_window)
                self.history_panel = HistoryPanel(main_window)
                self.palette_panel = ColorPalettePanel(main_window)

                # Add to main window
                main_window.addDockWidget(
                    Qt.DockWidgetArea.RightDockWidgetArea,
                    self.layers_panel)
                main_window.addDockWidget(
                    Qt.DockWidgetArea.RightDockWidgetArea,
                    self.history_panel)
                main_window.addDockWidget(
                    Qt.DockWidgetArea.RightDockWidgetArea,
                    self.palette_panel)

                # Stack them vertically in tab mode
                main_window.tabifyDockWidget(
                    self.layers_panel, self.history_panel)
                main_window.tabifyDockWidget(
                    self.history_panel, self.palette_panel)

                # Show layers panel by default
                self.layers_panel.raise_()

                self._panels_initialized = True

                QMessageBox.information(self, "Advanced Panels",
                                        "✅ Advanced panels enabled!\n\n"
                                        "• Layers Panel - Organize your design\n"
                                        "• History Panel - Visualize undo/redo\n"
                                        "• Color Palette - Manage colors\n\n"
                                        "Check the right side of the window!"
                                        )
            else:
                # Toggle visibility
                visible = not self.layers_panel.isVisible()
                self.layers_panel.setVisible(visible)
                self.history_panel.setVisible(visible)
                self.palette_panel.setVisible(visible)

    def detect_pattern_from_image(self):
        """Detect and extract pattern from any image (Google, photos, etc.)."""
        import numpy as np

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image to Detect Pattern", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if not path:
            return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            yarn_count, ok = QInputDialog.getInt(
                self, "Yarn Count",
                "How many yarn colors to detect?\n(2-3 typical for most designs)",
                3, 2, 32, 1
            )
            if not ok:
                QApplication.restoreOverrideCursor()
                return

            pattern_engine = PatternDetectionEngine()
            pattern_graph, info = pattern_engine.extract_from_url(
                path, yarn_count)

            colors = [(255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0),
                      (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
            h, w = pattern_graph.shape
            rgb_pattern = np.zeros((h, w, 3), dtype=np.uint8)
            for i in range(min(yarn_count, len(colors))):
                mask = pattern_graph == i
                rgb_pattern[mask] = colors[i]

            self.editor.set_image(rgb_pattern)
            QApplication.restoreOverrideCursor()

            QMessageBox.information(self, "Pattern Detected",
                                    f"Pattern extracted successfully:\n\n"
                                    f"• Repeat Size: {info['repeat_width']}×{info['repeat_height']} pixels\n"
                                    f"• Yarn Colors: {info['num_colors']}\n"
                                    f"• Original: {info['original_size'][0]}×{info['original_size'][1]}\n\n"
                                    f"The detected pattern is now loaded in the editor.\n"
                                    f"You can refine it with editing tools!")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Pattern Detection Error",
                                 f"Failed to detect pattern:\n{str(e)}\n\n"
                                 f"Try with a clearer image showing repeating motifs.")

    def show_card_sequence_editor(self):
        """Show card sequence/details editor for jacquard control."""
        from PyQt6.QtWidgets import QDialog

        hooks = getattr(self, 'current_loom_specs', {}).get('hooks', 480)
        dialog = CardSequenceDialog(hooks=hooks, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            card_config = dialog.get_card_sequence()
            if not hasattr(self, 'current_loom_specs'):
                self.current_loom_specs = {}
            self.current_loom_specs['card_sequence'] = card_config

            QMessageBox.information(self, "Card Sequence Configured",
                                    f"Card lifting sequence configured:\n\n"
                                    f"• Pattern: {card_config['pattern_type']}\n"
                                    f"• Cards: {card_config['num_cards']}\n"
                                    f"• Sequence: {', '.join(map(str, card_config['lifting_sequence']))}\n\n"
                                    f"This will be included in export metadata.")


class LoomExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Loom BMP")
        self.resize(400, 300)
        from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialogButtonBox,
                                     QFormLayout)
        layout = QFormLayout(self)

        self.combo_body = QComboBox()
        self.combo_body.addItems(
            ["Satin 1/4 (Standard)", "Twill 2/2", "Plain 1/1"])

        self.combo_border = QComboBox()
        self.combo_border.addItems(
            ["Satin 1/4 (Standard)", "Twill 2/2", "Plain 1/1"])

        self.combo_pallu = QComboBox()
        self.combo_pallu.addItems(["Float (Heavy)", "Satin 1/4", "Plain 1/1"])

        self.chk_palette = QCheckBox("Export as Palette BMP (8-bit)")
        self.chk_palette.setToolTip(
            "Uncheck for Machine-Ready Binary BMP (1-bit)")
        self.chk_palette.setChecked(True)

        layout.addRow("Body Weave (Red):", self.combo_body)
        layout.addRow("Border Weave (Green):", self.combo_border)
        layout.addRow("Pallu Weave (Blue):", self.combo_pallu)
        layout.addRow("", self.chk_palette)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_settings(self):
        return {
            1: self.combo_body.currentIndex(),
            2: self.combo_border.currentIndex(),
            3: self.combo_pallu.currentIndex(),
            'palette': self.chk_palette.isChecked()
        }


class SegmentationThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, parent, image_input, high_quality):
        super().__init__(parent)
        self.image_input = image_input
        self.high_quality = high_quality
        self.segmentation_engine = parent.segmentation_engine

    def run(self):
        mask = self.segmentation_engine.auto_segment(
            self.image_input, high_quality=self.high_quality)
        self.finished.emit(mask)


class AssemblyExportDialog(QDialog):
    def __init__(self, reed_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assembly Export")
        from PyQt6.QtWidgets import (QComboBox, QDialogButtonBox, QFormLayout,
                                     QSpinBox)
        layout = QFormLayout(self)
        self.spin_seq = QSpinBox()
        self.spin_seq.setValue(1)
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Body", "Full"])
        self.spin_kali = QSpinBox()
        self.spin_kali.setValue(2)
        self.spin_locking = QSpinBox()
        self.spin_locking.setValue(0)

        layout.addRow("Sequence:", self.spin_seq)
        layout.addRow("Type:", self.combo_type)
        layout.addRow("Kali:", self.spin_kali)
        layout.addRow("Locking:", self.spin_locking)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_config(self):
        return (self.spin_seq.value(), self.combo_type.currentText(),
                self.spin_kali.value(), self.spin_locking.value())

    # ==================== AI INTEGRATION METHODS ====================

    def handle_ai_suggestion(self, action: str, data: dict):
        """Handle suggestion actions from AI panel."""
        if action == 'refresh_analysis':
            self.run_ai_analysis()
        elif action == 'adjust_border_width':
            suggested = data.get('suggested_width', 7)
            QMessageBox.information(
                self,
                "Border Adjustment",
                f"Suggested border width: {suggested}cm\n\n"
                "Use the selection and resize tools to adjust your border to this width."
            )
        elif action == 'extend_pallu':
            suggested = data.get('suggested_length', 100)
            QMessageBox.information(
                self,
                "Pallu Extension",
                f"Suggested pallu length: {suggested}cm\n\n"
                "Consider extending your pallu design to comply with traditional proportions."
            )
        elif action == 'apply_color_scheme':
            colors = data.get('colors', [])
            if colors:
                color_text = "\n".join(
                    [f"• {c1} with {c2}" for c1, c2 in colors[:5]])
                QMessageBox.information(
                    self,
                    "Traditional Color Combinations",
                    f"Suggested color pairs:\n{color_text}\n\n"
                    "These combinations follow cultural traditions and are proven to work well."
                )

    def run_ai_analysis(self):
        """Run AI analysis on current image."""
        if self.editor.pixmap is None or self.editor.pixmap.isNull():
            return

        try:
            # Convert QPixmap to numpy array
            image = self.editor.pixmap.toImage()
            width, height = image.width(), image.height()

            # Convert to numpy
            ptr = image.constBits()
            ptr.setsize(height * width * 4)
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

            # Convert RGBA to RGB
            rgb_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

            # Run AI prediction
            prediction = self.ai_model.predict(rgb_image)

            if prediction:
                # Calculate design metrics
                design_metrics = {
                    'width_px': width,
                    'height_px': height,
                    'has_mask': self.current_mask is not None
                }

                # Generate suggestions
                suggestions = self.ai_assistant.analyze_design(
                    prediction, design_metrics)

                # Update UI
                self.ai_insights_panel.update_insights(prediction, suggestions)
                self.ai_last_analysis = prediction

                print("✅ AI Analysis Complete:")
                print(
                    f"   Pattern: {prediction['pattern']['type']} ({prediction['pattern']['confidence']:.1f}%)")
                print(
                    f"   Weave: {prediction['weave']['type']} ({prediction['weave']['confidence']:.1f}%)")
                print(
                    f"   Segmentation: {prediction['segmentation']['confidence']:.1f}% confident")
                print(f"   Suggestions: {len(suggestions)}")

        except Exception as e:
            print(f"AI Analysis Error: {e}")
            import traceback
            traceback.print_exc()

    def auto_analyze_on_load(self):
        """Automatically run AI analysis when image is loaded."""
        # Schedule analysis after a short delay to let UI update
        QTimer.singleShot(500, self.run_ai_analysis)

    def load_generated_design(self, image: np.ndarray):
        """Load a generated design from the generation panel into the editor."""
        print("DEBUG: load_generated_design called")
        try:
            if image is None:
                print("DEBUG: Image is None!")
                return

            # Convert numpy array to QPixmap
            h, w, c = image.shape
            print(f"DEBUG: Processing image shape: {h}x{w}x{c}")
            bytes_per_line = c * w

            # Create QImage from numpy array
            q_img = QImage(
                image.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)

            # Load into editor
            self.editor.load_pixmap(pixmap)

            print(f"✅ Loaded generated design: {w}x{h}")

            # Run AI analysis on the generated design
            self.auto_analyze_on_load()

        except Exception as e:
            print(f"Error loading generated design: {e}")
            import traceback
            traceback.print_exc()

    def show_generation_panel(self):
        """Show the generation panel for text-to-design."""
        if hasattr(self, 'generation_panel'):
            self.generation_panel.show()
            self.generation_panel.raise_()

    def toggle_generation_panel(self):
        """Toggle generation panel visibility."""
        if hasattr(self, 'generation_panel'):
            if self.generation_panel.isVisible():
                self.generation_panel.hide()
            else:
                self.generation_panel.show()
                self.generation_panel.raise_()


# ================== GTK SEGMENT CONFIG DIALOG ==================

class GTKSegmentConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Loom BMP")
        self.resize(400, 300)
        from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialogButtonBox,
                                     QFormLayout)
        layout = QFormLayout(self)

        self.combo_body = QComboBox()
        self.combo_body.addItems(
            ["Satin 1/4 (Standard)", "Twill 2/2", "Plain 1/1"])

        self.combo_border = QComboBox()
        self.combo_border.addItems(
            ["Satin 1/4 (Standard)", "Twill 2/2", "Plain 1/1"])

        self.combo_pallu = QComboBox()
        self.combo_pallu.addItems(["Float (Heavy)", "Satin 1/4", "Plain 1/1"])

        self.chk_palette = QCheckBox("Export as Palette BMP (8-bit)")
        self.chk_palette.setToolTip(
            "Uncheck for Machine-Ready Binary BMP (1-bit)")
        self.chk_palette.setChecked(True)

        layout.addRow("Body Weave (Red):", self.combo_body)
        layout.addRow("Border Weave (Green):", self.combo_border)
        layout.addRow("Pallu Weave (Blue):", self.combo_pallu)
        layout.addRow("", self.chk_palette)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_settings(self):
        return {
            1: self.combo_body.currentIndex(),
            2: self.combo_border.currentIndex(),
            3: self.combo_pallu.currentIndex(),
            'palette': self.chk_palette.isChecked()
        }

    # ==================== AI INTEGRATION METHODS ====================

    def handle_ai_suggestion(self, action: str, data: dict):
        """Handle suggestion actions from AI panel."""
        if action == 'refresh_analysis':
            self.run_ai_analysis()
        elif action == 'adjust_border_width':
            suggested = data.get('suggested_width', 7)
            QMessageBox.information(
                self,
                "Border Adjustment",
                f"Suggested border width: {suggested}cm\n\n"
                "Use the selection and resize tools to adjust your border to this width."
            )
        elif action == 'extend_pallu':
            suggested = data.get('suggested_length', 100)
            QMessageBox.information(
                self,
                "Pallu Extension",
                f"Suggested pallu length: {suggested}cm\n\n"
                "Consider extending your pallu design to comply with traditional proportions."
            )
        elif action == 'apply_color_scheme':
            colors = data.get('colors', [])
            if colors:
                color_text = "\n".join(
                    [f"• {c1} with {c2}" for c1, c2 in colors[:5]])
                QMessageBox.information(
                    self,
                    "Traditional Color Combinations",
                    f"Suggested color pairs:\n{color_text}\n\n"
                    "These combinations follow cultural traditions and are proven to work well."
                )

    def run_ai_analysis(self):
        """Run AI analysis on current image."""
        if self.editor.pixmap is None or self.editor.pixmap.isNull():
            return

        try:
            # Convert QPixmap to numpy array
            image = self.editor.pixmap.toImage()
            width, height = image.width(), image.height()

            # Convert to numpy
            ptr = image.constBits()
            ptr.setsize(height * width * 4)
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

            # Convert RGBA to RGB
            rgb_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

            # Run AI prediction
            prediction = self.ai_model.predict(rgb_image)

            if prediction:
                # Calculate design metrics
                design_metrics = {
                    'width_px': width,
                    'height_px': height,
                    'has_mask': self.current_mask is not None
                }

                # Generate suggestions
                suggestions = self.ai_assistant.analyze_design(
                    prediction, design_metrics)

                # Update UI
                self.ai_insights_panel.update_insights(prediction, suggestions)
                self.ai_last_analysis = prediction

                print("✅ AI Analysis Complete:")
                print(
                    f"   Pattern: {prediction['pattern']['type']} ({prediction['pattern']['confidence']:.1f}%)")
                print(
                    f"   Weave: {prediction['weave']['type']} ({prediction['weave']['confidence']:.1f}%)")
                print(
                    f"   Segmentation: {prediction['segmentation']['confidence']:.1f}% confident")
                print(f"   Suggestions: {len(suggestions)}")

        except Exception as e:
            print(f"AI Analysis Error: {e}")
            import traceback
            traceback.print_exc()

        if action == 'refresh_analysis':
            self.run_ai_analysis()
        elif action == 'adjust_border_width':
            suggested = data.get('suggested_width', 7)
            QMessageBox.information(
                self,
                "Border Adjustment",
                f"Suggested border width: {suggested}cm\n\n"
                "Use the selection and resize tools to adjust your border to this width."
            )
        elif action == 'extend_pallu':
            suggested = data.get('suggested_length', 100)
            QMessageBox.information(
                self,
                "Pallu Extension",
                f"Suggested pallu length: {suggested}cm\n\n"
                "Consider extending your pallu design to comply with traditional proportions."
            )
        elif action == 'apply_color_scheme':
            colors = data.get('colors', [])
            if colors:
                color_text = "\n".join(
                    [f"• {c1} with {c2}" for c1, c2 in colors[:5]])
                QMessageBox.information(
                    self,
                    "Traditional Color Combinations",
                    f"Suggested color pairs:\n{color_text}\n\n"
                    "These combinations follow cultural traditions and are proven to work well."
                )
        else:
            QMessageBox.warning(
                self,
                "AI Suggestion",
                f"Unknown AI action: {action}")

    def auto_analyze_on_load(self):
        """Automatically run AI analysis when image is loaded."""
        # Schedule analysis after a short delay to let UI update
        QTimer.singleShot(500, self.run_ai_analysis)

    def load_generated_design(self, image: np.ndarray):
        """Load a generated design from the generation panel into the editor."""
        try:
            # Convert numpy array to QPixmap
            h, w, c = image.shape
            bytes_per_line = c * w

            # Create QImage from numpy array
            q_img = QImage(
                image.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)

            # Load into editor
            self.editor.load_pixmap(pixmap)

            print(f"✅ Loaded generated design: {w}x{h}")

            # Run AI analysis on the generated design
            self.auto_analyze_on_load()

        except Exception as e:
            print(f"Error loading generated design: {e}")
            import traceback
            traceback.print_exc()

    def show_generation_panel(self):
        """Show the generation panel for text-to-design."""
        if hasattr(self, 'generation_panel'):
            self.generation_panel.show()
            self.generation_panel.raise_()

    def toggle_generation_panel(self):
        """Toggle generation panel visibility."""
        if hasattr(self, 'generation_panel'):
            if self.generation_panel.isVisible():
                self.generation_panel.hide()
            else:
                self.generation_panel.show()
                self.generation_panel.raise_()

# ================== AI GENERATION THREAD ==================


class GenerationThread(QThread):
    finished_signal = pyqtSignal(object)  # Returns vectors/image
    error_signal = pyqtSignal(str)

    def __init__(self, prompt, variations=False):
        super().__init__()
        self.prompt = prompt
        self.variations = variations

    def run(self):
        print("DEBUG: GenerationThread Started")
        try:
            # Fix path for thread context
            import os
            import sys

            # sj_das/ui/designer_view.py -> sj_das/ui -> sj_das -> root
            root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__))))
            if root not in sys.path:
                sys.path.insert(0, root)

            print("DEBUG: Importing GenerativeDesignEngine...")
            from sj_das.core.generative_engine import GenerativeDesignEngine
            engine = GenerativeDesignEngine()

            # Use standard border dims
            w = 480
            h = 120

            print(f"DEBUG: Calling generate_border('{self.prompt}')...")
            if self.variations:
                imgs = engine.generate_variations(self.prompt, w, h, 3)
                final_res = []
                for qimg in imgs:
                    ptr = qimg.bits()
                    ptr.setsize(h * w * 3)
                    arr = np.array(ptr).reshape(h, w, 3)
                    import cv2
                    final_res.append(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
                self.finished_signal.emit(final_res)
            else:
                # Engine generates QImage (internal logic), let's get it back
                qimg = engine.generate_border(self.prompt, w, h)
                print(f"DEBUG: Engine returned qimg: {qimg}")

                if qimg is None:
                    raise RuntimeError("AI returned None (Empty Image)")

                # Convert to numpy in thread - safer to pass numpy array than
                # QImage across threads sometimes
                ptr = qimg.bits()
                ptr.setsize(h * w * 3)
                arr = np.array(ptr).reshape(h, w, 3)
                import cv2

                # Use deep copy to ensure memory ownership is clean
                final_cv = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR).copy()

                print(
                    f"DEBUG: Emitting finished signal with shape {final_cv.shape}")
                self.finished_signal.emit(final_cv)

        except Exception as e:
            print(f"DEBUG: GenerationThread Exception: {e}")
            import traceback
            traceback.print_exc()
            self.error_signal.emit(str(e))

    def _qimage_to_cv2(self, qimg):
        # Helper to convert back
        qimg = qimg.convertToFormat(QImage.Format.Format_RGB888)
        w, h = qimg.width(), qimg.height()
        ptr = qimg.bits()
        ptr.setsize(h * w * 3)
        arr = np.array(ptr).reshape(h, w, 3)
        return arr[..., ::-1].copy()  # RGB->BGR
