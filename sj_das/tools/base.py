"""Base Tool Interface for SJ-DAS Pixel Editor.

Provides abstract base class and common utilities for all editor tools.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, Qt

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget


class Tool(ABC):
    """
    Abstract base class for all editor tools.

    Implements the Strategy pattern for tool behavior.
    Each tool handles mouse events and performs specific operations
    on the editor's pixel data.

    Attributes:
        editor: Reference to the PixelEditorWidget
    """

    def __init__(self, editor: 'PixelEditorWidget'):
        """
        Initialize tool with editor reference.

        Args:
            editor: The PixelEditorWidget this tool operates on
        """
        self.editor = editor

    @abstractmethod
    def mouse_press(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Handle mouse press event.

        Args:
            pos: Scene position of mouse press
            buttons: Qt mouse button flags
        """
        pass

    def mouse_move(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Handle mouse move event.

        Default implementation does nothing. Override if needed.

        Args:
            pos: Scene position of mouse
            buttons: Qt mouse button flags
        """
        pass

    def mouse_release(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Handle mouse release event.

        Default implementation does nothing. Override if needed.

        Args:
            pos: Scene position of mouse release
            buttons: Qt mouse button flags
        """
        pass

    def activate(self) -> None:
        """
        Called when tool is activated.

        Override to perform tool-specific setup.
        """
        pass

    def deactivate(self) -> None:
        """
        Called when tool is deactivated.

        Override to perform cleanup.
        """
        pass
