"""
Premium Theme System for SJ-DAS
World-class, professional color scheme and styling
"""
from typing import Dict

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication


class PremiumTheme:
    """
    Premium dark theme with professional aesthetics.
    Based on industry standards (VS Code, Adobe, Figma).
    """

    # Color Palette - Professional Dark Theme
    COLORS = {
        # Backgrounds
        'bg_primary': '#1E1E1E',      # Main background
        'bg_secondary': '#252526',    # Secondary panels
        'bg_elevated': '#2D2D30',     # Elevated surfaces
        'bg_hover': '#2A2D2E',        # Hover states
        'bg_active': '#37373D',       # Active states
        'bg_input': '#3C3C3C',        # Input fields

        # Borders
        'border_subtle': '#3E3E42',   # Subtle borders
        'border_focus': '#007ACC',    # Focus borders
        'border_accent': '#0078D4',   # Accent borders

        # Text
        'text_primary': '#CCCCCC',    # Primary text
        'text_secondary': '#969696',  # Secondary text
        'text_disabled': '#6E6E6E',   # Disabled text
        'text_bright': '#FFFFFF',     # Bright text (headers)

        # Accent Colors
        'accent_blue': '#0078D4',     # Primary accent
        'accent_purple': '#6B69D6',   # Secondary accent
        'accent_teal': '#00B7C3',     # Tertiary accent

        # Status Colors
        'success': '#107C10',         # Success green
        'warning': '#FFB900',         # Warning amber
        'error': '#D13438',           # Error red
        'info': '#0078D4',            # Info blue

        # Canvas
        'canvas_bg': '#1A1A1A',       # Canvas background
        'canvas_grid': '#2A2A2A',     # Grid lines
        'canvas_guide': '#0078D4',    # Guide lines
    }

    # Typography
    FONTS = {
        'primary': 'Segoe UI',
        'monospace': 'Cascadia Code',
        'fallback': '-apple-system, BlinkMacSystemFont, sans-serif'
    }

    FONT_SIZES = {
        'h1': 32,      # Page titles
        'h2': 24,      # Section headers
        'h3': 18,      # Subsections
        'body': 14,    # Regular text
        'small': 12,   # Captions
        'tiny': 10,    # Labels
    }

    # Spacing (8-point grid)
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
    }

    # Border Radius
    RADIUS = {
        'sm': 2,
        'md': 4,
        'lg': 8,
        'xl': 12,
    }

    # Shadows
    SHADOWS = {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
        'md': '0 2px 4px rgba(0, 0, 0, 0.4)',
        'lg': '0 4px 8px rgba(0, 0, 0, 0.5)',
        'xl': '0 8px 16px rgba(0, 0, 0, 0.6)',
    }

    @classmethod
    def get_stylesheet(cls) -> str:
        """
        Get complete application stylesheet.

        Returns:
            CSS stylesheet string
        """
        c = cls.COLORS
        s = cls.SPACING
        r = cls.RADIUS

        return f"""
        /* Global Styles */
        * {{
            font-family: {cls.FONTS['primary']}, {cls.FONTS['fallback']};
            font-size: {cls.FONT_SIZES['body']}px;
        }}

        QWidget {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
        }}

        /* Main Window */
        QMainWindow {{
            background-color: {c['bg_primary']};
        }}

        /* Panels */
        QFrame {{
            background-color: {c['bg_secondary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {r['md']}px;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {r['md']}px;
            padding: {s['sm']}px {s['md']}px;
            min-height: 32px;
        }}

        QPushButton:hover {{
            background-color: {c['bg_hover']};
            border-color: {c['border_focus']};
        }}

        QPushButton:pressed {{
            background-color: {c['bg_active']};
        }}

        QPushButton:disabled {{
            color: {c['text_disabled']};
            background-color: {c['bg_secondary']};
        }}

        /* Primary Button */
        QPushButton[primary="true"] {{
            background-color: {c['accent_blue']};
            color: {c['text_bright']};
            border: none;
        }}

        QPushButton[primary="true"]:hover {{
            background-color: #1084D8;
        }}

        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['bg_input']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {r['sm']}px;
            padding: {s['sm']}px;
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border-color: {c['border_focus']};
        }}

        /* Sliders */
        QSlider::groove:horizontal {{
            background: {c['bg_input']};
            height: 4px;
            border-radius: 2px;
        }}

        QSlider::handle:horizontal {{
            background: {c['accent_blue']};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}

        QSlider::handle:horizontal:hover {{
            background: #1084D8;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background: {c['bg_secondary']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background: {c['bg_elevated']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {c['bg_hover']};
        }}

        QScrollBar:horizontal {{
            background: {c['bg_secondary']};
            height: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background: {c['bg_elevated']};
            border-radius: 6px;
            min-width: 20px;
        }}

        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {c['border_subtle']};
            background: {c['bg_secondary']};
        }}

        QTabBar::tab {{
            background: {c['bg_secondary']};
            color: {c['text_secondary']};
            padding: {s['sm']}px {s['md']}px;
            border: 1px solid {c['border_subtle']};
            border-bottom: none;
        }}

        QTabBar::tab:selected {{
            background: {c['bg_primary']};
            color: {c['text_bright']};
            border-bottom: 2px solid {c['accent_blue']};
        }}

        QTabBar::tab:hover {{
            background: {c['bg_hover']};
        }}

        /* Menus */
        QMenuBar {{
            background-color: {c['bg_secondary']};
            color: {c['text_primary']};
            border-bottom: 1px solid {c['border_subtle']};
        }}

        QMenuBar::item:selected {{
            background-color: {c['bg_hover']};
        }}

        QMenu {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
        }}

        QMenu::item:selected {{
            background-color: {c['accent_blue']};
        }}

        /* Toolbars */
        QToolBar {{
            background-color: {c['bg_secondary']};
            border: none;
            spacing: {s['sm']}px;
            padding: {s['sm']}px;
        }}

        QToolButton {{
            background-color: transparent;
            color: {c['text_primary']};
            border: none;
            border-radius: {r['sm']}px;
            padding: {s['sm']}px;
        }}

        QToolButton:hover {{
            background-color: {c['bg_hover']};
        }}

        QToolButton:pressed {{
            background-color: {c['bg_active']};
        }}

        QToolButton:checked {{
            background-color: {c['accent_blue']};
            color: {c['text_bright']};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {c['bg_secondary']};
            color: {c['text_secondary']};
            border-top: 1px solid {c['border_subtle']};
        }}

        /* Tooltips */
        QToolTip {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
            padding: {s['sm']}px;
            border-radius: {r['sm']}px;
        }}

        /* Splitters */
        QSplitter::handle {{
            background-color: {c['border_subtle']};
        }}

        QSplitter::handle:hover {{
            background-color: {c['accent_blue']};
        }}

        /* Progress Bars */
        QProgressBar {{
            background-color: {c['bg_input']};
            border: none;
            border-radius: {r['sm']}px;
            text-align: center;
            color: {c['text_primary']};
        }}

        QProgressBar::chunk {{
            background-color: {c['accent_blue']};
            border-radius: {r['sm']}px;
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {c['bg_input']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {r['sm']}px;
            padding: {s['sm']}px;
        }}

        QComboBox:hover {{
            border-color: {c['border_focus']};
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        /* Spin Boxes */
        QSpinBox, QDoubleSpinBox {{
            background-color: {c['bg_input']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {r['sm']}px;
            padding: {s['sm']}px;
        }}

        /* Check Boxes */
        QCheckBox {{
            color: {c['text_primary']};
            spacing: {s['sm']}px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {c['border_subtle']};
            border-radius: {r['sm']}px;
            background-color: {c['bg_input']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['accent_blue']};
            border-color: {c['accent_blue']};
        }}

        /* Radio Buttons */
        QRadioButton {{
            color: {c['text_primary']};
            spacing: {s['sm']}px;
        }}

        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {c['border_subtle']};
            border-radius: 9px;
            background-color: {c['bg_input']};
        }}

        QRadioButton::indicator:checked {{
            background-color: {c['accent_blue']};
            border-color: {c['accent_blue']};
        }}
        """

    @classmethod
    def apply_to_app(cls, app: QApplication):
        """
        Apply theme to application.

        Args:
            app: QApplication instance
        """
        # Set stylesheet
        app.setStyleSheet(cls.get_stylesheet())

        # Set palette
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
                cls.COLORS['accent_blue']))
        palette.setColor(
            QPalette.ColorRole.HighlightedText, QColor(
                cls.COLORS['text_bright']))

        app.setPalette(palette)

        # Set default font
        font = QFont(cls.FONTS['primary'], cls.FONT_SIZES['body'])
        app.setFont(font)


# Global theme instance
_theme = PremiumTheme()


def get_theme() -> PremiumTheme:
    """Get global theme instance."""
    return _theme


def apply_premium_theme(app: QApplication):
    """
    Apply premium theme to application.

    Args:
        app: QApplication instance
    """
    PremiumTheme.apply_to_app(app)
