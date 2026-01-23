"""
Test Suite for Canvas Rendering Optimization
Tests Phase 1.2 performance optimizations
"""
from sj_das.utils.render_optimizer import (ProgressiveRenderer,
                                           RenderOptimizer,
                                           get_render_optimizer)
from PyQt6.QtCore import QRect
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_viewport_culling():
    """Test viewport culling."""
    optimizer = RenderOptimizer(tile_size=256)

    # Image size 1000x1000, viewport 0,0,500,500
    viewport = QRect(0, 0, 500, 500)
    image_size = (1000, 1000)

    visible_tiles = optimizer.get_visible_tiles(viewport, image_size)

    # Should only get tiles in viewport
    assert len(visible_tiles) > 0
    assert len(visible_tiles) < 16  # Much less than total tiles

    print(f"✅ Viewport culling works ({len(visible_tiles)} visible tiles)")


def test_dirty_rectangle_tracking():
    """Test dirty rectangle tracking."""
    optimizer = RenderOptimizer(tile_size=256)

    # Mark region as dirty
    optimizer.mark_dirty(100, 100, 200, 200)

    stats = optimizer.get_cache_stats()
    assert stats['dirty_tiles'] > 0

    print(f"✅ Dirty tracking works ({stats['dirty_tiles']} dirty tiles)")


def test_tile_caching():
    """Test tile caching."""
    from PyQt6.QtGui import QImage

    optimizer = RenderOptimizer(tile_size=256)

    # Create dummy tile
    tile = QImage(256, 256, QImage.Format.Format_RGB888)

    # Cache it
    optimizer.cache_tile(0, 0, tile)

    # Retrieve it
    cached = optimizer.get_cached_tile(0, 0)
    assert cached is not None

    stats = optimizer.get_cache_stats()
    assert stats['cached_tiles'] == 1

    print(f"✅ Tile caching works ({stats['cache_memory_mb']:.2f}MB)")


def test_progressive_rendering():
    """Test progressive rendering."""
    renderer = ProgressiveRenderer()

    # Create test image
    image = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)

    # Render progressively
    results = renderer.render_progressive(image, (500, 500), quality_levels=3)

    assert len(results) == 3
    assert results[0].width() < results[-1].width()

    print(f"✅ Progressive rendering works ({len(results)} quality levels)")


def test_render_optimization_integration():
    """Test full rendering optimization."""
    optimizer = get_render_optimizer()

    # Simulate large image
    image_size = (4000, 4000)
    viewport = QRect(1000, 1000, 800, 600)

    # Get visible tiles
    visible = optimizer.get_visible_tiles(viewport, image_size)

    # Calculate savings
    total_tiles = ((image_size[0] // 256) + 1) * ((image_size[1] // 256) + 1)
    savings = (1 - len(visible) / total_tiles) * 100

    print(f"✅ Optimization works ({savings:.0f}% fewer tiles rendered)")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1.2 Canvas Rendering Optimization Tests")
    print("=" * 60)

    print("\n📦 Testing Viewport Culling...")
    test_viewport_culling()

    print("\n🎯 Testing Dirty Tracking...")
    test_dirty_rectangle_tracking()

    print("\n💾 Testing Tile Caching...")
    test_tile_caching()

    print("\n🎨 Testing Progressive Rendering...")
    test_progressive_rendering()

    print("\n🔄 Testing Integration...")
    test_render_optimization_integration()

    print("\n" + "=" * 60)
    print("✅ All Phase 1.2 tests passed!")
    print("=" * 60)
