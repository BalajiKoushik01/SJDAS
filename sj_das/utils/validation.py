"""
Input validation utilities for SJ-DAS.

Provides comprehensive validation for all user inputs to prevent
errors, crashes, and security vulnerabilities.
"""

import os
from pathlib import Path

from PyQt6.QtGui import QImage

from sj_das.core.constants import (EditorConstants, ErrorMessages,
                                   FileConstants, ValidationConstants)
from sj_das.core.exceptions import ValidationError


class InputValidator:
    """Validates user inputs across the application."""

    @staticmethod
    def validate_brush_size(size: int) -> int:
        """
        Validate brush size.

        Args:
            size: Brush size to validate

        Returns:
            Validated brush size

        Raises:
            ValidationError: If size is invalid
        """
        if not isinstance(size, int):
            raise ValidationError(
                f"Brush size must be integer, got {type(size).__name__}"
            )

        if not EditorConstants.BRUSH_SIZE_MIN <= size <= EditorConstants.BRUSH_SIZE_MAX:
            raise ValidationError(
                ErrorMessages.OUT_OF_RANGE.format(
                    field="Brush size",
                    min=EditorConstants.BRUSH_SIZE_MIN,
                    max=EditorConstants.BRUSH_SIZE_MAX,
                    value=size
                )
            )

        return size

    @staticmethod
    def validate_opacity(opacity: float) -> float:
        """
        Validate opacity value.

        Args:
            opacity: Opacity to validate (0.0-1.0)

        Returns:
            Validated opacity

        Raises:
            ValidationError: If opacity is invalid
        """
        if not isinstance(opacity, (int, float)):
            raise ValidationError(
                f"Opacity must be numeric, got {type(opacity).__name__}"
            )

        opacity = float(opacity)

        if not EditorConstants.OPACITY_MIN <= opacity <= EditorConstants.OPACITY_MAX:
            raise ValidationError(
                ErrorMessages.OUT_OF_RANGE.format(
                    field="Opacity",
                    min=EditorConstants.OPACITY_MIN,
                    max=EditorConstants.OPACITY_MAX,
                    value=opacity
                )
            )

        return opacity

    @staticmethod
    def validate_file_path(
        file_path: str | Path,
        must_exist: bool = True,
        allowed_extensions: tuple | None = None
    ) -> Path:
        """
        Validate file path.

        Args:
            file_path: Path to validate
            must_exist: Whether file must exist
            allowed_extensions: Tuple of allowed extensions (e.g., ('.png', '.jpg'))

        Returns:
            Validated Path object

        Raises:
            ValidationError: If path is invalid
        """
        if not file_path:
            raise ValidationError("File path cannot be empty")

        try:
            path = Path(file_path).resolve()
        except Exception as e:
            raise ValidationError(f"Invalid file path: {e}")

        # Check if file exists
        if must_exist and not path.exists():
            raise ValidationError(
                ErrorMessages.FILE_NOT_FOUND.format(path=path)
            )

        # Check extension
        if allowed_extensions and path.suffix.lower() not in allowed_extensions:
            raise ValidationError(
                ErrorMessages.INVALID_FORMAT.format(format=path.suffix)
            )

        # Check file size if exists
        if path.exists() and path.is_file():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > FileConstants.MAX_FILE_SIZE_MB:
                raise ValidationError(
                    ErrorMessages.FILE_TOO_LARGE.format(
                        size=f"{size_mb:.1f}",
                        max=FileConstants.MAX_FILE_SIZE_MB
                    )
                )

        return path

    @staticmethod
    def validate_image(image) -> bool:
        """
        Validate image (supports both numpy arrays and QImage).

        Args:
            image: Image to validate (numpy array or QImage)

        Returns:
            True if valid, False otherwise
        """
        import numpy as np

        # Handle numpy arrays
        if isinstance(image, np.ndarray):
            if image.size == 0:
                return False
            if len(image.shape) not in [2, 3]:
                return False
            if len(image.shape) == 3 and image.shape[2] not in [1, 3, 4]:
                return False
            return True

        # Handle QImage
        if hasattr(image, 'isNull'):
            if image.isNull():
                return False
            if image.width() == 0 or image.height() == 0:
                return False
            return True

        return False

    @staticmethod
    def validate_string(
        value: str,
        field_name: str,
        max_length: int | None = None,
        allow_empty: bool = False
    ) -> str:
        """
        Validate string input.

        Args:
            value: String to validate
            field_name: Name of field (for error messages)
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed

        Returns:
            Validated string

        Raises:
            ValidationError: If string is invalid
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"{field_name} must be string, got {type(value).__name__}"
            )

        if not allow_empty and not value.strip():
            raise ValidationError(f"{field_name} cannot be empty")

        if max_length and len(value) > max_length:
            raise ValidationError(
                f"{field_name} too long: {len(value)} chars (max {max_length})"
            )

        return value

    @staticmethod
    def validate_zoom(zoom: float) -> float:
        """
        Validate zoom level.

        Args:
            zoom: Zoom level to validate

        Returns:
            Validated zoom level

        Raises:
            ValidationError: If zoom is invalid
        """
        if not isinstance(zoom, (int, float)):
            raise ValidationError(
                f"Zoom must be numeric, got {type(zoom).__name__}"
            )

        zoom = float(zoom)

        if not EditorConstants.ZOOM_MIN <= zoom <= EditorConstants.ZOOM_MAX:
            raise ValidationError(
                ErrorMessages.OUT_OF_RANGE.format(
                    field="Zoom",
                    min=EditorConstants.ZOOM_MIN,
                    max=EditorConstants.ZOOM_MAX,
                    value=zoom
                )
            )

        return zoom

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and invalid characters.

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename
        """
        # Remove path separators
        filename = os.path.basename(filename)

        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        if len(filename) > ValidationConstants.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(filename)
            max_name_len = ValidationConstants.MAX_FILENAME_LENGTH - len(ext)
            filename = name[:max_name_len] + ext

        return filename
