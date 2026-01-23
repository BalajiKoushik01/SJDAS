"""
Modern Sleek Tool Options Bar for SJ-DAS.
Horizontal bar with context-sensitive tool options.
Premium indigo theme styling.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSlider, QSpinBox


class ModernToolOptionsBar(QFrame):
    """Sleek horizontal tool options bar (premium modern design)."""

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setObjectName("ModernToolOptionsBar")
        self.setFixedHeight(48)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        # Tool name label
        self.tool_label = QLabel("Brush Tool")
        self.tool_label.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        self.tool_label.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(self.tool_label)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("background-color: #3730A3;")
        sep1.setFixedWidth(1)
        layout.addWidget(sep1)

        # Size control
        size_label = QLabel("Size:")
        size_label.setFont(QFont("Inter", 10))
        size_label.setStyleSheet("color: #94A3B8;")
        layout.addWidget(size_label)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.setValue(10)
        self.size_slider.setFixedWidth(120)
        layout.addWidget(self.size_slider)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 100)
        self.size_spin.setValue(10)
        self.size_spin.setFixedWidth(60)
        layout.addWidget(self.size_spin)

        # Connect size controls
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.size_slider.setValue)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet("background-color: #3730A3;")
        sep2.setFixedWidth(1)
        layout.addWidget(sep2)

        # Opacity control
        opacity_label = QLabel("Opacity:")
        opacity_label.setFont(QFont("Inter", 10))
        opacity_label.setStyleSheet("color: #94A3B8;")
        layout.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setFixedWidth(100)
        layout.addWidget(self.opacity_slider)

        self.opacity_label = QLabel("100%")
        self.opacity_label.setFont(QFont("Inter", 10))
        self.opacity_label.setStyleSheet("color: #E2E8F0;")
        self.opacity_label.setFixedWidth(40)
        layout.addWidget(self.opacity_label)

        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )

        layout.addStretch()

        # Modern styling
        self.setStyleSheet("""
            #ModernToolOptionsBar {
                background-color: #252233;
                border-bottom: 1px solid #3730A3;
            }
            QSlider::groove:horizontal {
                background-color: #3730A3;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #6366F1;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #818CF8;
            }
            QSpinBox {
                background-color: #2D2A3E;
                color: #E2E8F0;
                border: 1px solid #3730A3;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QSpinBox:focus {
                border-color: #6366F1;
            }
        """)

    def set_tool(self, tool_name):
        """Update tool name display."""
        self.tool_label.setText(tool_name)
