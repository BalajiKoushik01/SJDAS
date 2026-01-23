"""
Qt Warning Suppressor for Professional Output
Suppresses cosmetic Qt warnings that don't affect functionality
"""
import os
import sys
import warnings


def suppress_qt_warnings():
    """
    Suppress Qt warnings for cleaner console output.
    These warnings are cosmetic and don't affect functionality.
    """
    # Suppress Qt warnings
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

    # Suppress Python warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*QFont.*")

    # Redirect Qt messages to null on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX
            kernel32.SetErrorMode(0x0001 | 0x0002 | 0x8000)
        except BaseException:
            pass


def setup_professional_logging():
    """
    Configure logging for professional output.
    """
    import logging

    # Set up clean logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Suppress verbose libraries
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    return logging.getLogger("SJ_DAS")
