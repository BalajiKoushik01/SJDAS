from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class NavigatorWidget(QWidget):
    """
    Mini-map for navigating the editor view.
    """

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.editor.scene.changed.connect(
            self.update_view)  # Trigger on scene change
        # Also need to trigger on viewport move (scroll)
        self.editor.verticalScrollBar().valueChanged.connect(self.update_view)
        self.editor.horizontalScrollBar().valueChanged.connect(self.update_view)

        self.setFixedSize(200, 200)  # Fixed size for now
        self.preview_pixmap = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        if hasattr(self.editor, 'mask_image') and self.editor.mask_image:
            # Draw scaled preview
            # We cache this ideally, but for now just scale on fly (cheap for 200px)
            # Actually, better to use cached pixmap if mask doesn't change often.
            # But mask changes on every draw.
            scaled = self.editor.mask_image.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation)

            # Center it
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawImage(x, y, scaled)

            # Draw Viewport Rect
            # Map viewport rect to scene rect, then to navigator rect
            view_rect = self.editor.mapToScene(
                self.editor.viewport().rect()).boundingRect()
            scene_rect = self.editor.sceneRect()

            if scene_rect.width() > 0 and scene_rect.height() > 0:
                scale_x = scaled.width() / scene_rect.width()
                scale_y = scaled.height() / scene_rect.height()

                # Navigator rect relative to the image
                nav_x = x + (view_rect.x() - scene_rect.x()) * scale_x
                nav_y = y + (view_rect.y() - scene_rect.y()) * scale_y
                nav_w = view_rect.width() * scale_x
                nav_h = view_rect.height() * scale_y

                painter.setPen(QPen(Qt.GlobalColor.red, 2))
                painter.drawRect(QRectF(nav_x, nav_y, nav_w, nav_h))

    def update_view(self):
        self.update()

    def mousePressEvent(self, event):
        """Allow clicking to jump to position."""
        try:
            if self.editor.mask_image and event.button() == Qt.MouseButton.LeftButton:
                # Get click position
                click_x = event.pos().x()
                click_y = event.pos().y()

                # Get scaled image dimensions
                scaled = self.editor.mask_image.scaled(
                    self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation
                )

                # Calculate image offset (centered)
                x_offset = (self.width() - scaled.width()) // 2
                y_offset = (self.height() - scaled.height()) // 2

                # Convert click to scene coordinates
                scene_rect = self.editor.sceneRect()
                if scene_rect.width() > 0 and scene_rect.height() > 0:
                    scale_x = scene_rect.width() / scaled.width()
                    scale_y = scene_rect.height() / scaled.height()

                    scene_x = (click_x - x_offset) * scale_x + scene_rect.x()
                    scene_y = (click_y - y_offset) * scale_y + scene_rect.y()

                    # Center view on clicked position
                    self.editor.centerOn(scene_x, scene_y)

        except Exception as e:
            import logging
            logging.getLogger("SJ_DAS").error(
                f"Navigator jump failed: {e}", exc_info=True)
