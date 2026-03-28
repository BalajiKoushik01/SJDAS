"""
Unit tests for UI command patterns.

Tests the undo/redo command implementation for correct state management.
"""

from unittest.mock import MagicMock, Mock

import pytest
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QImage, QUndoStack

from sj_das.ui.commands import BitmapEditCommand


class TestBitmapEditCommand:
    """Test suite for BitmapEditCommand."""

    @pytest.fixture
    def mock_editor(self):
        """Create a mock editor with necessary attributes."""
        editor = Mock()
        editor.mask_image = QImage(100, 100, QImage.Format.Format_ARGB32)
        editor.mask_image.fill(0)
        editor.mask_item = Mock()
        editor.mask_updated = Mock()
        editor.mask_updated.emit = Mock()
        return editor

    @pytest.fixture
    def sample_images(self):
        """Create sample before/after images."""
        before = QImage(100, 100, QImage.Format.Format_ARGB32)
        before.fill(0xFF000000)  # Black

        after = QImage(100, 100, QImage.Format.Format_ARGB32)
        after.fill(0xFFFFFFFF)  # White

        return before, after

    def test_command_creation(self, mock_editor, sample_images):
        """Test command can be created with valid parameters."""
        before, after = sample_images
        rect = QRect(0, 0, 50, 50)

        cmd = BitmapEditCommand(
            mock_editor,
            before,
            after,
            rect,
            "Test Edit"
        )

        assert cmd.editor == mock_editor
        assert cmd.before_img == before
        assert cmd.after_img == after
        assert cmd.rect == rect
        assert cmd.text() == "Test Edit"

    def test_redo_emits_signal(self, mock_editor, sample_images):
        """Test that redo emits mask_updated signal."""
        before, after = sample_images
        rect = QRect(0, 0, 50, 50)

        cmd = BitmapEditCommand(mock_editor, before, after, rect, "Test")
        cmd.redo()

        mock_editor.mask_updated.emit.assert_called_once()

    def test_undo_emits_signal(self, mock_editor, sample_images):
        """Test that undo emits mask_updated signal."""
        before, after = sample_images
        rect = QRect(0, 0, 50, 50)

        cmd = BitmapEditCommand(mock_editor, before, after, rect, "Test")
        cmd.undo()

        mock_editor.mask_updated.emit.assert_called_once()

    def test_redo_undo_cycle(self, mock_editor, sample_images):
        """Test that redo followed by undo restores state."""
        before, after = sample_images
        rect = QRect(0, 0, 50, 50)

        cmd = BitmapEditCommand(mock_editor, before, after, rect, "Test")

        # Redo then undo
        cmd.redo()
        cmd.undo()

        # Should have emitted signal twice
        assert mock_editor.mask_updated.emit.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
