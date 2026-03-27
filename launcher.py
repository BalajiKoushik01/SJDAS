import os
import sys

# Suppress Qt font warnings (cosmetic only, doesn't affect functionality)
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false;qt.gui.font.*=false'

# Fix Torch DLL initialization collision (WinError 1114)
# We must set this before importing torch
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Import AI/CV2 at the absolute top to avoid DLL race conditions with PyQt6
try:
    import torch
    import cv2
    import numpy as np
    import moderngl
    import glm
except Exception:
    pass

from sj_das.ui.modern_main_window import create_modern_app
from PyQt6.QtWidgets import QMessageBox
import traceback


# =============================================================================
# SJ-DAS Standard Launcher
# =============================================================================
# This script is the official entry point for the SJ-DAS (Pro) Application.
# It sets up pathing, exception handling, and initializes the Modern Fluent UI.
# =============================================================================


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import traceback
from PyQt6.QtWidgets import QMessageBox

def exception_hook(exctype, value, tb):
    """Global exception handler to capture and log crashes gracefully."""
    traceback_str = "".join(traceback.format_exception(exctype, value, tb))
    print("\n" + "=" * 80)
    print("CRITICAL ERROR CAUGHT BY LAUNCHER")
    print("=" * 80)
    print(traceback_str)

    # Log to official logger
    try:
        from sj_das.utils.logger import logger
        logger.critical(f"Unhandled exception: {value}\n{traceback_str}")
    except ImportError:
        print("[ERROR] Could not import logger to save crash dump.")
    except Exception as e:
        print(f"[ERROR] Failed to log crash: {e}")

    # User Notification (GUI)
    from PyQt6.QtWidgets import QApplication
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("An unexpected error occurred.")
        msg.setInformativeText(
            f"{value}\n\nThe application will try to continue, but save your work immediately.")
        msg.setDetailedText(traceback_str)
        msg.setWindowTitle("SJ-DAS Error")
        msg.exec()


from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QApplication

# Global Instance
app_instance = None


class StartupWorker(QThread):
    """
    Async worker to handle heavy startup tasks without freezing the UI.
    """
    progress_update = pyqtSignal(str)
    finished_ok = pyqtSignal()
    fatal_error = pyqtSignal(str)

    def run(self):
        try:
            # 1. Core Framework
            self.progress_update.emit("Initializing Core Framework...")
            import time
            from sj_das.ui.theme_manager import ThemeManager
            time.sleep(0.3) # Short buffer for visual smoothing

            # 2. Themes (Visuals first)
            self.progress_update.emit("Loading Interface Themes...")
            ThemeManager() # Pre-load prefs
            time.sleep(0.5) 

            # 3. Textile Engine (Assets)
            self.progress_update.emit("Loading Weave Patterns & Textures...")
            from sj_das.core.services.textile_service import TextileService
            TextileService.instance() # Triggers LoomEngine load
            time.sleep(0.8) # Buffer to show the user this is happening

            # 4. AI Engine
            self.progress_update.emit("Connectng to Neural Engine...")
            from sj_das.core.services.ai_service import AIService
            ai = AIService.instance()
            ai.initialize_core_models() # Hook to verify config
            time.sleep(0.5)

            # 5. User Data/Cloud
            self.progress_update.emit("Loading User Preferences...")
            # Simulated user data/cloud sync check
            time.sleep(0.5)
            
            self.progress_update.emit("Finalizing Interface...")
            time.sleep(0.5)
            
            self.finished_ok.emit()

        except Exception as e:
            traceback.print_exc()
            self.fatal_error.emit(str(e))


def main():
    """
    Main Entry Point with async loading.
    """
    # Register Crash Handler
    sys.excepthook = exception_hook

    print("=" * 60)
    print("   SJ-DAS Pro | Design Automation System")
    print("   Version: 2025.1.0 (Fluent Edition)")
    print("=" * 60)

    # Configure High DPI
    from PyQt6.QtGui import QGuiApplication
    if hasattr(Qt.HighDpiScaleFactorRoundingPolicy, 'PassThrough'):
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    # 1. Create Application (Required for Splash)
    app = QApplication(sys.argv)
    
    # 2. Show Splash
    from sj_das.ui.splash_screen import ModernSplashScreen
    splash = ModernSplashScreen()
    splash.show()
    
    # 3. Start Worker
    worker = StartupWorker()
    
    # State holder for window (to prevent GC)
    context = {'window': None}

    def on_loaded():
        """Called when worker finishes."""
        splash.show_message("Starting...")
        
        try:
            from sj_das.ui.modern_main_window import ModernMainWindow
            window = ModernMainWindow()
            context['window'] = window # Keep alive
            
            # Phase: Polish
            # Ensure layout is calculated before showing (prevents geometry glitches)
            window.ensurePolished()
            
            # Align splash and swap
            splash.finish(window)
            window.show()
            
        except Exception as e:
            with open("startup_debug.txt", "w") as f:
                f.write(traceback.format_exc())
            traceback.print_exc()
            QMessageBox.critical(None, "Startup Failed", str(e))
            sys.exit(1)

    worker.progress_update.connect(splash.show_message)
    worker.finished_ok.connect(on_loaded)
    worker.fatal_error.connect(lambda e: QMessageBox.critical(None, "Fatal Error", e))
    
    worker.start()

    # 4. Event Loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
