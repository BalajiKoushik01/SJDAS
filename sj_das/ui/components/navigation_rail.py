"""
Navigation Rail Component for SJDAS
Implements a collapsible vertical tool rail (Left Sidebar).
"""
import logging
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget, QSizePolicy
from qfluentwidgets import (FluentIcon as FIF, TransparentToolButton, 
                            ToolTipFilter, NavigationItemPosition)

logger = logging.getLogger("SJ_DAS.NavigationRail")

class ToolRailGroup(QWidget):
    """A group of vertical tools."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

class NavigationRail(QFrame):
    """
    Professional Collapsible Vertical Tool Rail.
    Replaces the standard vertical toolbar with a more organized, group-based system.
    """
    tool_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navigationRail")
        self.setFixedWidth(50) # Standard collapsed width
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 10, 4, 10)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Style context
        self.setStyleSheet("""
            QFrame#navigationRail {
                background-color: #111827; 
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

    def add_tool(self, tool_id, icon, tooltip=""):
        btn = TransparentToolButton(icon, self)
        btn.setFixedSize(40, 40)
        btn.setIconSize(QSize(20, 20))
        btn.setToolTip(tooltip)
        btn.installEventFilter(ToolTipFilter(btn))
        btn.clicked.connect(lambda: self.tool_triggered.emit(tool_id))
        self.main_layout.addWidget(btn)

    def add_separator(self):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); margin: 5px 0;")
        self.main_layout.addWidget(line)

    def add_stretch(self):
        self.main_layout.addStretch()
