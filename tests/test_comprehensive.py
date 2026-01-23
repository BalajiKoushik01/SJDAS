"""
Comprehensive Test Suite for SJ-DAS
Tests all components, identifies bottlenecks, validates functionality
"""
import sys
import time
import traceback
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name, func):
        """Run a single test."""
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
            self.errors.append((name, traceback.format_exc()))
            return False

    def report(self):
        """Print test report."""
        print("\n" + "=" * 60)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)

        if self.errors:
            print("\nFailed Tests:")
            for name, trace in self.errors:
                print(f"\n{name}:")
                print(trace)


# Initialize test runner
runner = TestRunner()

# ============================================================================
# PART 1: Core Module Tests
# ============================================================================


def test_core_imports():
    """Test all core module imports."""
    from sj_das.core import (AdvancedVisionEngine, AgentEngine, AIOrchestrator,
                             AIUpscaler, CLIPEngine, ControlNetEngine,
                             DesignRecoveryEngine, FabricRenderer3D,
                             LoomEngine, MagicEraserEngine, MiDaSDepth,
                             RealESRGANUpscaler, SAMEngine,
                             StyleTransferEngine, VoiceCommandEngine)
    assert AIUpscaler is not None
    assert ControlNetEngine is not None


def test_loom_engine():
    """Test loom engine functionality."""
    import numpy as np

    from sj_das.core import LoomEngine

    loom = LoomEngine()

    # Test weave generation
    weave = loom.get_weave_structure("plain")
    assert weave is not None
    assert weave.shape[0] > 0

    # Test design to weave conversion
    design = np.random.randint(0, 8, (100, 100), dtype=np.uint8)
    weave_map = loom.design_to_weave(design, hooks=100)
    assert weave_map is not None
    print(f"  Weave map shape: {weave_map.shape}")


def test_color_quantizer():
    """Test color quantization."""
    import numpy as np

    from sj_das.core.quantizer import ColorQuantizerEngine

    quantizer = ColorQuantizerEngine()

    # Create test image
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    # Quantize to 8 colors (k parameter)
    result = quantizer.quantize(img, k=8)
    assert result is not None
    assert result.shape == img.shape
    print(f"  Quantized {img.shape} image to 8 colors")


def test_ai_orchestrator():
    """Test AI orchestrator routing."""
    from sj_das.core import AIOrchestrator

    orch = AIOrchestrator()

    # Test that orchestrator exists and has route method
    assert hasattr(orch, 'route')
    print(f"  AI Orchestrator initialized successfully")

# ============================================================================
# PART 2: AI Engine Tests
# ============================================================================


def test_clip_engine():
    """Test CLIP engine."""
    from sj_das.core import CLIPEngine

    # Just verify it can be imported
    assert CLIPEngine is not None
    print(f"  CLIP engine available")


def test_sam_engine():
    """Test SAM engine."""
    from sj_das.core import SAMEngine

    # Just verify it can be imported
    assert SAMEngine is not None
    print(f"  SAM engine available")


def test_design_recovery_engine():
    """Test design recovery pipeline."""
    from sj_das.core import DesignRecoveryEngine

    # Just verify it can be imported
    assert DesignRecoveryEngine is not None
    print(f"  Design Recovery engine available")


def test_controlnet_engine():
    """Test ControlNet engine."""
    from sj_das.core import ControlNetEngine

    # Just verify it can be imported
    assert ControlNetEngine is not None
    print(f"  ControlNet engine available")

# ============================================================================
# PART 3: UI Component Tests
# ============================================================================


def test_ui_imports():
    """Test UI module imports."""
    from sj_das.ui.editor_widget import PixelEditorWidget
    from sj_das.ui.modern_designer_view import PremiumDesignerView
    from sj_das.ui.modern_main_window import ModernMainWindow

    assert ModernMainWindow is not None
    assert PremiumDesignerView is not None
    assert PixelEditorWidget is not None


def test_menu_builder():
    """Test menu builder."""
    from sj_das.ui.components.menu_builder import StandardMenuBuilder

    assert StandardMenuBuilder is not None
    assert hasattr(StandardMenuBuilder, 'build_file_menu')
    assert hasattr(StandardMenuBuilder, 'build_ai_tools_menu')

# ============================================================================
# PART 4: Integration Tests
# ============================================================================


def test_full_workflow_simulation():
    """Simulate complete design workflow."""
    import numpy as np

    from sj_das.core import ColorQuantizerEngine, LoomEngine

    # 1. Create sample design
    design = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)

    # 2. Quantize colors
    quantizer = ColorQuantizerEngine()
    quantized = quantizer.quantize(design, k=8)
    assert quantized is not None

    # 3. Convert to weave
    loom = LoomEngine()
    weave = loom.design_to_weave(quantized[:, :, 0], hooks=200)
    assert weave is not None

    print(
        f"  Workflow: Design ({design.shape}) → Quantized → Weave ({weave.shape})")

# ============================================================================
# PART 5: Performance Benchmarks
# ============================================================================


def benchmark_color_quantization():
    """Benchmark color quantization performance."""
    import numpy as np

    from sj_das.core.quantizer import ColorQuantizerEngine

    quantizer = ColorQuantizerEngine()

    sizes = [(100, 100), (500, 500), (1000, 1000)]

    for size in sizes:
        img = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)

        start = time.time()
        result = quantizer.quantize(img, k=8)
        elapsed = time.time() - start

        print(
            f"  {size[0]}x{size[1]}: {elapsed:.3f}s ({size[0]*size[1]/elapsed:.0f} pixels/sec)")


def benchmark_weave_generation():
    """Benchmark weave generation."""
    import numpy as np

    from sj_das.core import LoomEngine

    loom = LoomEngine()

    sizes = [100, 500, 1000, 2000]

    for size in sizes:
        design = np.random.randint(0, 8, (size, size), dtype=np.uint8)

        start = time.time()
        weave = loom.design_to_weave(design, hooks=size)
        elapsed = time.time() - start

        print(f"  {size}x{size}: {elapsed:.3f}s")

# ============================================================================
# Run All Tests
# ============================================================================


if __name__ == "__main__":
    print("=" * 60)
    print("SJ-DAS Comprehensive Test Suite")
    print("=" * 60)

    print("\n📦 Testing Core Modules...")
    runner.test("Core imports", test_core_imports)
    runner.test("Loom engine", test_loom_engine)
    runner.test("Color quantizer", test_color_quantizer)
    runner.test("AI orchestrator", test_ai_orchestrator)

    print("\n🤖 Testing AI Engines...")
    runner.test("CLIP engine", test_clip_engine)
    runner.test("SAM engine", test_sam_engine)
    runner.test("Design recovery", test_design_recovery_engine)
    runner.test("ControlNet", test_controlnet_engine)

    print("\n🎨 Testing UI Components...")
    runner.test("UI imports", test_ui_imports)
    runner.test("Menu builder", test_menu_builder)

    print("\n🔄 Integration Tests...")
    runner.test("Full workflow", test_full_workflow_simulation)

    print("\n⚡ Performance Benchmarks...")
    print("Color Quantization:")
    benchmark_color_quantization()
    print("\nWeave Generation:")
    benchmark_weave_generation()

    # Final report
    runner.report()

    # Exit code
    sys.exit(0 if runner.failed == 0 else 1)
