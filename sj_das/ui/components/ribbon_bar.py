"""
Ribbon Bar Component for SJDAS
Implements a category-based tool navigation system (Home, Design, AI, Textile).
"""
import logging
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QStackedWidget
from qfluentwidgets import Pivot, TransparentToolButton, ToolTipFilter

logger = logging.getLogger("SJ_DAS.RibbonBar")

class RibbonCategory(QFrame):
    """A single category (tab) in the Ribbon containing grouped tools."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 2, 5, 2)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def add_tool(self, text, icon, callback, tooltip=""):
        btn = TransparentToolButton(icon, self)
        btn.setText(text)
        
        # Professional Ribbon Style: Icon over Text
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Flexible width to prevent text overlapping
        btn.setMinimumWidth(95)
        btn.setFixedHeight(80)
        btn.setIconSize(QSize(24, 24))
        
        # Discard the 'checked' boolean argument from the clicked signal
        # to prevent TypeError in methods that only accept 'self'.
        btn.clicked.connect(lambda: callback())
        if tooltip:
            btn.setToolTip(tooltip)
            btn.installEventFilter(ToolTipFilter(btn))
        
        # Improved styling for readability and professional feel
        btn.setStyleSheet("""
            ToolButton { 
                font-size: 10px; 
                font-weight: 500;
                padding: 8px 4px 4px 4px; 
                border-radius: 6px;
                color: #CBD5E1;
            }
            ToolButton:hover {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)
        self.layout.addWidget(btn)

    def add_separator(self):
        line = QFrame()
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); margin: 8px 2px;")
        self.layout.addWidget(line)

class RibbonBar(QFrame):
    """
    The main Ribbon interface.
    Consists of a Pivot (Tabs) and a StackedWidget (Tool Groups).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ribbonBar")
        self.setFixedHeight(110) # Pivot (~40px) + Stack (~70px)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Pivot (Tabs)
        self.pivot = Pivot(self)
        self.main_layout.addWidget(self.pivot)

        # 2. Stacked Widget (Sub-toolbars)
        self.stack = QStackedWidget(self)
        self.main_layout.addWidget(self.stack)

        # Style context
        self.setStyleSheet("""
            QFrame#ribbonBar {
                background-color: #1E293B;
                border_bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

    def add_category(self, routeKey, text, icon=None):
        """Adds a new category and its corresponding page."""
        page = RibbonCategory(self.stack)
        self.stack.addWidget(page)
        self.pivot.addItem(
            routeKey=routeKey,
            text=text,
            onClick=lambda: self.stack.setCurrentWidget(page),
            icon=icon
        )
        return page

    def finalize(self):
        """Sets the default page."""
        if self.stack.count() > 0 and self.pivot.items:
            # Use the first routeKey
            first_key = list(self.pivot.items.keys())[0]
            self.pivot.setCurrentItem(first_key)
            self.stack.setCurrentIndex(0)
