"""
Custom exception hierarchy for SJ-DAS application.

This module defines domain-specific exceptions that provide clear,
actionable error messages and enable precise error handling throughout
the application.
"""

from typing import Any


class SJDASException(Exception):
    """
    Base exception for all SJ-DAS specific errors.

    All custom exceptions should inherit from this class to enable
    catch-all error handling when needed.
    """

    def __init__(self, message: str,
                 details: "Optional[dict[str, Any]]" = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(
                f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class DesignImportError(SJDASException):
    """
    Raised when design import fails.

    Examples:
        - Unsupported file format
        - Corrupted image data
        - Invalid dimensions
    """
    pass


class AIProcessingError(SJDASException):
    """
    Raised when AI/ML processing fails.

    Examples:
        - Model not loaded
        - Invalid input dimensions
        - Inference timeout
    """
    pass


class LoomConfigError(SJDASException):
    """
    Raised when loom configuration is invalid.

    Examples:
        - Invalid hook count
        - Unsupported weave pattern
        - Incompatible yarn specifications
    """
    pass


class ExportError(SJDASException):
    """
    Raised when design export fails.

    Examples:
        - Write permission denied
        - Invalid export format
        - BMP encoding error
    """
    pass


class ValidationError(SJDASException):
    """
    Raised when data validation fails.

    Examples:
        - Invalid color palette
        - Out-of-range values
        - Missing required fields
    """
    pass


class ResourceNotFoundError(SJDASException):
    """
    Raised when a required resource is not found.

    Examples:
        - Missing model weights
        - Asset file not found
        - Configuration file missing
    """
    pass


class WeaveGenerationError(SJDASException):
    """
    Raised when weave pattern generation fails.

    Examples:
        - Invalid weave structure
        - Incompatible yarn configuration
        - Pattern generation timeout
    """
    pass
