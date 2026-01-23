"""Scene Manager for Graphics Item Lifecycle.

Manages QGraphicsScene items with proper lifecycle and performance optimization.
"""

import logging

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene

logger = logging.getLogger(__name__)


class SceneManager:
    """
    Professional scene management with item recycling.

    Prevents C++ object deletion errors by reusing QGraphicsItems
    instead of destroying and recreating them.

    Features:
    - Item recycling for performance
    - Z-order management
   - Automatic bounds calculation
    - Memory efficient

    Attributes:
        scene: The QGraphicsScene being managed
        items: Dictionary of managed items by layer name
    """

    def __init__(self, scene: QGraphicsScene):
        """
        Initialize scene manager.

        Args:
            scene: QGraphicsScene to manage
        """
        self.scene = scene
        self.items: dict[str, QGraphicsPixmapItem] = {}

        logger.debug("Initialized SceneManager")

    def update_layer(
        self,
        layer_name: str,
        image: QImage,
        z_value: int = 0
    ) -> None:
        """
        Update or create a layer with new image.

        Args:
            layer_name: Unique layer identifier
            image: Image to display
            z_value: Z-order (higher = on top)
        """
        pixmap = QPixmap.fromImage(image)

        if layer_name in self.items:
            # Recycle existing item
            item = self.items[layer_name]
            item.setPixmap(pixmap)
            item.setZValue(z_value)
            logger.debug(f"Updated layer: {layer_name}")
        else:
            # Create new item
            item = QGraphicsPixmapItem(pixmap)
            item.setZValue(z_value)
            self.scene.addItem(item)
            self.items[layer_name] = item
            logger.debug(f"Created layer: {layer_name} (z={z_value})")

    def remove_layer(self, layer_name: str) -> None:
        """
        Remove a layer from scene.

        Args:
            layer_name: Layer to remove
        """
        if layer_name in self.items:
            item = self.items[layer_name]
            self.scene.removeItem(item)
            del self.items[layer_name]
            logger.debug(f"Removed layer: {layer_name}")

    def clear_layer(self, layer_name: str) -> None:
        """
        Clear a layer (make transparent).

        Args:
            layer_name: Layer to clear
        """
        if layer_name in self.items:
            item = self.items[layer_name]
            item.setPixmap(QPixmap())  # Empty pixmap
            logger.debug(f"Cleared layer: {layer_name}")

    def get_layer_bounds(self, layer_name: str) -> QRectF | None:
        """
        Get bounding rectangle of a layer.

        Args:
            layer_name: Layer to query

        Returns:
            Bounding rectangle or None if layer doesn't exist
        """
        if layer_name in self.items:
            return self.items[layer_name].boundingRect()
        return None

    def update_scene_rect(self) -> None:
        """Update scene rectangle to fit all items."""
        self.scene.setSceneRect(self.scene.itemsBoundingRect())

    def clear_all(self) -> None:
        """Remove all managed layers."""
        for layer_name in list(self.items.keys()):
            self.remove_layer(layer_name)
        logger.info("Cleared all layers")

    def get_layer_count(self) -> int:
        """Get number of active layers."""
        return len(self.items)

    def layer_exists(self, layer_name: str) -> bool:
        """Check if layer exists."""
        return layer_name in self.items
