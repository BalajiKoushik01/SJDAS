"""
UI/UX Integration Test Script
Tests all major UI features to identify non-working functionality
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ui_features():
    """Test all UI features for integration issues."""
    print("=" * 60)
    print("UI/UX Integration Testing")
    print("=" * 60)

    issues = []

    # Test 1: Menu System
    print("\n1. Testing Menu System...")
    try:
        from sj_das.ui.components.menu_builder import StandardMenuBuilder
        from sj_das.ui.modern_designer_view import PremiumDesignerView

        # Check if all menu methods exist
        required_methods = [
            'build_file_menu',
            'build_edit_menu',
            'build_view_menu',
            'build_tools_menu',
            'build_ai_tools_menu',
            'build_help_menu'
        ]

        for method in required_methods:
            if not hasattr(StandardMenuBuilder, method):
                issues.append(f"Missing menu method: {method}")

        print("   ✅ Menu system structure OK")
    except Exception as e:
        issues.append(f"Menu system error: {e}")
        print(f"   ❌ Menu system error: {e}")

    # Test 2: AI Tools Integration
    print("\n2. Testing AI Tools Integration...")
    try:
        from sj_das.ui.modern_designer_view import PremiumDesignerView

        required_ai_methods = [
            'show_ai_pattern_gen',
            'generate_from_sketch_controlnet',
            'apply_ai_upscale_4x',
            'show_defect_scan',
            'apply_smart_quantize_8'
        ]

        for method in required_ai_methods:
            if not hasattr(PremiumDesignerView, method):
                issues.append(f"Missing AI method: {method}")

        print("   ✅ AI tools methods present")
    except Exception as e:
        issues.append(f"AI tools error: {e}")
        print(f"   ❌ AI tools error: {e}")

    # Test 3: Design Recovery
    print("\n3. Testing Design Recovery...")
    try:
        from sj_das.core import DesignRecoveryEngine

        if DesignRecoveryEngine is None:
            issues.append("DesignRecoveryEngine not available")
        else:
            recovery = DesignRecoveryEngine()
            if not hasattr(recovery, 'recover_design'):
                issues.append("recover_design method missing")

        print("   ✅ Design Recovery available")
    except Exception as e:
        issues.append(f"Design Recovery error: {e}")
        print(f"   ❌ Design Recovery error: {e}")

    # Test 4: ControlNet Integration
    print("\n4. Testing ControlNet...")
    try:
        from sj_das.core import ControlNetEngine

        if ControlNetEngine is None:
            issues.append("ControlNetEngine not available")
        else:
            controlnet = ControlNetEngine()
            if not hasattr(controlnet, 'generate_from_sketch'):
                issues.append("generate_from_sketch method missing")

        print("   ✅ ControlNet available")
    except Exception as e:
        issues.append(f"ControlNet error: {e}")
        print(f"   ❌ ControlNet error: {e}")

    # Test 5: Loom Export
    print("\n5. Testing Loom Export...")
    try:
        from sj_das.core import LoomEngine

        if LoomEngine is None:
            issues.append("LoomEngine not available")
        else:
            loom = LoomEngine()
            required_loom_methods = [
                'generate_graph',
                'save_loom_file',
                'design_to_weave']
            for method in required_loom_methods:
                if not hasattr(loom, method):
                    issues.append(f"LoomEngine missing: {method}")

        print("   ✅ Loom export available")
    except Exception as e:
        issues.append(f"Loom export error: {e}")
        print(f"   ❌ Loom export error: {e}")

    # Test 6: Voice Commands
    print("\n6. Testing Voice Commands...")
    try:
        from sj_das.core import VoiceCommandEngine

        if VoiceCommandEngine is None:
            print("   ⚠️  Voice commands not available (optional)")
        else:
            print("   ✅ Voice commands available")
    except Exception as e:
        print(f"   ⚠️  Voice commands not available: {e}")

    # Test 7: 3D Fabric Rendering
    print("\n7. Testing 3D Fabric Rendering...")
    try:
        from sj_das.core import FabricRenderer3D

        if FabricRenderer3D is None:
            issues.append("FabricRenderer3D not available")
        else:
            print("   ✅ 3D rendering available")
    except Exception as e:
        issues.append(f"3D rendering error: {e}")
        print(f"   ❌ 3D rendering error: {e}")

    # Test 8: Costing Engine
    print("\n8. Testing Costing Engine...")
    try:
        from sj_das.core import CostingEngine

        if CostingEngine is None:
            issues.append("CostingEngine not available")
        else:
            print("   ✅ Costing engine available")
    except Exception as e:
        issues.append(f"Costing error: {e}")
        print(f"   ❌ Costing error: {e}")

    # Final Report
    print("\n" + "=" * 60)
    print("INTEGRATION TEST RESULTS")
    print("=" * 60)

    if not issues:
        print("✅ ALL UI/UX FEATURES INTEGRATED PROPERLY")
        return True
    else:
        print(f"❌ FOUND {len(issues)} INTEGRATION ISSUES:\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        return False


if __name__ == "__main__":
    success = test_ui_features()
    sys.exit(0 if success else 1)
