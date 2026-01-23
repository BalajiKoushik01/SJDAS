"""
Manual UI Testing Script - Tests UI functionality systematically
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ui_methods():
    """Test that all required UI methods exist."""
    print("=" * 60)
    print("SJ-DAS UI Method Validation")
    print("=" * 60)

    results = {"passed": 0, "failed": 0, "errors": []}

    # Test 1: Menu Builder Methods
    print("\n1. Testing Menu Builder Methods...")
    try:
        from sj_das.ui.components.menu_builder import StandardMenuBuilder

        required_methods = [
            'build_file_menu',
            'build_edit_menu',
            'build_view_menu',
            'build_tools_menu',
            'build_image_menu',
            'build_colors_menu',
            'build_textile_menu',
            'build_ai_tools_menu',
            'build_help_menu',
            'build_settings_menu'
        ]

        for method in required_methods:
            if hasattr(StandardMenuBuilder, method):
                print(f"   ✅ {method}")
                results["passed"] += 1
            else:
                print(f"   ❌ {method} - MISSING")
                results["failed"] += 1
                results["errors"].append(f"Missing method: {method}")

    except Exception as e:
        print(f"   ❌ Error loading MenuBuilder: {e}")
        results["failed"] += 1
        results["errors"].append(str(e))

    # Test 2: Designer View Methods
    print("\n2. Testing Designer View Methods...")
    try:
        from sj_das.ui.modern_designer_view import PremiumDesignerView

        required_methods = [
            'new_file',
            'open_file',
            'save_file',
            'undo',
            'redo',
            'activate_brush',
            'activate_eraser',
            'zoom_in',
            'zoom_out',
            'apply_smart_quantize_8',
            'export_to_loom',
            'show_ai_pattern_gen',
            'generate_from_sketch_controlnet'
        ]

        for method in required_methods:
            if hasattr(PremiumDesignerView, method):
                print(f"   ✅ {method}")
                results["passed"] += 1
            else:
                print(f"   ❌ {method} - MISSING")
                results["failed"] += 1
                results["errors"].append(f"Missing method: {method}")

    except Exception as e:
        print(f"   ❌ Error loading DesignerView: {e}")
        results["failed"] += 1
        results["errors"].append(str(e))

    # Test 3: Core Engine Availability
    print("\n3. Testing Core Engines...")
    engines = [
        ('LoomEngine', 'sj_das.core.loom_engine'),
        ('ColorQuantizerEngine', 'sj_das.core.quantizer'),
        ('DesignRecoveryEngine', 'sj_das.core.design_recovery'),
        ('CLIPEngine', 'sj_das.core'),
        ('SAMEngine', 'sj_das.core'),
        ('ControlNetEngine', 'sj_das.core')
    ]

    for engine_name, module_path in engines:
        try:
            module = __import__(module_path, fromlist=[engine_name])
            engine_class = getattr(module, engine_name, None)
            if engine_class is not None:
                print(f"   ✅ {engine_name}")
                results["passed"] += 1
            else:
                print(f"   ❌ {engine_name} - NOT AVAILABLE")
                results["failed"] += 1
                results["errors"].append(f"{engine_name} not available")
        except Exception as e:
            print(f"   ❌ {engine_name} - ERROR: {e}")
            results["failed"] += 1
            results["errors"].append(f"{engine_name}: {e}")

    # Final Report
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")

    if results['failed'] > 0:
        print("\nERRORS:")
        for error in results["errors"]:
            print(f"  - {error}")

    print("=" * 60)

    return results['failed'] == 0


if __name__ == "__main__":
    success = test_ui_methods()
    sys.exit(0 if success else 1)
