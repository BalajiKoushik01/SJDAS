"""
Type definitions and protocols for SJ-DAS.

Provides type hints, protocols, and type aliases for better
type safety and IDE support throughout the application.
"""

from collections.abc import Callable
from typing import Any, Optional, Protocol, Union

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor, QImage

# ===== Type Aliases =====

# Color can be QColor or RGB tuple
ColorType = Union[QColor, tuple[int, int, int], tuple[int, int, int, int]]

# Image dimensions
Dimensions = tuple[int, int]  # (width, height)

# Rectangle coordinates
RectCoords = tuple[int, int, int, int]  # (x, y, width, height)

# Point coordinates
PointCoords = tuple[int, int]  # (x, y)

# File path
FilePath = Union[str, 'Path']

# Loom specifications
LoomSpecs = dict[str, Union[int, str, float]]


# ===== Protocols =====

class ImageEditor(Protocol):
    """
    Protocol for image editor widgets.

    Defines the interface that all image editors must implement.
    Allows for dependency injection and easier testing.
    """

    def set_image(self, image: QImage) -> None:
        """Set the current image."""
        ...

    def get_image(self) -> QImage:
        """Get the current image."""
        ...

    def update_region(self, rect: QRect) -> None:
        """Update a specific region of the canvas."""
        ...


class ValidationProvider(Protocol):
    """
    Protocol for validation providers.

    Defines the interface for input validation.
    """

    def validate(self, value: Any) -> bool:
        """Validate a value."""
        ...

    def get_error_message(self) -> str:
        """Get validation error message."""
        ...


class FeatureModule(Protocol):
    """
    Protocol for feature modules.

    All feature modules should implement this interface for
    consistent integration with the main application.
    """

    def initialize(self) -> None:
        """Initialize the feature module."""
        ...

    def cleanup(self) -> None:
        """Cleanup resources used by the feature."""
        ...

    def is_available(self) -> bool:
        """Check if feature is available."""
        ...


class AIModel(Protocol):
    """
    Protocol for AI models.

    Defines the interface for AI processing models.
    """

    def predict(self, image: QImage) -> Any:
        """Make a prediction on an image."""
        ...

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        ...


class ThemeProvider(Protocol):
    """
    Protocol for theme providers.

    Defines the interface for theme management.
    """

    def get_color(self, color_name: str) -> QColor:
        """Get a color from the current theme."""
        ...

    def apply_theme(self, theme_name: str) -> None:
        """Apply a theme."""
        ...


# ===== Callback Types =====

# Progress callback: (current, total, message)
ProgressCallback = Optional[Callable[[int, int, str], None]]

# Error callback: (error_message, details)
ErrorCallback = Optional[Callable[[str, dict[str, Any]], None]]

# Success callback: (result)
SuccessCallback = Optional[Callable[[Any], None]]


# ===== Enums (as TypeAlias for now) =====

ToolType = str  # 'select', 'brush', 'eraser', etc.
BlendMode = str  # 'normal', 'multiply', 'screen', etc.
ExportFormat = str  # 'bmp', 'png', 'jpg'
