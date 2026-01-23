
"""
Symmetry Engine for SJ-DAS.
Handles coordinate mirroring and visual guides.
"""
import enum

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import QGraphicsLineItem


class SymmetryMode(enum.Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2
    QUAD = 3
    RADIAL = 4


class SymmetryManager:
    """Manages symmetry calculations and visual guides."""

    def __init__(self, editor):
        self.editor = editor
        self.mode = SymmetryMode.NONE
        self.radial_segments = 6
        self.guides = []

        # Guide Appearance
        self.guide_pen = QPen(QColor(0, 120, 215, 180),
                              1, Qt.PenStyle.DashLine)
        self.guide_pen.setCosmetic(True)

    def set_mode(self, mode_name):
        """Set symmetry mode by name string."""
        mode_map = {
            "none": SymmetryMode.NONE,
            "horizontal": SymmetryMode.HORIZONTAL,
            "vertical": SymmetryMode.VERTICAL,
            "quad": SymmetryMode.QUAD,
            "radial": SymmetryMode.RADIAL
        }
        self.mode = mode_map.get(mode_name.lower(), SymmetryMode.NONE)
        self.update_guides()

    def get_mirrored_points(self, point: QPointF) -> list[QPointF]:
        """Return list of all mirrored points including original."""
        if self.mode == SymmetryMode.NONE:
            return [point]

        points = [point]
        w = self.editor.original_image.width()
        h = self.editor.original_image.height()
        cx = w / 2
        cy = h / 2

        x = point.x()
        y = point.y()

        if self.mode == SymmetryMode.HORIZONTAL:
            # Mirror across X axis (Left/Right)
            # Distance from center X
            dx = x - cx
            points.append(QPointF(cx - dx, y))

        elif self.mode == SymmetryMode.VERTICAL:
            # Mirror across Y axis (Top/Bottom)
            dy = y - cy
            points.append(QPointF(x, cy - dy))

        elif self.mode == SymmetryMode.QUAD:
            # Mirror both
            dx = x - cx
            dy = y - cy
            p2 = QPointF(cx - dx, y)
            p3 = QPointF(x, cy - dy)
            p4 = QPointF(cx - dx, cy - dy)
            points.extend([p2, p3, p4])

        elif self.mode == SymmetryMode.RADIAL:
            # Simple 4-way radial for now (Quad diagonal?)
            # No, classic mandala style requires rotation matrix.
            # Keeping it simple for "Industry Standard" start:
            # mirroring across diagonals + quad.

            # Let's do 8-way symmetry (Kaleidoscope)
            # 1. Quad
            dx = x - cx
            dy = y - cy

            # Quad Points
            q1 = QPointF(cx + dx, cy + dy)  # Orig
            q2 = QPointF(cx - dx, cy + dy)
            q3 = QPointF(cx + dx, cy - dy)
            q4 = QPointF(cx - dx, cy - dy)

            # Diagonal Points (Swap dx/dy)
            d1 = QPointF(cx + dy, cy + dx)
            d2 = QPointF(cx - dy, cy + dx)
            d3 = QPointF(cx + dy, cy - dx)
            d4 = QPointF(cx - dy, cy - dx)

            # Use set to dedup center?
            # List is faster.
            return [q1, q2, q3, q4, d1, d2, d3, d4]

        return points

    def update_guides(self):
        """Draw guide lines on the editor scene."""
        # Clear old guides
        for item in self.guides:
            if item.scene():
                self.editor.scene.removeItem(item)
        self.guides.clear()

        if self.mode == SymmetryMode.NONE:
            return

        w = self.editor.original_image.width()
        h = self.editor.original_image.height()
        cx = w / 2
        cy = h / 2

        # Add Lines
        lines = []

        if self.mode in [SymmetryMode.HORIZONTAL,
                         SymmetryMode.QUAD, SymmetryMode.RADIAL]:
            # Vertical Line (Mid point X)
            lines.append(((cx, 0), (cx, h)))

        if self.mode in [SymmetryMode.VERTICAL,
                         SymmetryMode.QUAD, SymmetryMode.RADIAL]:
            # Horizontal Line (Mid point Y)
            lines.append(((0, cy), (w, cy)))

        if self.mode == SymmetryMode.RADIAL:
            # Diagonals
            # 1. TopLeft to BotRight
            # 2. TopRight to BotLeft
            # Keep it simple: Just draw large cross for now for 8-way
            # Proper diagonal relies on aspect ratio
            # Assuming square for diagonals to line up perfectly in perception,
            # but math works regardless.
            lines.append(((0, 0), (w, h)))
            lines.append(((w, 0), (0, h)))

        for start, end in lines:
            line_item = QGraphicsLineItem(start[0], start[1], end[0], end[1])
            line_item.setPen(self.guide_pen)
            line_item.setZValue(500)  # Above image/mask, below cursor
            self.editor.scene.addItem(line_item)
            self.guides.append(line_item)
