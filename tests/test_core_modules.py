"""
Comprehensive test suite for SJ-DAS core modules.

Tests constants, exceptions, validation, memory management,
logging, caching, and file utilities.
"""

import tempfile
from pathlib import Path

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage

# Import modules to test
from sj_das.core.constants import (EditorConstants, ErrorMessages,
                                   FileConstants, UIConstants,
                                   ValidationConstants)
from sj_das.core.exceptions import (DesignImportError, SJDASException,
                                    ValidationError)
from sj_das.utils.cache import ImageCache, cached_result, image_hash
from sj_das.utils.file_utils import (TempFileManager, ensure_directory,
                                     safe_delete)
from sj_das.utils.memory import MemoryManager
from sj_das.utils.validation import InputValidator


class TestConstants:
    """Test constants module."""

    def test_ui_constants(self):
        """Test UI constants are defined."""
        assert UIConstants.STATUS_BAR_HEIGHT > 0
        assert UIConstants.ANIMATION_FAST > 0
        assert UIConstants.TOOLBAR_ICON_SIZE > 0

    def test_editor_constants(self):
        """Test editor constants."""
        assert EditorConstants.BRUSH_SIZE_MIN == 1
        assert EditorConstants.BRUSH_SIZE_MAX == 200
        assert EditorConstants.MAX_IMAGE_WIDTH > 0

    def test_file_constants(self):
        """Test file constants."""
        assert '.png' in FileConstants.SUPPORTED_IMAGE_FORMATS
        assert '.jpg' in FileConstants.SUPPORTED_IMAGE_FORMATS
        assert FileConstants.MAX_FILE_SIZE_MB > 0

    def test_error_messages(self):
        """Test error message templates."""
        msg = ErrorMessages.FILE_NOT_FOUND.format(path="/test/path")
        assert "/test/path" in msg


class TestExceptions:
    """Test exception hierarchy."""

    def test_base_exception(self):
        """Test base exception."""
        exc = SJDASException("Test error", details={"key": "value"})
        assert exc.message == "Test error"
        assert exc.details["key"] == "value"
        assert "key=value" in str(exc)

    def test_validation_error(self):
        """Test validation error."""
        exc = ValidationError("Invalid input")
        assert isinstance(exc, SJDASException)
        assert exc.message == "Invalid input"

    def test_design_import_error(self):
        """Test design import error."""
        exc = DesignImportError("Import failed", details={"path": "/test"})
        assert exc.details["path"] == "/test"


class TestInputValidator:
    """Test input validation."""

    def test_validate_brush_size_valid(self):
        """Test valid brush size."""
        size = InputValidator.validate_brush_size(50)
        assert size == 50

    def test_validate_brush_size_invalid(self):
        """Test invalid brush size."""
        with pytest.raises(ValidationError):
            InputValidator.validate_brush_size(0)

        with pytest.raises(ValidationError):
            InputValidator.validate_brush_size(300)

    def test_validate_opacity_valid(self):
        """Test valid opacity."""
        opacity = InputValidator.validate_opacity(0.5)
        assert opacity == 0.5

    def test_validate_opacity_invalid(self):
        """Test invalid opacity."""
        with pytest.raises(ValidationError):
            InputValidator.validate_opacity(-0.1)

        with pytest.raises(ValidationError):
            InputValidator.validate_opacity(1.5)

    def test_validate_zoom_valid(self):
        """Test valid zoom."""
        zoom = InputValidator.validate_zoom(2.0)
        assert zoom == 2.0

    def test_validate_zoom_invalid(self):
        """Test invalid zoom."""
        with pytest.raises(ValidationError):
            InputValidator.validate_zoom(0.05)

        with pytest.raises(ValidationError):
            InputValidator.validate_zoom(15.0)

    def test_validate_string_valid(self):
        """Test valid string."""
        text = InputValidator.validate_string("Hello", "test", max_length=10)
        assert text == "Hello"

    def test_validate_string_empty(self):
        """Test empty string."""
        with pytest.raises(ValidationError):
            InputValidator.validate_string("", "test")

    def test_validate_string_too_long(self):
        """Test string too long."""
        with pytest.raises(ValidationError):
            InputValidator.validate_string("A" * 300, "test", max_length=100)

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test path traversal
        safe = InputValidator.sanitize_filename("../../../etc/passwd")
        assert ".." not in safe
        assert "/" not in safe

        # Test invalid characters
        safe = InputValidator.sanitize_filename("file<>:|?.txt")
        assert "<" not in safe
        assert ">" not in safe
        assert "|" not in safe

    def test_validate_image_valid(self):
        """Test valid image."""
        image = QImage(100, 100, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.white)

        validated = InputValidator.validate_image(image)
        assert validated.width() == 100
        assert validated.height() == 100

    def test_validate_image_null(self):
        """Test null image."""
        image = QImage()
        with pytest.raises(ValidationError):
            InputValidator.validate_image(image)

    def test_validate_image_too_large(self):
        """Test image too large."""
        # Create image larger than max dimensions
        image = QImage(10000, 10000, QImage.Format.Format_RGB32)
        with pytest.raises(ValidationError):
            InputValidator.validate_image(image)


class TestMemoryManager:
    """Test memory management."""

    def test_get_memory_usage(self):
        """Test memory usage tracking."""
        manager = MemoryManager()
        usage = manager.get_memory_usage_mb()
        assert usage > 0

    def test_cleanup_image(self):
        """Test image cleanup."""
        manager = MemoryManager()
        image = QImage(100, 100, QImage.Format.Format_RGB32)

        # Should not raise
        manager.cleanup_image(image)
        manager.cleanup_image(None)

    def test_check_memory_status(self):
        """Test memory status check."""
        manager = MemoryManager()
        status = manager.check_memory_status()
        assert status in ['ok', 'warning', 'critical']


class TestImageCache:
    """Test image caching."""

    def test_cache_put_get(self):
        """Test cache put and get."""
        cache = ImageCache(max_size_mb=10)
        image = QImage(100, 100, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.red)

        cache.put("test_key", image)
        retrieved = cache.get("test_key")

        assert retrieved is not None
        assert retrieved.width() == 100
        assert retrieved.height() == 100

    def test_cache_miss(self):
        """Test cache miss."""
        cache = ImageCache(max_size_mb=10)
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = ImageCache(max_size_mb=10)
        image = QImage(100, 100, QImage.Format.Format_RGB32)

        cache.put("key1", image)
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['item_count'] == 1

    def test_cache_clear(self):
        """Test cache clear."""
        cache = ImageCache(max_size_mb=10)
        image = QImage(100, 100, QImage.Format.Format_RGB32)

        cache.put("key1", image)
        cache.put("key2", image)

        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestCachedResult:
    """Test result caching decorator."""

    def test_cached_function(self):
        """Test cached function."""
        call_count = [0]

        @cached_result(maxsize=128)
        def expensive_func(x: int) -> int:
            call_count[0] += 1
            return x * 2

        # First call
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count[0] == 1

        # Second call (cached)
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count[0] == 1  # Not called again

        # Different argument
        result3 = expensive_func(10)
        assert result3 == 20
        assert call_count[0] == 2


class TestImageHash:
    """Test image hashing."""

    def test_image_hash_consistent(self):
        """Test hash is consistent."""
        image = QImage(100, 100, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.blue)

        hash1 = image_hash(image)
        hash2 = image_hash(image)

        assert hash1 == hash2

    def test_image_hash_different(self):
        """Test different images have different hashes."""
        image1 = QImage(100, 100, QImage.Format.Format_RGB32)
        image1.fill(Qt.GlobalColor.red)

        image2 = QImage(100, 100, QImage.Format.Format_RGB32)
        image2.fill(Qt.GlobalColor.blue)

        hash1 = image_hash(image1)
        hash2 = image_hash(image2)

        assert hash1 != hash2


class TestTempFileManager:
    """Test temporary file management."""

    def test_create_temp_file(self):
        """Test temp file creation."""
        manager = TempFileManager()
        temp_file = manager.create_temp_file(suffix=".txt")

        assert temp_file.exists()
        assert temp_file.suffix == ".txt"

        # Cleanup
        manager.cleanup_all()
        assert not temp_file.exists()

    def test_create_temp_dir(self):
        """Test temp directory creation."""
        manager = TempFileManager()
        temp_dir = manager.create_temp_dir()

        assert temp_dir.exists()
        assert temp_dir.is_dir()

        # Cleanup
        manager.cleanup_all()
        assert not temp_dir.exists()

    def test_temp_count(self):
        """Test temp file counting."""
        manager = TempFileManager()

        manager.create_temp_file()
        manager.create_temp_file()
        manager.create_temp_dir()

        file_count, dir_count = manager.get_temp_count()
        assert file_count == 2
        assert dir_count == 1

        manager.cleanup_all()


class TestFileUtils:
    """Test file utilities."""

    def test_safe_delete(self):
        """Test safe file deletion."""
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

        assert temp_path.exists()

        # Delete
        result = safe_delete(temp_path)
        assert result is True
        assert not temp_path.exists()

        # Delete non-existent
        result = safe_delete(temp_path)
        assert result is False

    def test_ensure_directory(self):
        """Test directory creation."""
        temp_dir = Path(tempfile.gettempdir()) / \
            "test_sj_das" / "nested" / "dir"

        # Remove if exists
        if temp_dir.exists():
            temp_dir.rmdir()

        # Create
        result = ensure_directory(temp_dir)
        assert result is True
        assert temp_dir.exists()

        # Cleanup
        temp_dir.rmdir()
        temp_dir.parent.rmdir()
        temp_dir.parent.parent.rmdir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
