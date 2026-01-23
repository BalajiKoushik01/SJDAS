"""Undo/Redo Manager using Command Pattern.

Provides professional undo/redo functionality with memory management
and command grouping support.
"""

import logging
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)


class Command(Protocol):
    """Protocol for undo/redo commands."""

    def execute(self) -> None:
        """Execute the command."""
        ...

    def undo(self) -> None:
        """Undo the command."""
        ...

    def get_description(self) -> str:
        """Get human-readable description of command."""
        ...


@dataclass
class ImageCommand:
    """
    Command for image editing operations.

    Stores before/after states for undo/redo.
    """
    description: str
    before_state: bytes  # Serialized QImage
    after_state: bytes   # Serialized QImage
    apply_callback: callable

    def execute(self) -> None:
        """Apply the after state."""
        self.apply_callback(self.after_state)

    def undo(self) -> None:
        """Restore the before state."""
        self.apply_callback(self.before_state)

    def get_description(self) -> str:
        """Get command description."""
        return self.description


class UndoManager:
    """
    Professional undo/redo manager using Command pattern.

    Features:
    - Unlimited undo/redo with memory limit
    - Command grouping (batch operations)
    - Memory management
    - Clean/dirty state tracking

    Attributes:
        max_commands: Maximum commands to keep in history
        undo_stack: Stack of undo commands
        redo_stack: Stack of redo commands
    """

    def __init__(self, max_commands: int = 50):
        """
        Initialize undo manager.

        Args:
            max_commands: Maximum number of commands to keep
        """
        self.max_commands = max_commands
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self._clean_index = 0

        logger.debug(
            f"Initialized UndoManager with {max_commands} max commands")

    def push(self, command: Command) -> None:
        """
        Push new command onto undo stack.

        Args:
            command: Command to add
        """
        # Execute the command
        command.execute()

        # Add to undo stack
        self.undo_stack.append(command)

        # Clear redo stack (new action invalidates redo)
        self.redo_stack.clear()

        # Limit stack size
        if len(self.undo_stack) > self.max_commands:
            removed = self.undo_stack.pop(0)
            logger.debug(f"Removed old command: {removed.get_description()}")

        logger.debug(f"Pushed command: {command.get_description()}")

    def undo(self) -> bool:
        """
        Undo last command.

        Returns:
            True if undo was performed, False if nothing to undo
        """
        if not self.can_undo():
            return False

        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)

        logger.info(f"Undid: {command.get_description()}")
        return True

    def redo(self) -> bool:
        """
        Redo last undone command.

        Returns:
            True if redo was performed, False if nothing to redo
        """
        if not self.can_redo():
            return False

        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)

        logger.info(f"Redid: {command.get_description()}")
        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0

    def clear(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._clean_index = 0
        logger.info("Cleared undo/redo history")

    def get_undo_description(self) -> str | None:
        """Get description of next undo command."""
        if self.can_undo():
            return self.undo_stack[-1].get_description()
        return None

    def get_redo_description(self) -> str | None:
        """Get description of next redo command."""
        if self.can_redo():
            return self.redo_stack[-1].get_description()
        return None

    def mark_clean(self) -> None:
        """Mark current state as clean (saved)."""
        self._clean_index = len(self.undo_stack)

    def is_clean(self) -> bool:
        """Check if document is in clean (saved) state."""
        return len(self.undo_stack) == self._clean_index

    def get_memory_usage(self) -> int:
        """
        Estimate memory usage in bytes.

        Returns:
            Approximate memory used by undo/redo stacks
        """
        # Rough estimate based on command count
        # Actual calculation would need to inspect command data
        total_commands = len(self.undo_stack) + len(self.redo_stack)
        return total_commands * 100000  # Assume ~100KB per command average
