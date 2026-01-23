
import logging
import os
import sys

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY")

# Add project root to sys.path to assert imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def verify_modules():
    print("--- Verifying Module Integriy ---")

    try:
        print("1. Importing AIService...")
        from sj_das.core.services.ai_service import AIService
        print("   -> Success")
    except Exception as e:
        print(f"   -> FAILED: {e}")
        return False

    try:
        print("2. Importing SAMEngine...")
        from sj_das.core.engines.vision.sam_engine import SAMEngine
        print("   -> Success")
    except Exception as e:
        print(f"   -> FAILED: {e}")
        return False

    try:
        print("3. Importing AGIAssistant...")
        from sj_das.ai.agi_assistant import AGIAssistant
        print("   -> Success")
    except Exception as e:
        print(f"   -> FAILED: {e}")
        return False

    try:
        print("4. Importing ModernMainWindow...")
        # This requires QApplication usually, might fail if headless without
        # qpa
        from PyQt6.QtWidgets import QApplication
        if not QApplication.instance():
            app = QApplication(sys.argv)
        from sj_das.ui.modern_main_window import ModernMainWindow
        print("   -> Success")
    except Exception as e:
        print(f"   -> FAILED: {e}")
        return False

    try:
        print("5. Importing PremiumDesignerView...")
        from sj_das.ui.modern_designer_view import PremiumDesignerView
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        return False

    print("6. Importing TextileService...")
    try:
        from sj_das.core.services.textile_service import TextileService

        # Check initialization
        svc = TextileService.instance()
        print(f"   -> Success (Weaves: {len(svc.get_available_weaves())})")
    except Exception as e:
        print(f"   -> Failed: {e}")
        return False

    print("7. Importing FabricPreviewDialog...")
    try:
        from sj_das.ui.dialogs.fabric_preview_dialog import FabricPreviewDialog
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        return False

    print("8. Importing OwlEngine (Smart Vision)...")
    try:
        from sj_das.core.engines.vision.owl_engine import OwlEngine
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed (Transformers missing?): {e}")
        return False

    print("9. Importing TechSheetGenerator...")
    try:
        from sj_das.core.reporting.tech_sheet_generator import \
            TechSheetGenerator
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        return False

    print("10. Importing PatternTilingDialog...")
    try:
        from sj_das.ui.dialogs.pattern_tiling_dialog import PatternTilingDialog
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        return False

    print("11. Importing RealESRGANUpscaler...")
    try:
        from sj_das.core.engines.enhancement.real_esrgan_upscaler import \
            RealESRGANUpscaler
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        # Not fatal, but good to know

    print("12. Importing CloudService (Requests)...")
    try:
        import requests

        from sj_das.core.services.cloud_service import CloudService
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}. (pip install requests)")
        return False

    print("13. Importing InspirationDialog (Met API)...")
    try:
        from sj_das.ui.dialogs.inspiration_dialog import InspirationDialog
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        return False

    print("14. Verifying Cortex (The Brain)...")
    try:
        from sj_das.core.cortex.orchestrator import CortexOrchestrator
        from sj_das.ui.components.omni_bar import OmniBar
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        return False

    print("15. Verifying UX Components (Toolbar)...")
    try:
        from sj_das.ui.components.toolbar import AcrylicToolbar
        print("   -> Success")
    except ImportError as e:
        print(f"   -> Failed: {e}")
        return False

    print("\nAll critical modules imported successfully.")
    return True


if __name__ == "__main__":
    success = verify_modules()
    sys.exit(0 if success else 1)
