"""
Pytest configuration for SJ-DAS.
Initializes QGuiApplication for tests requiring QtCore/QtGui.
"""
import sys

import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """
    Ensure QApplication exists for the entire test session.
    This is required for QImage, QPainter, and most Qt classes.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # No need to exec, just keeping the instance alive is enough for tests
    # Teardown logic if needed (usually not for simple unit tests)
