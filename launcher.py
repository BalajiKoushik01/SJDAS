
from sj_das.ui.modern_main_window import create_modern_app
from PyQt6.QtWidgets import QMessageBox
import os
import sys
import traceback

# Suppress Qt font warnings (cosmetic only, doesn't affect functionality)
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false;qt.gui.font.*=false'


# =============================================================================
# SJ-DAS Standard Launcher
# =============================================================================
# This script is the official entry point for the SJ-DAS (Pro) Application.
# It sets up pathing, exception handling, and initializes the Modern Fluent UI.
# =============================================================================

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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


def main():
    """
    Main Entry Point for the SJ-DAS (Pro) Application.

    Responsibilities:
    1. Register the global exception hook to capture crashes.
    2. Print startup banner for CLI visibility.
    3. Initialize the Modern Fluent UI (`create_modern_app`).
    """
    # Register Crash Handler
    sys.excepthook = exception_hook

    print("=" * 60)
    print("   SJ-DAS Pro | Design Automation System")
    print("   Version: 2025.1.0 (Fluent Edition)")
    print("=" * 60)
    print("   Initializing AI Subsystems...")

    # Configure High DPI Scaling (Fixes font size <= 0 warnings)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QGuiApplication
    if hasattr(Qt.HighDpiScaleFactorRoundingPolicy, 'PassThrough'):
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    # Launch App
    create_modern_app()


if __name__ == "__main__":
    main()
