"""
Professional Ruler Widget for SJ-DAS.
Syncs with QGraphicsView/QOpenGLWidget to provide accurate pixel measurements.
"""

from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class RulerWidget(QWidget):
    """
    Ruler widget capable of Horizontal or Vertical orientation.
    Syncs with a QGraphicsView to display scene coordinates.
    """

    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, orientation=HORIZONTAL, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.view = None  # The QGraphicsView we are tracking
        self.cursor_pos = 0  # Current mouse position in ruler coords

        # Styles
        self.bg_color = QColor(40, 40, 40)
        self.tick_color = QColor(180, 180, 180)
        self.text_color = QColor(200, 200, 200)
        # Red line for mouse tracker
        self.marker_color = QColor(255, 0, 0, 150)

        # Settings
        self.ruler_width = 25  # Thickness
        if orientation == self.HORIZONTAL:
            self.setFixedHeight(self.ruler_width)
        else:
            self.setFixedWidth(self.ruler_width)

        self.font = QFont("Segoe UI", 8)

    def set_view(self, view):
        """Bind to a QGraphicsView."""
        self.view = view
        # We need to repaint when view scrolls/zooms
        # There's no direct signal for scroll/zoom in QGraphicsView usually,
        # but the viewport updates.
        if hasattr(self.view, 'verticalScrollBar'):
            self.view.verticalScrollBar().valueChanged.connect(self.update)
        if hasattr(self.view, 'horizontalScrollBar'):
            self.view.horizontalScrollBar().valueChanged.connect(self.update)

    def update_cursor_pos(self, pos):
        """Update cursor tracking position (in global coords)."""
        # Convert global/widget pos to ruler pos
        if not self.view:
            return

        # This is tricky because pos is usually local to editor
        # Simplification: pass just the relevant coordinate
        self.cursor_pos = pos
        self.update()

    def paintEvent(self, event):
        if not self.view:
            return

        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)
        painter.setPen(QPen(self.tick_color, 1))
        painter.setFont(self.font)

        # Get Viewport status
        # We need mapFromScene logic but reverse.
        # Visible Scene Rect
        viewport_rect = self.view.viewport().rect()
        scene_tl = self.view.mapToScene(viewport_rect.topLeft())
        # scene_br = self.view.mapToScene(viewport_rect.bottomRight())

        # Transform (Zoom)
        transform = self.view.transform()
        scale = transform.m11()  # Horizontal scale (assume isotropic)

        # Start coordinate (Scene coord at top-left of viewport)
        start_scene = scene_tl.x() if self.orientation == self.HORIZONTAL else scene_tl.y()

        # Calculate Step size (in Scene Pixels) based on Zoom
        # Ideally we want ticks every 10, 50, 100 screen pixels
        # 1 tick = X scene pixels

        screen_step = 100  # pixels on screen between big ticks
        scene_step = screen_step / scale

        # Round to nice number (10, 50, 100, 500)
        steps = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
        step_size = steps[0]
        for s in steps:
            if scene_step < s:
                break
            step_size = s

        # Draw Ticks
        # Iterate visible range
        # Ruler length (screen)
        length = self.width() if self.orientation == self.HORIZONTAL else self.height()

        # scene units visible length
        scene_len = length / scale

        # First tick
        start_tick = (start_scene // step_size) * step_size
        end_tick = start_scene + scene_len

        curr = start_tick
        while curr < end_tick + step_size:
            # Determine screen position of this tick
            # (SceneCoord - StartSceneCoord) * Scale
            delta = curr - start_scene
            screen_pos = delta * scale

            # Draw
            label = f"{int(curr)}"

            if self.orientation == self.HORIZONTAL:
                x = int(screen_pos)
                if x >= -50 and x < length + 50:
                    painter.drawLine(x, 0, x, 10)  # Big tick
                    painter.drawText(x + 2, 20, label)

                    # Subticks (Halves)
                    mid_x = int(x + (step_size / 2) * scale)
                    painter.drawLine(mid_x, 0, mid_x, 6)
            else:
                y = int(screen_pos)
                if y >= -50 and y < length + 50:
                    painter.drawLine(0, y, 10, y)  # Big tick

                    # Vertical text is hard, draw rotated or just simple
                    painter.save()
                    painter.translate(12, y + 8)
                    # painter.rotate(90)
                    painter.drawText(0, 0, label)
                    painter.restore()

                    # Subticks
                    mid_y = int(y + (step_size / 2) * scale)
                    painter.drawLine(0, mid_y, 6, mid_y)

            curr += step_size

        # Draw Mouse Marker
        # cursor_pos is assumed to be screen pixel relative to widget start?
        # Ideally, cursor_pos is passed as view-relative coord
        # Ruler is static relative to viewport usually.
        if self.cursor_pos > 0:
            painter.setPen(QPen(self.marker_color, 1))
            if self.orientation == self.HORIZONTAL:
                painter.drawLine(
                    self.cursor_pos,
                    0,
                    self.cursor_pos,
                    self.height())
            else:
                painter.drawLine(
                    0,
                    self.cursor_pos,
                    self.width(),
                    self.cursor_pos)
