"""
Vector Tools for SJ-DAS.

Photoshop-quality vector tools including Pen Tool, Shape Tools,
and path operations.
"""

import logging
from typing import List, Tuple

import numpy as np
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (QBrush, QColor, QImage, QPainter, QPainterPath, QPen,
                         QPolygonF)

logger = logging.getLogger("SJ_DAS.VectorTools")


class PenTool:
    """
    Photoshop-style Pen Tool for creating bezier paths.

    Features:
        - Create bezier curves
        - Add/delete anchor points
        - Convert to selection
        - Stroke/fill paths
    """

    def __init__(self):
        self.path = QPainterPath()
        self.anchor_points = []
        self.control_points = []

    def create_path(
        self,
        points: List[QPointF],
        handles: List[Tuple[QPointF, QPointF]] = None
    ) -> QPainterPath:
        """
        Create bezier path from points and handles.

        Args:
            points: Anchor points
            handles: Control point pairs for each anchor

        Returns:
            QPainterPath object
        """
        path = QPainterPath()

        if not points:
            return path

        # Start path
        path.moveTo(points[0])

        # Add curves
        for i in range(1, len(points)):
            if handles and i - 1 < len(handles):
                # Cubic bezier
                h1, h2 = handles[i - 1]
                path.cubicTo(h1, h2, points[i])
            else:
                # Straight line
                path.lineTo(points[i])

        self.path = path
        logger.debug(f"Created path with {len(points)} points")
        return path

    def convert_to_selection(self, path: QPainterPath,
                             image_size: Tuple[int, int]) -> np.ndarray:
        """
        Convert path to selection mask.

        Args:
            path: QPainterPath to convert
            image_size: (width, height) of target image

        Returns:
            Selection mask (numpy array)
        """
        w, h = image_size

        # Create image to render path
        image = QImage(w, h, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        # Render path
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, QBrush(Qt.GlobalColor.white))
        painter.end()

        # Convert to numpy mask
        ptr = image.bits()
        ptr.setsize(h * w * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 4))
        mask = arr[:, :, 3]  # Alpha channel

        logger.debug(f"Converted path to selection: {np.sum(mask > 0)} pixels")
        return mask

    def stroke_path(
        self,
        path: QPainterPath,
        image_size: Tuple[int, int],
        pen_width: int = 2,
        color: QColor = QColor(0, 0, 0)
    ) -> np.ndarray:
        """
        Stroke path with specified pen.

        Args:
            path: Path to stroke
            image_size: Image dimensions
            pen_width: Stroke width
            color: Stroke color

        Returns:
            Stroked image (RGBA)
        """
        w, h = image_size

        image = QImage(w, h, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(color, pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        painter.drawPath(path)
        painter.end()

        # Convert to numpy
        ptr = image.bits()
        ptr.setsize(h * w * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 4))

        return arr.copy()

    def fill_path(
        self,
        path: QPainterPath,
        image_size: Tuple[int, int],
        color: QColor = QColor(255, 255, 255)
    ) -> np.ndarray:
        """Fill path with color."""
        w, h = image_size

        image = QImage(w, h, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, QBrush(color))
        painter.end()

        ptr = image.bits()
        ptr.setsize(h * w * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 4))

        return arr.copy()


class ShapeTools:
    """
    Vector shape tools.

    Shapes:
        - Rectangle
        - Rounded Rectangle
        - Ellipse
        - Polygon
        - Star
        - Custom shapes
    """

    @staticmethod
    def draw_rectangle(
        rect: QRectF,
        fill_color: QColor = None,
        stroke_color: QColor = None,
        stroke_width: int = 2
    ) -> QPainterPath:
        """Draw rectangle shape."""
        path = QPainterPath()
        path.addRect(rect)
        return path

    @staticmethod
    def draw_rounded_rectangle(
        rect: QRectF,
        radius: float = 10.0
    ) -> QPainterPath:
        """Draw rounded rectangle."""
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        return path

    @staticmethod
    def draw_ellipse(rect: QRectF) -> QPainterPath:
        """Draw ellipse/circle."""
        path = QPainterPath()
        path.addEllipse(rect)
        return path

    @staticmethod
    def draw_polygon(
        center: QPointF,
        radius: float,
        sides: int = 6
    ) -> QPainterPath:
        """
        Draw regular polygon.

        Args:
            center: Center point
            radius: Radius from center to vertex
            sides: Number of sides (3-100)
        """
        path = QPainterPath()

        points = []
        angle_step = 360.0 / sides

        for i in range(sides):
            angle = np.radians(i * angle_step - 90)  # Start from top
            x = center.x() + radius * np.cos(angle)
            y = center.y() + radius * np.sin(angle)
            points.append(QPointF(x, y))

        polygon = QPolygonF(points)
        path.addPolygon(polygon)
        path.closeSubpath()

        return path

    @staticmethod
    def draw_star(
        center: QPointF,
        outer_radius: float,
        inner_radius: float,
        points: int = 5
    ) -> QPainterPath:
        """
        Draw star shape.

        Args:
            center: Center point
            outer_radius: Outer point radius
            inner_radius: Inner point radius
            points: Number of star points
        """
        path = QPainterPath()

        vertices = []
        angle_step = 360.0 / (points * 2)

        for i in range(points * 2):
            angle = np.radians(i * angle_step - 90)
            radius = outer_radius if i % 2 == 0 else inner_radius

            x = center.x() + radius * np.cos(angle)
            y = center.y() + radius * np.sin(angle)
            vertices.append(QPointF(x, y))

        polygon = QPolygonF(vertices)
        path.addPolygon(polygon)
        path.closeSubpath()

        return path

    @staticmethod
    def draw_triangle(
        center: QPointF,
        radius: float,
        rotation: float = 0.0
    ) -> QPainterPath:
        """Draw triangle."""
        return ShapeTools.draw_polygon(center, radius, 3)

    @staticmethod
    def draw_hexagon(
        center: QPointF,
        radius: float
    ) -> QPainterPath:
        """Draw hexagon."""
        return ShapeTools.draw_polygon(center, radius, 6)

    @staticmethod
    def render_shape(
        path: QPainterPath,
        image_size: Tuple[int, int],
        fill_color: QColor = None,
        stroke_color: QColor = None,
        stroke_width: int = 2
    ) -> np.ndarray:
        """
        Render shape to image.

        Args:
            path: Shape path
            image_size: (width, height)
            fill_color: Fill color (None for no fill)
            stroke_color: Stroke color (None for no stroke)
            stroke_width: Stroke width in pixels

        Returns:
            RGBA image array
        """
        w, h = image_size

        image = QImage(w, h, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fill
        if fill_color:
            painter.fillPath(path, QBrush(fill_color))

        # Stroke
        if stroke_color:
            pen = QPen(stroke_color, stroke_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

        painter.end()

        # Convert to numpy
        ptr = image.bits()
        ptr.setsize(h * w * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((h, w, 4))

        logger.debug(f"Rendered shape to {w}x{h} image")
        return arr.copy()


class PathOperations:
    """
    Path boolean operations.

    Operations:
        - Union (combine paths)
        - Subtract (cut out)
        - Intersect (overlap only)
        - Exclude (non-overlapping)
    """

    @staticmethod
    def union(path1: QPainterPath, path2: QPainterPath) -> QPainterPath:
        """Combine two paths (OR operation)."""
        return path1.united(path2)

    @staticmethod
    def subtract(path1: QPainterPath, path2: QPainterPath) -> QPainterPath:
        """Subtract path2 from path1."""
        return path1.subtracted(path2)

    @staticmethod
    def intersect(path1: QPainterPath, path2: QPainterPath) -> QPainterPath:
        """Get intersection of two paths (AND operation)."""
        return path1.intersected(path2)

    @staticmethod
    def exclude(path1: QPainterPath, path2: QPainterPath) -> QPainterPath:
        """Get non-overlapping parts (XOR operation)."""
        # XOR = (A OR B) - (A AND B)
        union = path1.united(path2)
        intersection = path1.intersected(path2)
        return union.subtracted(intersection)
