"""
Test Suite for Image Caching and Memory Management
Tests Phase 1 performance optimizations
"""
from sj_das.utils.memory_manager import MemoryManager, get_memory_manager
from sj_das.utils.image_cache import ImageCache, get_cache
from sj_das.core.quantizer import ColorQuantizerEngine
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_image_cache_basic():
    """Test basic cache operations."""
    cache = ImageCache(max_size_mb=100)

    # Create test image
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    # Test put and get
    cache.put(img, 'test_op', {'param': 1}, result)
    cached = cache.get(img, 'test_op', {'param': 1})

    assert cached is not None
    assert np.array_equal(cached, result)

    # Test cache miss
    miss = cache.get(img, 'test_op', {'param': 2})
    assert miss is None

    print("✅ Basic cache operations work")


def test_cache_eviction():
    """Test LRU eviction."""
    cache = ImageCache(max_size_mb=1)  # Small cache

    # Fill cache
    for i in range(10):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        cache.put(img, f'op_{i}', {}, result)

    stats = cache.get_stats()
    assert stats['evictions'] > 0
    print(f"✅ Cache eviction works ({stats['evictions']} evictions)")


def test_cache_metrics():
    """Test cache hit/miss metrics."""
    cache = ImageCache(max_size_mb=100)

    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    # Cache miss
    cache.get(img, 'test', {})

    # Cache put
    cache.put(img, 'test', {}, result)

    # Cache hit
    cache.get(img, 'test', {})
    cache.get(img, 'test', {})

    stats = cache.get_stats()
    assert stats['hits'] == 2
    assert stats['misses'] == 1
    assert stats['hit_rate'] == 2 / 3

    print(f"✅ Cache metrics work (hit rate: {stats['hit_rate']:.1%})")


def test_quantizer_caching():
    """Test quantizer with caching."""
    quantizer = ColorQuantizerEngine()

    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)

    # First call - cache miss
    start = time.time()
    result1 = quantizer.quantize(img, k=8)
    time1 = time.time() - start

    # Second call - cache hit
    start = time.time()
    result2 = quantizer.quantize(img, k=8)
    time2 = time.time() - start

    assert np.array_equal(result1, result2)
    assert time2 < time1 * 0.5  # Should be at least 2x faster

    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"✅ Quantizer caching works ({speedup:.1f}x speedup)")


def test_memory_manager():
    """Test memory manager."""
    mm = MemoryManager(max_memory_mb=1024)

    # Test usage monitoring
    usage = mm.get_usage_mb()
    assert usage > 0

    # Test cleanup callback
    cleanup_called = [False]

    def cleanup():
        cleanup_called[0] = True

    mm.register_cleanup_callback(cleanup)
    mm.trigger_cleanup()

    assert cleanup_called[0]

    stats = mm.get_stats()
    print(f"✅ Memory manager works (usage: {stats['current_mb']:.1f}MB)")


def test_cache_integration():
    """Test full cache integration."""
    cache = get_cache()
    cache.clear()

    quantizer = ColorQuantizerEngine()

    # Process multiple images
    for i in range(5):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = quantizer.quantize(img, k=8)
        assert result is not None

    stats = cache.get_stats()
    print(
        f"✅ Cache integration works ({stats['entries']} entries, {stats['hit_rate']:.1%} hit rate)")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1 Performance Optimization Tests")
    print("=" * 60)

    print("\n📦 Testing Image Cache...")
    test_image_cache_basic()
    test_cache_eviction()
    test_cache_metrics()

    print("\n🔄 Testing Integration...")
    test_quantizer_caching()
    test_cache_integration()

    print("\n💾 Testing Memory Manager...")
    test_memory_manager()

    print("\n" + "=" * 60)
    print("✅ All Phase 1 tests passed!")
    print("=" * 60)
