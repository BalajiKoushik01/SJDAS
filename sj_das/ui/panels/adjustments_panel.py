from PyQt6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                             QToolButton, QVBoxLayout, QWidget)


class AdjustmentsPanel(QWidget):
    def __init__(self, designer_view, parent=None):
        super().__init__(parent)
        self.designer = designer_view

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(30)
        header.setStyleSheet(
            "background-color: #333; border-bottom: 1px solid #444;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 10, 0)
        h_layout.addWidget(QLabel("Adjustments"))
        layout.addWidget(header)

        # Grid Area
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: #2b2b2b;")
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(10)

        # Icons (Text for now, should be icons)
        self.add_adj_btn(grid_layout, "☀", "Brightness", 0, 0,
                         self.designer.apply_brightness_contrast)
        self.add_adj_btn(grid_layout, "◐", "Levels", 0, 1, None)  # Placeholder
        self.add_adj_btn(grid_layout, "⌇", "Curves", 0, 2, None)  # Placeholder
        self.add_adj_btn(grid_layout, "🎨", "Hue/Sat", 1, 0,
                         self.designer.apply_hue_saturation)
        self.add_adj_btn(grid_layout, "◆", "Vibrance", 1, 1, None)
        self.add_adj_btn(grid_layout, "BW", "Black & White", 1, 2, None)

        # Add Filter Buttons too?
        self.add_adj_btn(grid_layout, "💧", "Blur", 2, 0,
                         self.designer.apply_filter_gaussian_blur)
        self.add_adj_btn(grid_layout, "▲", "Sharpen", 2, 1,
                         self.designer.apply_filter_sharpen)

        layout.addWidget(grid_frame)
        layout.addStretch()

    def add_adj_btn(self, layout, text, tooltip, r, c, callback):
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setFixedSize(40, 40)
        btn.setStyleSheet("""
            QToolButton {
                background-color: #444;
                border-radius: 4px;
                color: white;
                font-size: 16px;
            }
            QToolButton:hover { background-color: #555; }
        """)
        if callback:
            btn.clicked.connect(callback)
        else:
            btn.setEnabled(False)  # Placeholder

        layout.addWidget(btn, r, c)
