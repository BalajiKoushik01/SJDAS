
import logging
import os
import shutil
from typing import TYPE_CHECKING, Optional

from PyQt6.QtCore import QObject, Qt, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget
    from sj_das.ui.modern_designer_view import PremiumDesignerView

logger = logging.getLogger("SJ_DAS.CanvasController")


class CanvasController(QObject):
    """
    Controller for Canvas Operations (MVC Pattern).
    Handles business logic for File I/O, Clipboard, and View manipulations.
    """

    def __init__(self, view: 'PremiumDesignerView'):
        super().__init__()
        self.view = view
        self._editor: Optional['PixelEditorWidget'] = getattr(
            view, 'editor', None)

        # IoC Injection
        from sj_das.core.feature_flags import FeatureFlagManager
        from sj_das.core.ioc_container import ServiceContainer

        self.container = ServiceContainer.instance()
        try:
            self.features = self.container.resolve(FeatureFlagManager)
        except BaseException:
            # Fallback if not registered (e.g. unit tests without bootstrap)
            self.features = FeatureFlagManager.instance()

        if not self._editor:
            logger.error(
                "CanvasController initialized without a valid editor widget.")

    def toggle_voice_control(self):
        """Toggle AI Voice Control (Feature Flagged)."""
        if self.features.is_enabled("AI_VOICE_COMMANDS"):
            self.view.show_notification(
                "Listening for commands... (Simulated)")
            logger.info("Voice Control Activated")
        else:
            self.view.show_notification(
                "Voice Control is disabled via Feature Flags.", duration=3000)
            logger.info("Voice Control blocked by Feature Flag")

    @property
    def editor(self) -> 'PixelEditorWidget':
        """Safe access to editor widget."""
        if not self._editor:
            raise ValueError("Editor widget not initialized")
        return self._editor

    # ==================== FILE OPERATIONS ====================

    def new_canvas(self, width: int = 2400, height: int = 3000) -> None:
        """Create a new blank canvas."""
        from PyQt6.QtGui import QImage, QPixmap

        try:
            blank = QImage(width, height, QImage.Format.Format_RGB888)
            blank.fill(Qt.GlobalColor.white)

            if hasattr(self.editor, 'set_pixmap'):
                self.editor.set_pixmap(QPixmap.fromImage(blank))
            elif hasattr(self.editor, 'setPixmap'):
                self.editor.setPixmap(QPixmap.fromImage(blank))

            self.view.current_image_path = None
            self.view.show_notification(
                f"New canvas created: {width}x{height}")
            logger.info(f"Created new canvas: {width}x{height}")
        except Exception as e:
            self.view.show_error(f"Failed to create canvas: {e}")

    def save_file(self, file_path: Optional[str] = None) -> None:
        """Save current canvas to file."""
        if not file_path:
            self.save_file_as()
            return

        try:
            if hasattr(self.editor, 'pixmap') and self.editor.pixmap:
                success = self.editor.pixmap.save(file_path)
                if success:
                    self.view.show_notification(
                        f"Saved: {os.path.basename(file_path)}")
                    logger.info(f"Saved file to: {file_path}")
                else:
                    self.view.show_error(f"Failed to save: {file_path}")
            else:
                self.view.show_error("No image to save")
        except Exception as e:
            self.view.show_error(f"Save error: {e}")
            logger.error(f"Save error: {e}", exc_info=True)

    def save_file_as(self) -> None:
        """Prompt user for filename and save."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Save Design",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp);;All Files (*.*)"
        )

        if file_path:
            self.save_file(file_path)
            self.view.current_image_path = file_path

    # ==================== CLIPBOARD OPERATIONS ====================

    def cut(self) -> None:
        """Cut selection to clipboard."""
        if hasattr(self.editor, 'cut_selection'):
            self.editor.cut_selection()
            self.view.show_notification("Cut to Clipboard")
        else:
            logger.warning("Editor missing cut_selection method")

    def copy(self) -> None:
        """Copy selection to clipboard."""
        if hasattr(self.editor, 'copy_selection'):
            self.editor.copy_selection()
            self.view.show_notification("Copied to Clipboard")
        else:
            logger.warning("Editor missing copy_selection method")

    def paste(self) -> None:
        """Paste from clipboard."""
        # Clean this up to use unified method if possible
        if hasattr(self.editor, 'paste_from_clipboard'):
            self.editor.paste_from_clipboard()
        elif hasattr(self.editor, 'paste_selection'):
            self.editor.paste_selection()
        else:
            logger.warning("Editor missing paste methods")
            return

        self.view.show_notification("Pasted from Clipboard")

    # ==================== PRODUCTION FEATURES (Phase 11) ====================

    def generate_tech_sheet(self):
        """Generate HTML Tech Sheet for manufacturing."""
        if not self.editor.pixmap:
            self.view.show_error("No design to process.")
            return

        from sj_das.core.reporting.tech_sheet_generator import \
            TechSheetGenerator

        # 1. Get Save Path
        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Export Tech Sheet", "tech_sheet.html", "HTML Files (*.html)"
        )
        if not file_path:
            return

        # 2. Extract Data (Simulated for proto)
        # In real app, we'd get yarn data from TextileService or editor
        # metadata
        img = self.editor.get_image_data()  # Ensure we implemented this helper

        # Basic palette extraction
        unique_colors = np.unique(img.reshape(-1, img.shape[2]), axis=0)
        # Limit to top 10 for sheet
        palette = [tuple(c) for c in unique_colors[:10]]

        metadata = {
            "name": "Saree Design Master",
            "designer": "Studio User",
            "hooks": 2400,
            "picks": 4800,
            "width": img.shape[1],
            "height": img.shape[0],
            "palette": palette
        }

        # 3. Generate
        generator = TechSheetGenerator()
        success = generator.generate_report(img, metadata, file_path)

        if success:
            self.view.show_notification(f"Tech Sheet Generated: {file_path}")
            # Optional: Open in browser
            import webbrowser
            webbrowser.open(f"file://{file_path}")

    def open_tiling_tool(self):
        """Open Pattern Tiling Dialog."""
        if not self.editor.pixmap:
            self.view.show_error("No design to tile.")
            return

        from sj_das.ui.dialogs.pattern_tiling_dialog import PatternTilingDialog

        # Get current image
        img = self.editor.get_image_data()

        dlg = PatternTilingDialog(img, self.view)
        if dlg.exec():
            # Apply result
            result = dlg.get_result()
            from PyQt6.QtGui import QImage, QPixmap

            h, w, ch = result.shape
            bytes_per_line = ch * w
            rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, bytes_per_line,
                          QImage.Format.Format_RGB888)

            if hasattr(self.editor, 'set_pixmap'):
                self.editor.set_pixmap(QPixmap.fromImage(qimg))
            elif hasattr(self.editor, 'setPixmap'):
                self.editor.setPixmap(QPixmap.fromImage(qimg))

            self.view.show_notification("Pattern Tiled Successfully")

            self.view.show_notification("Pattern Tiled Successfully")

    # ==================== AI OPERATIONS (Phase 12) ====================

    def start_upscaling(self):
        """Trigger 4x Upscale."""
        if not self.editor.pixmap:
            return

        from sj_das.core.services.ai_service import AIService
        img = self.editor.get_image_data()

        # Connect result handler dynamically
        service = AIService.instance()
        service.generation_completed.disconnect()  # Safety clear
        service.generation_completed.connect(self._on_upscale_complete)

        service.upscale_image(img, scale=4)

    def _on_upscale_complete(self, result):
        """Handle upscale callback."""
        if isinstance(result, np.ndarray):
            from PyQt6.QtGui import QImage, QPixmap
            # ... convert to pixmap ... (Using helper would be nice, but redundant logic exists in Tiling)
            h, w, ch = result.shape
            bytes_per_line = ch * w
            rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, bytes_per_line,
                          QImage.Format.Format_RGB888)

            if hasattr(self.editor, 'set_pixmap'):
                self.editor.set_pixmap(QPixmap.fromImage(qimg))
            elif hasattr(self.editor, 'setPixmap'):
                self.editor.setPixmap(QPixmap.fromImage(qimg))

            self.view.show_notification(f"Upscale Complete: {w}x{h}")

    def activate_magic_wand(self):
        """Prepare SAM embedding."""
        if not self.editor.pixmap:
            return

        # Tell view to switch cursor/mode
        self.view.show_notification(
            "Initializing Magic Wand (AI)... please wait.")

        from sj_das.core.services.ai_service import AIService
        img = self.editor.get_image_data()
        AIService.instance().prepare_magic_wand(img)

    def handle_magic_wand_click(self, x: int, y: int):
        """Process click for valid segmentation."""
        from sj_das.core.services.ai_service import AIService
        mask = AIService.instance().get_magic_wand_mask(x, y)

        if mask is not None:
            # Send mask to editor for selection
            if hasattr(self.editor, 'set_selection_from_mask'):
                self.editor.set_selection_from_mask(mask)
                logger.info(f"Magic Wand selection at {x},{y}")
            else:
                logger.warning("Editor missing set_selection_from_mask")

    # ==================== VIEW OPERATIONS ====================

    def zoom_in(self) -> None:
        """Zoom in on the canvas."""
        if hasattr(self.editor, 'zoom_in'):
            self.editor.zoom_in()

    def zoom_out(self) -> None:
        """Zoom out on the canvas."""
        if hasattr(self.editor, 'zoom_out'):
            self.editor.zoom_out()

    def zoom_fit(self) -> None:
        """Fit canvas to view."""
        if hasattr(self.editor, 'zoom_fit'):
            self.editor.zoom_fit()

    def zoom_actual(self) -> None:
        """Zoom to 100%."""
        if hasattr(self.editor, 'zoom_actual'):
            self.editor.zoom_actual()
