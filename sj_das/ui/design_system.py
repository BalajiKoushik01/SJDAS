"""
Professional Design System for SJ-DAS.
Consistent colors, typography, spacing, and component sizes.
"""

# ============================================================================
# TYPOGRAPHY
# ============================================================================

FONT_FAMILY_PRIMARY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

# Font Sizes (5-level hierarchy)
FONT_SIZE_HUGE = 18      # H1 - Main titles
FONT_SIZE_LARGE = 14     # H2 - Section headers
FONT_SIZE_NORMAL = 11    # Body - Normal text, buttons
FONT_SIZE_SMALL = 9      # Small - Labels, hints
FONT_SIZE_TINY = 8       # Tiny - Tool labels

# Font Weights
FONT_WEIGHT_BOLD = 700
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_NORMAL = 400

# ============================================================================
# SPACING (8px Grid System)
# ============================================================================

SPACING_TINY = 4         # Half-grid for fine-tuning
SPACING_SMALL = 8        # Standard spacing
SPACING_MEDIUM = 16      # Section spacing
SPACING_LARGE = 24       # Panel spacing
SPACING_HUGE = 32        # Major sections

# ============================================================================
# COMPONENT SIZES
# ============================================================================

# Toolbars
TOOLBAR_WIDTH = 72
SIDEBAR_WIDTH = 320
TOP_BAR_HEIGHT = 40
STATUS_BAR_HEIGHT = 24

# Buttons
BUTTON_HEIGHT = 32
BUTTON_PADDING_H = 16
BUTTON_PADDING_V = 8
TOOL_BUTTON_SIZE = 64

# Icons
ICON_SIZE_LARGE = 24
ICON_SIZE_MEDIUM = 16
ICON_SIZE_SMALL = 12

# Inputs
INPUT_HEIGHT = 28
INPUT_PADDING = 8

# Borders
BORDER_RADIUS_SMALL = 2
BORDER_RADIUS_MEDIUM = 4
BORDER_WIDTH = 1
SPLITTER_WIDTH = 2

# ============================================================================
# COLORS (Professional Dark Theme - VS Code Inspired)
# ============================================================================

# Backgrounds
COLOR_BG_PRIMARY = "#1E1E1E"      # Main background
COLOR_BG_SECONDARY = "#252526"    # Panels, sidebars
COLOR_BG_TERTIARY = "#2D2D2D"     # Toolbars, headers
COLOR_BG_ELEVATED = "#333333"     # Elevated elements
COLOR_BG_HOVER = "#2A2D2E"        # Hover state
COLOR_BG_ACTIVE = "#37373D"       # Active/pressed state

# Borders
COLOR_BORDER_PRIMARY = "#3E3E42"  # Main borders
COLOR_BORDER_SECONDARY = "#1a1a1a"  # Subtle borders
COLOR_BORDER_FOCUS = "#007ACC"    # Focus indicator

# Text
COLOR_TEXT_PRIMARY = "#CCCCCC"    # Main text
COLOR_TEXT_SECONDARY = "#858585"  # Secondary text
COLOR_TEXT_DISABLED = "#656565"   # Disabled text
COLOR_TEXT_INVERSE = "#FFFFFF"    # Text on dark backgrounds

# Accent (VS Code Blue)
COLOR_ACCENT = "#007ACC"
COLOR_ACCENT_HOVER = "#1C97EA"
COLOR_ACCENT_ACTIVE = "#005A9E"

# Status Colors
COLOR_SUCCESS = "#4EC9B0"
COLOR_WARNING = "#CE9178"
COLOR_ERROR = "#F48771"
COLOR_INFO = "#9CDCFE"

# ============================================================================
# TRANSITIONS
# ============================================================================

TRANSITION_FAST = "150ms"
TRANSITION_NORMAL = "250ms"
TRANSITION_SLOW = "350ms"

# ============================================================================
# SHADOWS
# ============================================================================

SHADOW_SMALL = "0 1px 3px rgba(0, 0, 0, 0.3)"
SHADOW_MEDIUM = "0 2px 8px rgba(0, 0, 0, 0.4)"
SHADOW_LARGE = "0 4px 16px rgba(0, 0, 0, 0.5)"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_button_style(variant="primary"):
    """Get consistent button styling."""
    if variant == "primary":
        return f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_TEXT_INVERSE};
                border: none;
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {BUTTON_PADDING_V}px {BUTTON_PADDING_H}px;
                font-size: {FONT_SIZE_NORMAL}px;
                font-family: "{FONT_FAMILY_PRIMARY}";
                min-height: {BUTTON_HEIGHT}px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_ACCENT_ACTIVE};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BG_ELEVATED};
                color: {COLOR_TEXT_DISABLED};
            }}
        """
    elif variant == "secondary":
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
                border: {BORDER_WIDTH}px solid {COLOR_BORDER_PRIMARY};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {BUTTON_PADDING_V}px {BUTTON_PADDING_H}px;
                font-size: {FONT_SIZE_NORMAL}px;
                font-family: "{FONT_FAMILY_PRIMARY}";
                min-height: {BUTTON_HEIGHT}px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BG_HOVER};
                border-color: {COLOR_ACCENT};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BG_ACTIVE};
            }}
        """
    return ""


def get_input_style():
    """Get consistent input styling."""
    return f"""
        QLineEdit, QSpinBox, QComboBox {{
            background-color: {COLOR_BG_PRIMARY};
            color: {COLOR_TEXT_PRIMARY};
            border: {BORDER_WIDTH}px solid {COLOR_BORDER_PRIMARY};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {SPACING_TINY}px {SPACING_SMALL}px;
            font-size: {FONT_SIZE_NORMAL}px;
            font-family: "{FONT_FAMILY_PRIMARY}";
            min-height: {INPUT_HEIGHT}px;
        }}
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border-color: {COLOR_BORDER_FOCUS};
        }}
        QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{
            background-color: {COLOR_BG_SECONDARY};
            color: {COLOR_TEXT_DISABLED};
        }}
    """
