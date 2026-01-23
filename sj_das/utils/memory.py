"""
Memory management utilities for SJ-DAS.

Provides tools for tracking and managing memory usage,
preventing memory leaks, and optimizing resource usage.
"""

import gc
import logging
from typing import Any

import psutil
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

logger = logging.getLogger("SJ_DAS.MemoryManager")


class MemoryManager(QObject):
    """
    Manages application memory usage.

    Features:
        - Memory usage tracking
        - Automatic cleanup
        - Memory leak detection
        - Resource pooling
    """

    memory_warning = pyqtSignal(int)  # Emits MB used
    memory_critical = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.process = psutil.Process()
        self._image_cache = {}
        self._max_cache_size = 10

    def get_memory_usage_mb(self) -> int:
        """Get current memory usage in MB."""
        try:
            mem_info = self.process.memory_info()
            return mem_info.rss // (1024 * 1024)
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0

    def check_memory_status(self) -> str:
        """
        Check memory status.

        Returns:
            'ok', 'warning', or 'critical'
        """
        mb_used = self.get_memory_usage_mb()

        if mb_used > 2048:  # 2GB
            self.memory_critical.emit(mb_used)
            return 'critical'
        elif mb_used > 1536:  # 1.5GB
            self.memory_warning.emit(mb_used)
            return 'warning'

        return 'ok'

    def cleanup_image(self, image: QImage | None) -> None:
        """
        Safely cleanup QImage.

        Args:
            image: QImage to cleanup
        """
        if image is not None:
            try:
                # Force deletion
                del image
            except Exception as e:
                logger.warning(f"Error cleaning up image: {e}")

    def cleanup_pixmap(self, pixmap: QPixmap | None) -> None:
        """
        Safely cleanup QPixmap.

        Args:
            pixmap: QPixmap to cleanup
        """
        if pixmap is not None:
            try:
                del pixmap
            except Exception as e:
                logger.warning(f"Error cleaning up pixmap: {e}")

    def force_garbage_collection(self) -> int:
        """
        Force garbage collection.

        Returns:
            Number of objects collected
        """
        collected = gc.collect()
        logger.debug(f"Garbage collection: {collected} objects collected")
        return collected

    def cache_image(self, key: str, image: QImage) -> None:
        """
        Cache an image with automatic size management.

        Args:
            key: Cache key
            image: Image to cache
        """
        # Remove oldest if cache full
        if len(self._image_cache) >= self._max_cache_size:
            oldest_key = next(iter(self._image_cache))
            self.cleanup_image(self._image_cache.pop(oldest_key))

        self._image_cache[key] = image.copy()

    def get_cached_image(self, key: str) -> QImage | None:
        """
        Get cached image.

        Args:
            key: Cache key

        Returns:
            Cached image or None
        """
        return self._image_cache.get(key)

    def clear_cache(self) -> None:
        """Clear all cached images."""
        for image in self._image_cache.values():
            self.cleanup_image(image)
        self._image_cache.clear()
        self.force_garbage_collection()
        logger.info("Image cache cleared")


class ResourceGuard:
    """
    Context manager for safe resource handling.

    Ensures resources are properly cleaned up even if errors occur.
    """

    def __init__(self, resource: Any, cleanup_func: callable):
        """
        Initialize resource guard.

        Args:
            resource: Resource to guard
            cleanup_func: Function to call for cleanup
        """
        self.resource = resource
        self.cleanup_func = cleanup_func

    def __enter__(self):
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.cleanup_func(self.resource)
        except Exception as e:
            logger.error(f"Error during resource cleanup: {e}")
        return False  # Don't suppress exceptions


def safe_image_operation(func):
    """
    Decorator for safe image operations with automatic cleanup.

    Usage:
        @safe_image_operation
        def process_image(self, image: QImage) -> QImage:
            # Process image
            return result
    """
    def wrapper(*args, **kwargs):
        temp_images = []
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
        finally:
            # Cleanup temporary images
            for img in temp_images:
                if img is not None:
                    del img
            gc.collect()

    return wrapper
