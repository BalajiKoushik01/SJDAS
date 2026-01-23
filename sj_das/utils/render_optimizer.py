"""
Canvas Rendering Optimization for SJ-DAS
Implements viewport culling, progressive rendering, and tile caching
"""
from typing import List, Optional, Set, Tuple

import numpy as np
from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QImage, QPainter

from sj_das.utils.enhanced_logger import get_logger

logger = get_logger(__name__)


class RenderOptimizer:
    """
    Optimizes canvas rendering for large images.

    Features:
    - Viewport culling (only render visible area)
    - Dirty rectangle tracking
    - Tile-based caching
    - Progressive rendering
    """

    def __init__(self, tile_size: int = 256):
        """
        Initialize render optimizer.

        Args:
            tile_size: Size of tiles for caching (default 256x256)
        """
        self.tile_size = tile_size
        self.tile_cache = {}
        self.dirty_tiles: Set[Tuple[int, int]] = set()

        logger.info(f"RenderOptimizer initialized (tile_size={tile_size})")

    def get_visible_tiles(
        self,
        viewport: QRect,
        image_size: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Get tiles that are visible in viewport.

        Args:
            viewport: Visible area (x, y, width, height)
            image_size: Full image size (width, height)

        Returns:
            List of tile coordinates [(tx, ty), ...]
        """
        vx, vy = viewport.x(), viewport.y()
        vw, vh = viewport.width(), viewport.height()
        img_w, img_h = image_size

        # Calculate tile range
        start_tx = max(0, vx // self.tile_size)
        start_ty = max(0, vy // self.tile_size)
        end_tx = min(
            (vx + vw) // self.tile_size + 1,
            (img_w // self.tile_size) + 1)
        end_ty = min(
            (vy + vh) // self.tile_size + 1,
            (img_h // self.tile_size) + 1)

        tiles = []
        for tx in range(start_tx, end_tx):
            for ty in range(start_ty, end_ty):
                tiles.append((tx, ty))

        logger.debug(
            f"Visible tiles: {len(tiles)} out of {((img_w//self.tile_size)+1)*((img_h//self.tile_size)+1)}")
        return tiles

    def mark_dirty(self, x: int, y: int, w: int, h: int):
        """
        Mark region as needing redraw.

        Args:
            x, y: Top-left corner
            w, h: Width and height
        """
        # Calculate affected tiles
        start_tx = x // self.tile_size
        start_ty = y // self.tile_size
        end_tx = (x + w) // self.tile_size + 1
        end_ty = (y + h) // self.tile_size + 1

        for tx in range(start_tx, end_tx):
            for ty in range(start_ty, end_ty):
                self.dirty_tiles.add((tx, ty))
                # Invalidate cache for dirty tiles
                if (tx, ty) in self.tile_cache:
                    del self.tile_cache[(tx, ty)]

        logger.debug(f"Marked {len(self.dirty_tiles)} tiles as dirty")

    def get_tile_bounds(
        self,
        tx: int,
        ty: int,
        image_size: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Get pixel bounds for a tile.

        Args:
            tx, ty: Tile coordinates
            image_size: Full image size

        Returns:
            (x, y, width, height) in pixels
        """
        img_w, img_h = image_size

        x = tx * self.tile_size
        y = ty * self.tile_size
        w = min(self.tile_size, img_w - x)
        h = min(self.tile_size, img_h - y)

        return (x, y, w, h)

    def cache_tile(self, tx: int, ty: int, tile_image: QImage):
        """
        Cache rendered tile.

        Args:
            tx, ty: Tile coordinates
            tile_image: Rendered tile image
        """
        self.tile_cache[(tx, ty)] = tile_image

        # Remove from dirty set
        if (tx, ty) in self.dirty_tiles:
            self.dirty_tiles.remove((tx, ty))

    def get_cached_tile(self, tx: int, ty: int) -> Optional[QImage]:
        """
        Get cached tile if available.

        Args:
            tx, ty: Tile coordinates

        Returns:
            Cached tile image or None
        """
        return self.tile_cache.get((tx, ty))

    def clear_cache(self):
        """Clear all cached tiles."""
        self.tile_cache.clear()
        self.dirty_tiles.clear()
        logger.info("Tile cache cleared")

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache metrics
        """
        return {
            'cached_tiles': len(self.tile_cache),
            'dirty_tiles': len(self.dirty_tiles),
            'tile_size': self.tile_size,
            'cache_memory_mb': len(self.tile_cache) * (self.tile_size * self.tile_size * 4) / 1024 / 1024
        }


class ProgressiveRenderer:
    """
    Renders large images progressively.

    Features:
    - Multi-pass rendering (low to high quality)
    - Interruptible rendering
    - Quality levels
    """

    def __init__(self):
        """Initialize progressive renderer."""
        self.rendering = False
        self.cancelled = False
        logger.info("ProgressiveRenderer initialized")

    def render_progressive(
        self,
        image: np.ndarray,
        target_size: Tuple[int, int],
        quality_levels: int = 3
    ) -> List[QImage]:
        """
        Render image progressively at multiple quality levels.

        Args:
            image: Source image (numpy array)
            target_size: Target display size
            quality_levels: Number of quality passes

        Returns:
            List of QImage at increasing quality
        """
        self.rendering = True
        self.cancelled = False

        results = []
        h, w = image.shape[:2]
        target_w, target_h = target_size

        for level in range(quality_levels):
            if self.cancelled:
                break

            # Calculate scale for this level
            scale = (level + 1) / quality_levels

            # Render at this quality
            scaled_w = int(target_w * scale)
            scaled_h = int(target_h * scale)

            # Simple downscaling (in production, use better interpolation)
            import cv2
            scaled = cv2.resize(image, (scaled_w, scaled_h),
                                interpolation=cv2.INTER_LINEAR)

            # Convert to QImage
            if len(scaled.shape) == 3:
                h, w, ch = scaled.shape
                bytes_per_line = ch * w
                qimg = QImage(
                    scaled.data,
                    w,
                    h,
                    bytes_per_line,
                    QImage.Format.Format_RGB888)
            else:
                h, w = scaled.shape
                qimg = QImage(
                    scaled.data, w, h, w, QImage.Format.Format_Grayscale8)

            results.append(qimg.copy())
            logger.debug(
                f"Progressive render level {level+1}/{quality_levels}: {scaled_w}x{scaled_h}")

        self.rendering = False
        return results

    def cancel(self):
        """Cancel ongoing progressive rendering."""
        self.cancelled = True
        logger.info("Progressive rendering cancelled")


# Global instances
_render_optimizer: Optional[RenderOptimizer] = None
_progressive_renderer: Optional[ProgressiveRenderer] = None


def get_render_optimizer(tile_size: int = 256) -> RenderOptimizer:
    """
    Get global render optimizer instance.

    Args:
        tile_size: Tile size (only used on first call)

    Returns:
        Global RenderOptimizer instance
    """
    global _render_optimizer
    if _render_optimizer is None:
        _render_optimizer = RenderOptimizer(tile_size)
    return _render_optimizer


def get_progressive_renderer() -> ProgressiveRenderer:
    """
    Get global progressive renderer instance.

    Returns:
        Global ProgressiveRenderer instance
    """
    global _progressive_renderer
    if _progressive_renderer is None:
        _progressive_renderer = ProgressiveRenderer()
    return _progressive_renderer
