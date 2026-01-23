"""Textile-specific methods for DesignerView class.

These methods should be added to the DesignerView class in designer_view.py
before the class ends (before line ~1028 where LoomExportDialog starts).
"""


def detect_pattern_from_image(self):
    """Detect and extract pattern from any image (Google, photos, etc.)."""
    import numpy as np
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (QApplication, QFileDialog, QInputDialog,
                                 QMessageBox)

    from sj_das.core.pattern_detection import PatternDetectionEngine

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
        pattern_graph, info = pattern_engine.extract_from_url(path, yarn_count)

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
    from PyQt6.QtWidgets import QDialog, QMessageBox

    from sj_das.ui.dialogs.card_sequence_dialog import CardSequenceDialog

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
