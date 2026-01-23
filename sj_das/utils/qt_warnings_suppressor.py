# QFont Warning Suppression Script

import sys
import warnings


# Suppress QFont warnings
def suppress_qfont_warnings():
    """Suppress Qt font warnings that don't affect functionality."""
    import os
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'


# Call this before importing Qt
suppress_qfont_warnings()

if __name__ == "__main__":
    print("QFont warnings suppressed")
