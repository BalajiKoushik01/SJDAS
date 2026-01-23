"""
Memory Management System for SJ-DAS
Monitors memory usage and triggers cleanup when needed
"""
import gc
import time
from typing import Any, Callable, Dict, List

import psutil

from sj_das.utils.enhanced_logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """
    Monitor and manage application memory usage.

    Features:
    - Real-time memory monitoring
    - Automatic cleanup triggers
    - Configurable thresholds
    - Cleanup callbacks
    """

    def __init__(self, max_memory_mb: int = 2048,
                 warning_threshold: float = 0.8):
        """
        Initialize memory manager.

        Args:
            max_memory_mb: Maximum allowed memory in MB
            warning_threshold: Threshold to trigger warnings (0.0-1.0)
        """
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.warning_threshold = warning_threshold
        self.cleanup_callbacks: List[Callable] = []
        self.last_check = 0
        self.check_interval = 10  # seconds

        logger.info(
            f"MemoryManager initialized (max: {max_memory_mb}MB, threshold: {warning_threshold:.0%})")

    def get_usage(self) -> int:
        """
        Get current memory usage in bytes.

        Returns:
            Current memory usage
        """
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0

    def get_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.get_usage() / 1024 / 1024

    def get_utilization(self) -> float:
        """
        Get memory utilization as percentage.

        Returns:
            Utilization (0.0-1.0)
        """
        return self.get_usage() / self.max_memory if self.max_memory > 0 else 0.0

    def register_cleanup_callback(self, callback: Callable):
        """
        Register callback to be called during cleanup.

        Args:
            callback: Function to call for cleanup
        """
        self.cleanup_callbacks.append(callback)
        logger.debug(f"Registered cleanup callback: {callback.__name__}")

    def check_and_cleanup(self, force: bool = False) -> bool:
        """
        Check memory and trigger cleanup if needed.

        Args:
            force: Force cleanup regardless of threshold

        Returns:
            True if cleanup was triggered
        """
        current_time = time.time()

        # Rate limit checks
        if not force and (
                current_time - self.last_check) < self.check_interval:
            return False

        self.last_check = current_time
        utilization = self.get_utilization()

        if force or utilization > self.warning_threshold:
            logger.warning(
                f"Memory usage high: {utilization:.1%} ({self.get_usage_mb():.1f}MB)")
            self.trigger_cleanup()
            return True

        return False

    def trigger_cleanup(self):
        """Trigger all cleanup callbacks and garbage collection."""
        logger.info("Triggering memory cleanup")

        # Call registered callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Cleanup callback failed: {e}")

        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")

        # Log new usage
        new_usage = self.get_usage_mb()
        logger.info(f"Memory after cleanup: {new_usage:.1f}MB")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dictionary with memory metrics
        """
        usage = self.get_usage()
        return {
            'current_mb': usage / 1024 / 1024,
            'max_mb': self.max_memory / 1024 / 1024,
            'utilization': self.get_utilization(),
            'warning_threshold': self.warning_threshold,
            'callbacks_registered': len(self.cleanup_callbacks)
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (f"MemoryManager(usage={stats['current_mb']:.1f}MB, "
                f"utilization={stats['utilization']:.1%})")


# Global memory manager instance
_global_memory_manager: MemoryManager = None


def get_memory_manager(max_memory_mb: int = 2048) -> MemoryManager:
    """
    Get global memory manager instance (singleton).

    Args:
        max_memory_mb: Maximum memory (only used on first call)

    Returns:
        Global MemoryManager instance
    """
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager(max_memory_mb)
    return _global_memory_manager
