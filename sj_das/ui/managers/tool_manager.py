"""Tool Manager for Editor Tool Orchestration.

Manages tool registration, activation, and event routing with proper
state management and tool lifecycle control.
"""

import logging
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPointF, Qt

from sj_das.tools.base import Tool

if TYPE_CHECKING:
    from sj_das.ui.editor_widget import PixelEditorWidget

logger = logging.getLogger(__name__)


class ToolManager:
    """
    Professional tool management system.

    Provides centralized tool orchestration with proper lifecycle
    management and event routing.

    Features:
    - Tool registration and activation
    - Event routing to active tool
    - Tool state persistence
    - Memory efficient (tools created on-demand)

    Attributes:
        editor: Reference to PixelEditorWidget
        active_tool: Currently active tool instance
        current_tool_id: ID of current tool
    """

    def __init__(self, editor: 'PixelEditorWidget'):
        """
        Initialize tool manager.

        Args:
            editor: Editor widget reference
        """
        self.editor = editor
        self.active_tool: Tool | None = None
        self.current_tool_id: int | None = None

        logger.debug("Initialized ToolManager")

    def set_tool(self, tool_id: int) -> None:
        """
        Activate a tool by ID.

        Args:
            tool_id: Tool identifier constant
        """
        # Deactivate previous tool
        if self.active_tool:
            self.active_tool.deactivate()
            self.active_tool = None

        # Store new tool ID
        self.current_tool_id = tool_id

        logger.info(f"Activated tool: {tool_id}")

    def _create_tool(self, tool_id: int) -> Tool | None:
        """
        Create tool instance on-demand.

        Args:
            tool_id: Tool to create

        Returns:
            Tool instance or None
        """
        # Import tools locally to avoid circular imports
        from sj_das.tools.brush import BrushTool
        from sj_das.tools.fill import FillTool
        from sj_das.tools.navigation import PanTool
        from sj_das.tools.perspective import PerspectiveTool
        from sj_das.tools.picker import PickerTool
        from sj_das.tools.selection import MagicWandTool, RectSelectTool
        from sj_das.tools.shapes import LineTool, RectTool

        # Tool factory
        tool_map = {
            self.editor.TOOL_BRUSH: lambda: BrushTool(self.editor, is_eraser=False),
            self.editor.TOOL_ERASER: lambda: BrushTool(self.editor, is_eraser=True),
            self.editor.TOOL_FILL: lambda: FillTool(self.editor),
            self.editor.TOOL_RECT: lambda: RectTool(self.editor),
            self.editor.TOOL_LINE: lambda: LineTool(self.editor),
            self.editor.TOOL_SELECT_RECT: lambda: RectSelectTool(self.editor),
            self.editor.TOOL_MAGIC_WAND: lambda: MagicWandTool(self.editor),
            self.editor.TOOL_PAN: lambda: PanTool(self.editor),
            self.editor.TOOL_PICKER: lambda: PickerTool(self.editor),
            self.editor.TOOL_PERSPECTIVE: lambda: PerspectiveTool(self.editor),
        }

        factory = tool_map.get(tool_id)
        if factory:
            return factory()

        logger.warning(f"Unknown tool ID: {tool_id}")
        return None

    def route_mouse_press(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Route mouse press event to active tool.

        Args:
            pos: Mouse position in scene coordinates
            buttons: Mouse buttons pressed
        """
        # Create tool instance if needed
        if self.current_tool_id is not None:
            self.active_tool = self._create_tool(self.current_tool_id)

        if self.active_tool:
            self.active_tool.mouse_press(pos, buttons)

    def route_mouse_move(self, pos: QPointF, buttons: Qt.MouseButton) -> None:
        """
        Route mouse move event to active tool.

        Args:
            pos: Mouse position in scene coordinates
            buttons: Mouse buttons pressed
        """
        if self.active_tool:
            self.active_tool.mouse_move(pos, buttons)

    def route_mouse_release(self, pos: QPointF,
                            buttons: Qt.MouseButton) -> None:
        """
        Route mouse release event to active tool.

        Args:
            pos: Mouse position in scene coordinates
            buttons: Mouse buttons pressed
        """
        if self.active_tool:
            self.active_tool.mouse_release(pos, buttons)

    def get_current_tool_id(self) -> int | None:
        """Get ID of currently active tool."""
        return self.current_tool_id

    def has_active_tool(self) -> bool:
        """Check if a tool is currently active."""
        return self.active_tool is not None
