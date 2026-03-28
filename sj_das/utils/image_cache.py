"""
Image Caching System for SJ-DAS
Implements LRU cache for processed images to improve performance
"""
import hashlib
import time
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple

import numpy as np

from sj_das.utils.enhanced_logger import get_logger

logger = get_logger(__name__)


class ImageCache:
    """
    LRU (Least Recently Used) cache for processed images.

    Features:
    - Size-based eviction (default 500MB)
    - Cache hit/miss metrics
    - Automatic cleanup
    - Thread-safe operations
    """

    def __init__(self, max_size_mb: int = 500):
        """
        Initialize image cache.

        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
        self.current_size = 0
        self.cache: OrderedDict[str, np.ndarray] = OrderedDict()

        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        logger.info(f"ImageCache initialized with max size: {max_size_mb}MB")

    def _generate_key(self, image: np.ndarray, operation: str,
                      params: Dict[str, Any]) -> str:
        """
        Generate unique cache key from image, operation, and parameters.

        Args:
            image: Input image array
            operation: Operation name (e.g., 'quantize', 'weave')
            params: Operation parameters

        Returns:
            Unique cache key string
        """
        try:
            # Hash image data (Use SHA256 for better collision resistance)
            img_hash = hashlib.sha256(image.tobytes()).hexdigest()[:16]

            # Sort params for consistent keys
            param_str = '_'.join(f"{k}={v}" for k, v in sorted(params.items()))

            key = f"{operation}_{img_hash}_{param_str}"
            return key
        except Exception as e:
            logger.error(f"Failed to generate cache key: {e}")
            return f"{operation}_{time.time()}"  # Fallback to timestamp

    def get(self, image: np.ndarray, operation: str,
            params: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Get cached result if available.

        Args:
            image: Input image
            operation: Operation name
            params: Operation parameters

        Returns:
            Cached result or None if not found
        """
        key = self._generate_key(image, operation, params)

        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            logger.debug(
                f"Cache HIT for {operation} (hit rate: {self.hit_rate:.1%})")
            # Return copy to prevent modification
            return self.cache[key].copy()

        self.misses += 1
        logger.debug(
            f"Cache MISS for {operation} (hit rate: {self.hit_rate:.1%})")
        return None

    def put(self, image: np.ndarray, operation: str,
            params: Dict[str, Any], result: np.ndarray):
        """
        Cache operation result.

        Args:
            image: Input image
            operation: Operation name
            params: Operation parameters
            result: Result to cache
        """
        key = self._generate_key(image, operation, params)
        result_size = result.nbytes

        # Evict old entries if needed
        while self.current_size + result_size > self.max_size and self.cache:
            evict_key, evict_value = self.cache.popitem(
                last=False)  # Remove oldest
            self.current_size -= evict_value.nbytes
            self.evictions += 1
            logger.debug(f"Evicted cache entry: {evict_key}")

        # Add new entry
        self.cache[key] = result.copy()
        self.current_size += result_size

        logger.debug(f"Cached {operation} result ({result_size / 1024 / 1024:.2f}MB, "
                     f"total: {self.current_size / 1024 / 1024:.2f}MB)")

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache metrics
        """
        return {
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'hit_rate': self.hit_rate,
            'current_size_mb': self.current_size / 1024 / 1024,
            'max_size_mb': self.max_size / 1024 / 1024,
            'entries': len(self.cache),
            'utilization': self.current_size / self.max_size if self.max_size > 0 else 0.0
        }

    def clear(self):
        """Clear all cached entries."""
        self.cache.clear()
        self.current_size = 0
        logger.info("Cache cleared")

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (f"ImageCache(entries={stats['entries']}, "
                f"size={stats['current_size_mb']:.1f}MB, "
                f"hit_rate={stats['hit_rate']:.1%})")


# Global cache instance
_global_cache: Optional[ImageCache] = None


def get_cache(max_size_mb: int = 500) -> ImageCache:
    """
    Get global cache instance (singleton pattern).

    Args:
        max_size_mb: Maximum cache size (only used on first call)

    Returns:
        Global ImageCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = ImageCache(max_size_mb)
    return _global_cache


def cached_operation(operation_name: str):
    """
    Decorator to automatically cache operation results.

    Usage:
        @cached_operation('quantize')
        def quantize(image, k=8):
            # ... expensive operation
            return result
    """
    def decorator(func):
        def wrapper(self, image: np.ndarray, **kwargs):
            cache = get_cache()

            # Try to get from cache
            cached_result = cache.get(image, operation_name, kwargs)
            if cached_result is not None:
                return cached_result

            # Execute operation
            result = func(self, image, **kwargs)

            # Cache result
            if result is not None and isinstance(result, np.ndarray):
                cache.put(image, operation_name, kwargs, result)

            return result

        return wrapper
    return decorator
