"""
Custom Exception Hierarchy for SJ-DAS
Provides meaningful, context-rich exceptions for better error handling
"""


class SJDASException(Exception):
    """Base exception for all SJ-DAS errors."""

    def __init__(self, message: str, context: dict = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

    def __str__(self):
        if self.context:
            return f"{self.message} | Context: {self.context}"
        return self.message


# ============================================================================
# AI Engine Exceptions
# ============================================================================

class AIEngineException(SJDASException):
    """Base exception for AI engine errors."""
    pass


class ModelLoadError(AIEngineException):
    """Raised when an AI model fails to load."""
    pass


class ModelInferenceError(AIEngineException):
    """Raised when model inference fails."""
    pass


class InsufficientMemoryError(AIEngineException):
    """Raised when there's not enough memory for AI operations."""
    pass


# ============================================================================
# Image Processing Exceptions
# ============================================================================

class ImageProcessingException(SJDASException):
    """Base exception for image processing errors."""
    pass


class InvalidImageError(ImageProcessingException):
    """Raised when image is invalid or corrupted."""
    pass


class UnsupportedFormatError(ImageProcessingException):
    """Raised when image format is not supported."""
    pass


class ImageTooLargeError(ImageProcessingException):
    """Raised when image exceeds size limits."""
    pass


# ============================================================================
# Loom/Manufacturing Exceptions
# ============================================================================

class LoomException(SJDASException):
    """Base exception for loom-related errors."""
    pass


class InvalidWeaveError(LoomException):
    """Raised when weave structure is invalid."""
    pass


class ExportError(LoomException):
    """Raised when loom export fails."""
    pass


class QuantizationError(ImageProcessingException):
    """Raised when color quantization fails."""
    pass


# ============================================================================
# UI Exceptions
# ============================================================================

class UIException(SJDASException):
    """Base exception for UI errors."""
    pass


class InvalidOperationError(UIException):
    """Raised when operation is invalid in current state."""
    pass


# ============================================================================
# File I/O Exceptions
# ============================================================================

class FileOperationException(SJDASException):
    """Base exception for file operations."""
    pass


class FileNotFoundError(FileOperationException):
    """Raised when file doesn't exist."""
    pass


class FileWriteError(FileOperationException):
    """Raised when file write fails."""
    pass


class CorruptedFileError(FileOperationException):
    """Raised when file is corrupted."""
    pass
