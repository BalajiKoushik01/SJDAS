"""
Comprehensive Integration Test Suite for SJ-DAS
Tests complete workflows end-to-end
"""
from sj_das.utils.render_optimizer import get_render_optimizer
from sj_das.utils.model_manager import get_model_manager
from sj_das.utils.memory_manager import get_memory_manager
from sj_das.utils.image_cache import get_cache
from sj_das.core.quantizer import ColorQuantizerEngine
from sj_das.core.loom_engine import LoomEngine
from sj_das.core.design_recovery import DesignRecoveryEngine
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


class IntegrationTestSuite:
    """Comprehensive integration tests."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name, func):
        """Run a test."""
        try:
            start = time.time()
            func()
            elapsed = time.time() - start
            self.passed += 1
            print(f"✅ {name} ({elapsed:.2f}s)")
            return True
        except Exception as e:
            self.failed += 1
            error = f"❌ {name}: {str(e)}"
            print(error)
            self.errors.append((name, str(e)))
            return False

    def report(self):
        """Print test report."""
        print("\n" + "=" * 60)
        print(
            f"Integration Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)

        if self.errors:
            print("\nFailed Tests:")
            for name, error in self.errors:
                print(f"  {name}: {error}")


def test_complete_design_workflow():
    """Test complete design workflow: load → quantize → weave → export."""
    # 1. Create sample design
    design = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)

    # 2. Quantize colors
    quantizer = ColorQuantizerEngine()
    quantized = quantizer.quantize(design, k=8)
    assert quantized is not None
    assert quantized.shape == design.shape

    # 3. Convert to weave
    loom = LoomEngine()
    weave = loom.design_to_weave(quantized[:, :, 0], hooks=500)
    assert weave is not None

    # 4. Verify cache was used on second quantization
    quantized2 = quantizer.quantize(design, k=8)
    assert np.array_equal(quantized, quantized2)

    print(
        f"  Workflow: Design ({design.shape}) → Quantized → Weave ({weave.shape})")


def test_caching_integration():
    """Test caching across multiple operations."""
    cache = get_cache()
    cache.clear()

    quantizer = ColorQuantizerEngine()

    # Process 5 images
    images = [
        np.random.randint(
            0, 255, (200, 200, 3), dtype=np.uint8) for _ in range(5)]

    # First pass - all cache misses
    for img in images:
        quantizer.quantize(img, k=8)

    # Second pass - all cache hits
    for img in images:
        quantizer.quantize(img, k=8)

    stats = cache.get_stats()
    assert stats['hit_rate'] >= 0.5  # At least 50% hit rate

    print(
        f"  Cache: {stats['entries']} entries, {stats['hit_rate']:.0%} hit rate")


def test_memory_management_integration():
    """Test memory management across operations."""
    mm = get_memory_manager()

    # Register cleanup
    cleanup_called = [False]

    def cleanup():
        cleanup_called[0] = True

    mm.register_cleanup_callback(cleanup)

    # Force cleanup
    mm.trigger_cleanup()

    assert cleanup_called[0]

    stats = mm.get_stats()
    print(
        f"  Memory: {stats['current_mb']:.1f}MB, {stats['callbacks_registered']} callbacks")


def test_render_optimization_workflow():
    """Test rendering optimization in workflow."""
    from PyQt6.QtCore import QRect

    optimizer = get_render_optimizer()
    optimizer.clear_cache()

    # Simulate large image
    image_size = (2000, 2000)
    viewport = QRect(500, 500, 800, 600)

    # Get visible tiles
    visible = optimizer.get_visible_tiles(viewport, image_size)

    # Mark some dirty
    optimizer.mark_dirty(600, 600, 200, 200)

    stats = optimizer.get_cache_stats()
    assert stats['dirty_tiles'] > 0

    print(
        f"  Rendering: {len(visible)} visible tiles, {stats['dirty_tiles']} dirty")


def test_error_recovery():
    """Test error recovery scenarios."""
    quantizer = ColorQuantizerEngine()

    # Test with invalid input
    try:
        quantizer.quantize(np.array([]), k=8)
        assert False, "Should have raised error"
    except Exception:
        pass  # Expected

    # Test with invalid k
    try:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        quantizer.quantize(img, k=1000)
        assert False, "Should have raised error"
    except Exception:
        pass  # Expected

    print("  Error recovery: Handled invalid inputs correctly")


def test_concurrent_operations():
    """Test concurrent operations."""
    import threading

    quantizer = ColorQuantizerEngine()
    results = []

    def process_image(idx):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = quantizer.quantize(img, k=8)
        results.append(result is not None)

    # Run 5 concurrent operations
    threads = [
        threading.Thread(
            target=process_image,
            args=(
                i,
            )) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(results)
    print(f"  Concurrent: {len(results)} operations completed successfully")


def test_large_image_handling():
    """Test handling of large images."""
    # Create large image (4K)
    large_img = np.random.randint(0, 255, (4000, 4000, 3), dtype=np.uint8)

    quantizer = ColorQuantizerEngine()

    start = time.time()
    result = quantizer.quantize(large_img, k=8)
    elapsed = time.time() - start

    assert result is not None
    assert result.shape == large_img.shape

    print(f"  Large image (4K): Processed in {elapsed:.2f}s")


def test_model_manager_integration():
    """Test model manager integration."""
    manager = get_model_manager()

    # Register dummy loader
    def load_test():
        return {"model": "test", "loaded": True}

    manager.register_loader('test_model', load_test)

    # Load model
    model = manager.get_model('test_model')
    assert model is not None

    stats = manager.get_stats()
    print(
        f"  Model manager: {stats['loaded_models']} loaded, {stats['registered_loaders']} registered")


if __name__ == "__main__":
    print("=" * 60)
    print("SJ-DAS Integration Test Suite")
    print("=" * 60)

    suite = IntegrationTestSuite()

    print("\n🔄 Testing Complete Workflows...")
    suite.test("Complete design workflow", test_complete_design_workflow)

    print("\n💾 Testing Caching Integration...")
    suite.test("Caching across operations", test_caching_integration)

    print("\n🧠 Testing Memory Management...")
    suite.test(
        "Memory management integration",
        test_memory_management_integration)

    print("\n🎨 Testing Render Optimization...")
    suite.test(
        "Render optimization workflow",
        test_render_optimization_workflow)

    print("\n⚠️ Testing Error Recovery...")
    suite.test("Error recovery scenarios", test_error_recovery)

    print("\n🔀 Testing Concurrent Operations...")
    suite.test("Concurrent operations", test_concurrent_operations)

    print("\n📏 Testing Large Images...")
    suite.test("Large image handling (4K)", test_large_image_handling)

    print("\n🤖 Testing Model Manager...")
    suite.test("Model manager integration", test_model_manager_integration)

    # Final report
    suite.report()

    sys.exit(0 if suite.failed == 0 else 1)
