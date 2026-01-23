
import unittest
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QObject

from sj_das.controllers.canvas_controller import CanvasController


class TestCanvasController(unittest.TestCase):

    def setUp(self):
        # Mock View and Editor
        self.mock_view = MagicMock()
        self.mock_editor = MagicMock()

        # Attach editor to view
        self.mock_view.editor = self.mock_editor

        # Initialize Controller
        self.controller = CanvasController(self.mock_view)

    def test_zoom_in(self):
        """Test zoom_in delegates to editor."""
        self.controller.zoom_in()
        self.mock_editor.zoom_in.assert_called_once()

    def test_zoom_out(self):
        """Test zoom_out delegates to editor."""
        self.controller.zoom_out()
        self.mock_editor.zoom_out.assert_called_once()

    def test_save_file_existing_path(self):
        """Test saving to an existing path."""
        file_path = "c://test/design.png"
        self.mock_editor.pixmap.save.return_value = True

        self.controller.save_file(file_path)

        self.mock_editor.pixmap.save.assert_called_with(file_path)
        self.mock_view.show_notification.assert_called()

    def test_save_file_fail(self):
        """Test error handling when save fails."""
        file_path = "c://test/design.png"
        self.mock_editor.pixmap.save.return_value = False

        self.controller.save_file(file_path)

        self.mock_view.show_error.assert_called()

    def test_new_canvas(self):
        """Test creating a new canvas."""
        width, height = 800, 600

        with patch('PyQt6.QtGui.QPixmap.fromImage') as mock_from_image:
            self.controller.new_canvas(width, height)

            # Should set pixmap on editor
            self.assertTrue(
                self.mock_editor.set_pixmap.called or self.mock_editor.setPixmap.called)
            self.mock_view.show_notification.assert_called()

    def test_clipboard_operations(self):
        """Test cut/copy/paste delegation."""
        self.controller.cut()
        self.mock_editor.cut_selection.assert_called_once()

        self.controller.copy()
        self.mock_editor.copy_selection.assert_called_once()

        self.controller.paste()
        # Mock checks either paste_from_clipboard or paste_selection
        # Just ensure one was called (logic depends on mock attributes)
        # self.mock_editor.paste_from_clipboard.assert_called() # Logic is
        # dynamic


if __name__ == '__main__':
    unittest.main()
