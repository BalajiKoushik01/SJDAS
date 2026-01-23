
from typing import TYPE_CHECKING

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage, QPainter, QPixmap, QUndoCommand

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget


class BitmapEditCommand(QUndoCommand):
    """
    Generic Undo/Redo Command for Bitmap changes (BG or Mask).
    Supports dirty rect optimization.
    """

    def __init__(self, editor: 'PixelEditorWidget', before_img: QImage,
                 after_img: QImage, rect: QRect, description: str, layer_type='mask'):
        super().__init__(description)
        self.editor = editor
        self.before_img = before_img
        self.after_img = after_img
        self.rect = rect
        self.layer_type = layer_type

    def redo(self):
        self._apply(self.after_img)
        if self.layer_type == 'mask':
            self.editor.mask_updated.emit()

    def undo(self):
        self._apply(self.before_img)
        if self.layer_type == 'mask':
            self.editor.mask_updated.emit()

    def _apply(self, source_full_img: QImage):
        """Restores state for specific dirty rect."""
        target_img = None
        target_item = None

        if self.layer_type == 'mask':
            target_img = self.editor.mask_image
            target_item = self.editor.mask_item
        elif self.layer_type == 'bg':
            target_img = self.editor.original_image
            target_item = self.editor.image_item

        if target_img is None:
            return

        if self.rect.isNull():
            # Full replacement (Fast Path)
            # But source_full_img is the full image, so we just copy it?
            # Or we assume source_full_img IS the state.
            # Ideally we copy bits.
            painter = QPainter(target_img)
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_Source)
            painter.drawImage(0, 0, source_full_img)
            painter.end()
        else:
            # Dirty Rect Update
            painter = QPainter(target_img)
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_Source)
            painter.drawImage(self.rect, source_full_img, self.rect)
            painter.end()

        # Update View
        if target_item:
            target_item.setPixmap(QPixmap.fromImage(target_img))
