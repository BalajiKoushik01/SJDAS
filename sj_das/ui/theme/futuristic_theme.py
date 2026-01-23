"""
Futuristic Theme System for SJ-DAS (Qt-Compatible)
Cyberpunk/Neon aesthetics with Glassmorphism
"""
from typing import Dict

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication


class FuturisticTheme:
    """
    Futuristic neon theme with glassmorphism support.
    Cyberpunk aesthetic: Deep blues, Neon Cyan/Magenta accents.
    Qt-compatible (no CSS3 properties).
    """

    # Color Palette - Cyberpunk / Neon
    COLORS = {
        # Backgrounds (Deep Space) - Glass Theme
        # Deepest blue/black (darker for contrast)
        'bg_primary': '#0A0B12',
        'bg_secondary': '#10121C',    # Secondary panels (more transparent)
        'bg_elevated': '#16182A',     # Elevated surfaces (glass cards)
        'bg_hover': '#1E2238',        # Hover states (lighter glass)
        'bg_active': '#262B45',       # Active states
        'bg_input': '#0C0E16',        # Input fields (darker glass)

        # Borders (Neon Glows) - Glass Edges
        'border_subtle': '#2A2F4580',   # Subtle borders (semi-transparent)
        'border_glass': '#FFFFFF15',    # Glass edge highlight
        'border_focus': '#00F0FF',      # Neon Cyan Focus
        'border_accent': '#FF003C',     # Neon Red/Pink Accent

        # Text
        'text_primary': '#E0E6ED',    # Primary text (Off-white)
        'text_secondary': '#94A3B8',  # Secondary text (Blue-grey)
        'text_disabled': '#475569',   # Disabled text
        'text_bright': '#FFFFFF',     # Bright text

        # Accent Colors
        'accent_cyan': '#00F0FF',     # Primary Neon Cyan
        'accent_magenta': '#FF003C',  # Secondary Neon Magenta
        'accent_yellow': '#FFEE00',   # Warning/Highlight Neon Yellow
        'accent_purple': '#BC13FE',   # Creative Purple

        # Status Colors (Neon variants)
        'success': '#00FF9D',         # Neon Green
        'warning': '#FFEE00',         # Neon Yellow
        'error': '#FF003C',           # Neon Red
        'info': '#00F0FF',            # Neon Cyan

        # Canvas
        'canvas_bg': '#08090D',       # Almost black
        'canvas_grid': '#1F2937',     # Subtle grid
        'canvas_guide': '#00F0FF',    # Cyan guides
    }

    # Typography (Tech-inspired)
    FONTS = {
        'primary': 'Segoe UI',         # Reliable fallback
        'header': 'Orbitron',          # Sci-fi header (if available)
        'monospace': 'JetBrains Mono',  # Code font
        'fallback': 'Roboto, sans-serif'
    }

    FONT_SIZES = {
        'h1': 32,      # Page titles
        'h2': 24,      # Section headers
        'h3': 18,      # Subsections
        'body': 14,    # Regular text
        'small': 12,   # Captions
        'tiny': 10,    # Labels
    }

    # Spacing (Expanded for airy feel)
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
    }

    # Border Radius (Sharp & Soft mix)
    RADIUS = {
        'sm': 2,    # Sharp inner elements
        'md': 6,    # Standard buttons
        'lg': 12,   # Panels
        'xl': 16,   # Modal dialogs
    }

    @classmethod
    def get_stylesheet(cls) -> str:
        """
        Get complete futuristic application stylesheet (Qt-compatible).
        """
        c = cls.COLORS
        s = cls.SPACING
        r = cls.RADIUS

        return f"""
        /* Global Styles */
        * {{
            font-family: {cls.FONTS['primary']}, {cls.FONTS['fallback']};
            font-size: {cls.FONT_SIZES['body']}px;
            selection-background-color: {c['accent_cyan']};
            selection-color: #000000;
        }}

        QWidget {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
        }}

        /* Main Window */
        QMainWindow {{
            background-color: {c['bg_primary']};
        }}

        /* Glassmorphism Panels - Enhanced Glass Effect */
        QFrame {{
            background-color: {c['bg_secondary']}; /* Fallback */
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(22, 24, 42, 0.7),
                stop:1 rgba(16, 18, 28, 0.6)); /* Glass gradient */
            border: 1px solid rgba(255, 255, 255, 0.08); /* Glass edge */
            border-top: 1px solid rgba(255, 255, 255, 0.15); /* Top highlight */
            border-radius: {r['lg']}px;
        }}

        /* Glass Buttons - Frosted Effect */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(26, 29, 41, 0.8),
                stop:1 rgba(22, 25, 37, 0.7)); /* Glass gradient */
            color: {c['text_primary']};
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: 1px solid rgba(255, 255, 255, 0.2); /* Glass highlight */
            border-radius: {r['md']}px;
            padding: {s['sm']}px {s['md']}px;
            min-height: 32px;
        }}

        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(30, 34, 56, 0.9),
                stop:1 rgba(26, 30, 48, 0.8)); /* Brighter glass */
            border: 2px solid {c['accent_cyan']}; /* Neon glow border */
            border-top: 2px solid rgba(0, 240, 255, 0.6);
            color: {c['accent_cyan']};
        }}

        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 240, 255, 0.4),
                stop:1 rgba(0, 240, 255, 0.3));
            color: #FFFFFF;
            border: 2px solid {c['accent_cyan']};
        }}

        QPushButton:disabled {{
            color: {c['text_disabled']};
            background-color: {c['bg_secondary']};
            border: 1px solid {c['border_subtle']};
        }}

        /* Primary Action Button (Neon Gradient feel) */
        QPushButton[primary="true"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {c['accent_cyan']},
                stop:1 rgba(0, 240, 255, 0.8));
            color: #000000;
            border: 1px solid rgba(255, 255, 255, 0.3);
            font-weight: bold;
        }}

        QPushButton[primary="true"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #00FFFF,
                stop:1 {c['accent_cyan']});
            border: 2px solid #FFFFFF;
        }}

        /* Input Fields (Glass Tech) */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background: rgba(12, 14, 22, 0.6); /* Transparent glass */
            color: {c['accent_cyan']}; /* Matrix-like text */
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-bottom: 2px solid rgba(0, 240, 255, 0.3); /* Accent underline */
            border-radius: {r['sm']}px;
            padding: {s['sm']}px;
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {c['accent_cyan']};
            border-bottom: 2px solid {c['accent_cyan']};
            background: rgba(30, 34, 58, 0.7); /* Brighter glass on focus */
        }}

        /* Sliders (Neon Glow) */
        QSlider::groove:horizontal {{
            background: {c['bg_input']};
            height: 4px;
            border-radius: 2px;
        }}

        QSlider::handle:horizontal {{
            background: {c['accent_magenta']};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
            border: 2px solid {c['bg_primary']};
        }}

        QSlider::handle:horizontal:hover {{
            background: #FF4070; /* Lighter Magenta */
            border: 2px solid {c['text_bright']};
            width: 20px;
            height: 20px;
            margin: -8px 0;
        }}

        /* Scrollbars (Slim & Stealth) */
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background: rgba(0, 240, 255, 0.3);
            border-radius: 4px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: rgba(0, 240, 255, 0.6);
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 8px;
            margin: 0;
        }}

        QScrollBar::handle:horizontal {{
            background: rgba(0, 240, 255, 0.3);
            border-radius: 4px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: rgba(0, 240, 255, 0.6);
        }}

        /* Tab Widget (Futuristic Tabs) */
        QTabWidget::pane {{
            border: 1px solid {c['border_subtle']};
            background: {c['bg_secondary']};
            border-radius: {r['lg']}px;
        }}

        QTabBar::tab {{
            background: transparent;
            color: {c['text_secondary']};
            padding: {s['sm']}px {s['lg']}px;
            border-bottom: 2px solid transparent;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            color: {c['accent_cyan']};
            border-bottom: 2px solid {c['accent_cyan']};
        }}

        QTabBar::tab:hover {{
            color: {c['text_primary']};
            background-color: rgba(255, 255, 255, 0.05);
        }}

        /* Menus */
        QMenuBar {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
            border-bottom: 1px solid {c['border_subtle']};
        }}

        QMenuBar::item:selected {{
            background-color: {c['bg_hover']};
            color: {c['accent_cyan']};
        }}

        QMenu {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {r['md']}px;
        }}

        QMenu::item:selected {{
            background-color: {c['accent_purple']}; /* Creative accent check */
            color: #FFFFFF;
        }}

        /* Toolbars */
        QToolBar {{
            background-color: {c['bg_secondary']};
            border-bottom: 1px solid {c['border_subtle']};
            spacing: {s['sm']}px;
        }}

        QToolButton {{
            background-color: transparent;
            border-radius: {r['sm']}px;
            color: {c['text_primary']};
        }}

        QToolButton:hover {{
            background-color: {c['bg_hover']};
            border: 1px solid {c['accent_cyan']};
        }}

        QToolButton:checked {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0, 240, 255, 0.3),
                stop:1 rgba(0, 240, 255, 0.2));
            border: 1px solid {c['accent_cyan']};
            color: {c['accent_cyan']};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {c['bg_primary']};
            color: {c['text_secondary']};
            border-top: 1px solid {c['border_subtle']};
        }}

        /* Checkbox & Radio (Neon Indicators) */
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            background-color: {c['bg_input']};
            border: 1px solid {c['border_subtle']};
            border-radius: 2px;
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['accent_cyan']};
            border-color: {c['accent_cyan']};
        }}

        QRadioButton::indicator {{
            border-radius: 8px;
        }}

        QRadioButton::indicator:checked {{
            background-color: {c['accent_magenta']};
            border-color: {c['accent_magenta']};
        }}
        """

    @classmethod
    def apply_to_app(cls, app: QApplication):
        """
        Apply futuristic theme to application.
        """
        from PyQt6.QtGui import QColor
        from qfluentwidgets import Theme, setTheme, setThemeColor

        # 1. Apply QFluentWidgets Theme (Dark)
        setTheme(Theme.DARK)

        # 2. Force Neon Cyan Accent
        setThemeColor(QColor(cls.COLORS['accent_cyan']))

        # 3. Set global stylesheet
        app.setStyleSheet(cls.get_stylesheet())

        # 4. Set palette (Standard fallback)
        palette = QPalette()
        palette.setColor(
            QPalette.ColorRole.Window, QColor(
                cls.COLORS['bg_primary']))
        palette.setColor(
            QPalette.ColorRole.WindowText, QColor(
                cls.COLORS['text_primary']))
        palette.setColor(
            QPalette.ColorRole.Base, QColor(
                cls.COLORS['bg_input']))
        palette.setColor(
            QPalette.ColorRole.AlternateBase, QColor(
                cls.COLORS['bg_secondary']))
        palette.setColor(
            QPalette.ColorRole.ToolTipBase, QColor(
                cls.COLORS['bg_elevated']))
        palette.setColor(
            QPalette.ColorRole.ToolTipText, QColor(
                cls.COLORS['text_primary']))
        palette.setColor(
            QPalette.ColorRole.Text, QColor(
                cls.COLORS['text_primary']))
        palette.setColor(
            QPalette.ColorRole.Button, QColor(
                cls.COLORS['bg_elevated']))
        palette.setColor(
            QPalette.ColorRole.ButtonText, QColor(
                cls.COLORS['text_primary']))
        palette.setColor(
            QPalette.ColorRole.Highlight, QColor(
                cls.COLORS['accent_cyan']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#000000'))

        app.setPalette(palette)

        # 5. Determine Font
        font_family = cls.FONTS['primary']
        font = QFont(font_family, cls.FONT_SIZES['body'])
        app.setFont(font)
