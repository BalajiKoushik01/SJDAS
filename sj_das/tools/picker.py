from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QToolTip

from .base import Tool


class PickerTool(Tool):
    """
    Eyedropper / Color Picker with Live Preview.
    """

    def mouse_press(self, pos, buttons):
        self.editor._pick_color(pos)

    def mouse_move(self, pos, buttons):
        # Show Color Info
        x, y = int(pos.x()), int(pos.y())
        if self.editor.original_image and self.editor.original_image.valid(
                x, y):
            c = self.editor.original_image.pixelColor(x, y)
            info = f"RGB: {c.red()}, {c.green()}, {c.blue()}\nHex: {c.name()}"
            QToolTip.showText(QCursor.pos(), info, self.editor)

    def mouse_release(self, pos, buttons):
        QToolTip.hideText()
