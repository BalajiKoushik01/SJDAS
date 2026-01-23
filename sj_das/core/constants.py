"""
Constants and configuration for SJ-DAS application.

Centralizes all magic numbers, timeouts, and configuration values
to improve maintainability and reduce errors.
"""

from typing import Final


# ===== UI CONSTANTS =====
class UIConstants:
    """UI layout and styling constants."""

    # Dimensions
    STATUS_BAR_HEIGHT: Final[int] = 32
    TOOL_STRIP_WIDTH: Final[int] = 50
    TOOLBAR_ICON_SIZE: Final[int] = 32  # Added for validation
    PANEL_MIN_WIDTH: Final[int] = 250
    PANEL_MAX_WIDTH: Final[int] = 400

    # Spacing
    LAYOUT_MARGIN: Final[int] = 8
    LAYOUT_SPACING: Final[int] = 4
    BUTTON_PADDING: Final[int] = 8

    # Sizes
    ICON_SIZE_SMALL: Final[int] = 16
    ICON_SIZE_MEDIUM: Final[int] = 24
    ICON_SIZE_LARGE: Final[int] = 32

    # Animation durations (ms)
    ANIMATION_FAST: Final[int] = 150
    ANIMATION_NORMAL: Final[int] = 250
    ANIMATION_SLOW: Final[int] = 400

    # Timeouts (ms)
    TOOLTIP_DURATION: Final[int] = 2000
    NOTIFICATION_DURATION: Final[int] = 3000
    ERROR_NOTIFICATION_DURATION: Final[int] = 5000


# ===== EDITOR CONSTANTS =====
class EditorConstants:
    """Image editor configuration."""

    # Brush settings
    BRUSH_SIZE_MIN: Final[int] = 1
    BRUSH_SIZE_MAX: Final[int] = 200
    BRUSH_SIZE_DEFAULT: Final[int] = 10

    OPACITY_MIN: Final[float] = 0.0
    OPACITY_MAX: Final[float] = 1.0
    OPACITY_DEFAULT: Final[float] = 1.0

    HARDNESS_MIN: Final[float] = 0.0
    HARDNESS_MAX: Final[float] = 1.0
    HARDNESS_DEFAULT: Final[float] = 0.8

    # Image constraints
    MAX_IMAGE_WIDTH: Final[int] = 8192
    MAX_IMAGE_HEIGHT: Final[int] = 8192
    MAX_IMAGE_SIZE_MB: Final[int] = 100

    # Zoom
    ZOOM_MIN: Final[float] = 0.1
    ZOOM_MAX: Final[float] = 10.0
    ZOOM_STEP: Final[float] = 0.1

    # Undo/Redo
    MAX_UNDO_STEPS: Final[int] = 50


# ===== AI CONSTANTS =====
class AIConstants:
    """AI processing configuration."""

    # Timeouts (seconds)
    AI_PROCESSING_TIMEOUT: Final[int] = 30
    AI_CHECK_INTERVAL: Final[int] = 10

    # Limits
    MAX_VARIATIONS: Final[int] = 10
    MAX_PROMPT_LENGTH: Final[int] = 500

    # Model settings
    DEFAULT_TEMPERATURE: Final[float] = 0.7
    DEFAULT_TOP_P: Final[float] = 0.9


# ===== FILE CONSTANTS =====
class FileConstants:
    """File handling configuration."""

    # Supported formats
    SUPPORTED_IMAGE_FORMATS: Final[tuple] = (
        '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif'
    )

    SUPPORTED_EXPORT_FORMATS: Final[tuple] = (
        '.bmp', '.png', '.jpg'
    )

    # Size limits
    MAX_FILE_SIZE_MB: Final[int] = 100

    # Paths
    DEFAULT_EXPORT_DIR: Final[str] = "exports"
    DEFAULT_PROJECT_DIR: Final[str] = "projects"
    CACHE_DIR: Final[str] = ".cache"


# ===== PERFORMANCE CONSTANTS =====
class PerformanceConstants:
    """Performance tuning configuration."""

    # Cache sizes
    IMAGE_CACHE_SIZE: Final[int] = 10
    THUMBNAIL_CACHE_SIZE: Final[int] = 100

    # Thread pool
    MAX_WORKER_THREADS: Final[int] = 4

    # Rendering
    TARGET_FPS: Final[int] = 60
    FRAME_TIME_MS: Final[int] = 16  # 1000/60

    # Memory
    MAX_MEMORY_MB: Final[int] = 2048
    MEMORY_WARNING_THRESHOLD_MB: Final[int] = 1536


# ===== VALIDATION CONSTANTS =====
class ValidationConstants:
    """Input validation rules."""

    # String lengths
    MAX_FILENAME_LENGTH: Final[int] = 255
    MAX_PROJECT_NAME_LENGTH: Final[int] = 100
    MAX_LAYER_NAME_LENGTH: Final[int] = 50

    # Numeric ranges
    MIN_TOLERANCE: Final[int] = 0
    MAX_TOLERANCE: Final[int] = 255

    MIN_THREAD_COUNT: Final[int] = 1
    MAX_THREAD_COUNT: Final[int] = 256


# ===== COLOR CONSTANTS =====
class ColorConstants:
    """Color palette and theme colors."""

    # Theme colors (Dark)
    BG_PRIMARY: Final[str] = '#0F172A'
    BG_SECONDARY: Final[str] = '#1E293B'
    BG_ELEVATED: Final[str] = '#334155'
    BG_HOVER: Final[str] = '#475569'

    BORDER_SUBTLE: Final[str] = '#334155'
    BORDER_ACCENT: Final[str] = '#6366F1'

    TEXT_PRIMARY: Final[str] = '#E2E8F0'
    TEXT_SECONDARY: Final[str] = '#94A3B8'
    TEXT_MUTED: Final[str] = '#64748B'

    ACCENT_PRIMARY: Final[str] = '#6366F1'
    ACCENT_SECONDARY: Final[str] = '#8B5CF6'

    SUCCESS: Final[str] = '#10B981'
    WARNING: Final[str] = '#F59E0B'
    ERROR: Final[str] = '#EF4444'
    INFO: Final[str] = '#3B82F6'


# ===== LOGGING CONSTANTS =====
class LoggingConstants:
    """Logging configuration."""

    LOG_FORMAT: Final[str] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT: Final[str] = '%Y-%m-%d %H:%M:%S'

    MAX_LOG_FILE_SIZE_MB: Final[int] = 10
    MAX_LOG_FILES: Final[int] = 5


# ===== ERROR MESSAGES =====
class ErrorMessages:
    """Standardized error messages."""

    # File errors
    FILE_NOT_FOUND: Final[str] = "File not found: {path}"
    FILE_TOO_LARGE: Final[str] = "File too large: {size}MB (max {max}MB)"
    INVALID_FORMAT: Final[str] = "Invalid file format: {format}"
    PERMISSION_DENIED: Final[str] = "Permission denied: {path}"

    # Image errors
    IMAGE_LOAD_FAILED: Final[str] = "Failed to load image: {reason}"
    IMAGE_TOO_LARGE: Final[str] = "Image too large: {width}x{height} (max {max}x{max})"
    INVALID_IMAGE: Final[str] = "Invalid or corrupted image file"

    # Input errors
    INVALID_INPUT: Final[str] = "Invalid input: {field} must be {constraint}"
    OUT_OF_RANGE: Final[str] = "{field} must be between {min} and {max}, got {value}"

    # AI errors
    AI_TIMEOUT: Final[str] = "AI processing timed out after {timeout}s"
    AI_FAILED: Final[str] = "AI processing failed: {reason}"

    # General errors
    OPERATION_FAILED: Final[str] = "Operation failed: {operation}"
    UNEXPECTED_ERROR: Final[str] = "Unexpected error: {error}"
