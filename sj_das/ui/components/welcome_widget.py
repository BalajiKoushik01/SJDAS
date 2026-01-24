
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGraphicsDropShadowEffect)
from qfluentwidgets import PrimaryPushButton, HyperlinkButton, FluentIcon as FIF

class WelcomeWidget(QWidget):
    """
    Premium Welcome Screen for the Empty State.
    Displayed when no canvas is open.
    """
    
    action_new = pyqtSignal()
    action_open = pyqtSignal()
    action_recent = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.opacity_effect = None # Placeholder
        
    def showEvent(self, event):
        """Trigger entrance animation."""
        super().showEvent(event)
        self._animate_entrance()

    def _animate_entrance(self):
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
        
        # Reset position (simple slide up)
        # We need to animate the content layout container usually, but let's animate the card
        card = self.findChild(QFrame, "card")
        if card:
            # Opacity
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            self.opacity_effect = QGraphicsOpacityEffect(card)
            card.setGraphicsEffect(self.opacity_effect)
            
            self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.anim.setDuration(800)
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(1.0)
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim.start()

    def init_ui(self):
        # ... (Rest of existing init code moved here? No, let's keep __init__ logic but verify indentation)
        pass 

    def _setup_styles(self): # Helper to keep init clean
        self.setStyleSheet("""
            WelcomeWidget {
                background-color: #1E1E1E;
            }
            QLabel#heroTitle {
                font-size: 32px;
                font-weight: bold;
                color: #FFFFFF;
                font-family: 'Segoe UI Display', 'Inter', sans-serif;
            }
            QLabel#subTitle {
                font-size: 16px;
                color: #A0A0A0;
            }
            QFrame#card {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 12px;
            }
            QPushButton#actionBtn {
                text-align: left;
                padding: 12px 20px;
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                color: #E0E0E0;
                font-size: 14px;
            }
            QPushButton#actionBtn:hover {
                background-color: #3D3D3D;
                border: 1px solid #505050;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        # 1. Hero Section
        hero_layout = QVBoxLayout()
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.setSpacing(8)
        
        icon_lbl = QLabel("✨") # Or an image
        icon_lbl.setStyleSheet("font-size: 64px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("SJ-DAS Professional")
        title.setObjectName("heroTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub = QLabel("AI-Powered Textile Design Suite")
        sub.setObjectName("subTitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hero_layout.addWidget(icon_lbl)
        hero_layout.addWidget(title)
        hero_layout.addWidget(sub)
        layout.addLayout(hero_layout)

        # 2. Actions Card
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(400)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # New Project
        btn_new = QPushButton("  New Project...")
        btn_new.setObjectName("actionBtn")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self.action_new.emit)
        card_layout.addWidget(btn_new)

        # Open Project
        btn_open = QPushButton("  Open Existing...")
        btn_open.setObjectName("actionBtn")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(self.action_open.emit)
        card_layout.addWidget(btn_open)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #404040;")
        card_layout.addWidget(line)

        # Recent (Placeholder)
        lbl_recent = QLabel("Recent Files")
        lbl_recent.setStyleSheet("color: #808080; font-weight: bold; font-size: 12px; text-transform: uppercase;")
        card_layout.addWidget(lbl_recent)
        
        # Mock Recents
        for name in ["Saree_Design_v4.png", "Floral_Motif_Set.das", "Kanchipuram_Draft.png"]:
            btn = HyperlinkButton(url="", text=name, parent=self)
            btn.clicked.connect(lambda ch, n=name: self.action_recent.emit(n))
            card_layout.addWidget(btn)

        layout.addWidget(card)
