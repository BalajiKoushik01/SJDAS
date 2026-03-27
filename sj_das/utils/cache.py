"""
Caching utilities for SJ-DAS.

Provides LRU caching for expensive operations to improve performance.
"""

import hashlib
import logging
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, Optional, TypeVar

from PyQt6.QtGui import QImage

logger = logging.getLogger("SJ_DAS.Cache")

F = TypeVar('F', bound=Callable[..., Any])


class ImageCache:
    """
    LRU cache for QImage objects.

    Features:
        - Size-based eviction
        - Memory usage tracking
        - Cache statistics
    """

    def __init__(self, max_size_mb: int = 100):
        """
        Initialize image cache.

        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size_mb = max_size_mb
        self._cache: Dict[str, QImage] = {}
        self._sizes: Dict[str, int] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[QImage]:
        """
        Get image from cache.

        Args:
            key: Cache key

        Returns:
            Cached image or None
        """
        if key in self._cache:
            self._hits += 1
            logger.debug(f"Cache hit: {key}")
            return self._cache[key].copy()

        self._misses += 1
        logger.debug(f"Cache miss: {key}")
        return None

    def put(self, key: str, image: QImage) -> None:
        """
        Put image in cache.

        Args:
            key: Cache key
            image: Image to cache
        """
        # Calculate image size
        size_bytes = image.sizeInBytes()
        size_mb = size_bytes / (1024 * 1024)

        # Check if we need to evict
        while self.get_size_mb() + size_mb > self.max_size_mb and self._cache:
            # Evict oldest (first) item
            oldest_key = next(iter(self._cache))
            self._evict(oldest_key)

        # Store image
        self._cache[key] = image.copy()
        self._sizes[key] = size_bytes
        logger.debug(f"Cached image: {key} ({size_mb:.2f}MB)")

    def _evict(self, key: str) -> None:
        """Evict item from cache."""
        if key in self._cache:
            del self._cache[key]
            del self._sizes[key]
            logger.debug(f"Evicted from cache: {key}")

    def clear(self) -> None:
        """Clear all cached images."""
        count = len(self._cache)
        self._cache.clear()
        self._sizes.clear()
        logger.info(f"Cleared {count} images from cache")

    def get_size_mb(self) -> float:
        """
        Get current cache size in megabytes.

        Returns:
            Size in MB
        """
        total_bytes = sum(self._sizes.values())
        return total_bytes / (1024 * 1024)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            'size_mb': self.get_size_mb(),
            'max_size_mb': self.max_size_mb,
            'item_count': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate
        }


# Global image cache
_image_cache = ImageCache(max_size_mb=100)


def get_image_cache() -> ImageCache:
    """Get the global image cache."""
    return _image_cache


def cached_result(maxsize: int = 128) -> Callable[[F], F]:
    """
    Decorator for caching function results with LRU.

    Args:
        maxsize: Maximum cache size

    Returns:
        Decorated function

    Example:
        @cached_result(maxsize=256)
        def expensive_calculation(x: int) -> int:
            return x ** 2
    """
    def decorator(func: F) -> F:
        cached_func = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return cached_func(*args, **kwargs)

        # Add cache info method
        wrapper.cache_info = cached_func.cache_info  # type: ignore
        wrapper.cache_clear = cached_func.cache_clear  # type: ignore

        return wrapper  # type: ignore

    return decorator


def image_hash(image: QImage) -> str:
    """
    Generate hash for QImage.

    Args:
        image: Image to hash

    Returns:
        Hash string
    """
    # Use image dimensions and first few pixels as hash
    width = image.width()
    height = image.height()

    # Sample a few pixels
    sample_data = []
    for y in range(0, min(height, 10), 2):
        for x in range(0, min(width, 10), 2):
            pixel = image.pixel(x, y)
            sample_data.append(pixel)

    # Create hash
    hash_input = f"{width}x{height}:{sample_data}"
    return hashlib.sha256(hash_input.encode()).hexdigest()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics for all caches.

    Returns:
        Dictionary with cache statistics
    """
    return {
        'image_cache': _image_cache.get_stats()
    }
