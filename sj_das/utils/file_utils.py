"""
File utilities for SJ-DAS.

Provides safe file operations and temporary file management
to prevent resource leaks and ensure clean cleanup.
"""

import atexit
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("SJ_DAS.FileUtils")


class TempFileManager:
    """
    Manages temporary files with automatic cleanup.

    Features:
        - Track all temporary files
        - Automatic cleanup on exit
        - Safe deletion with error handling
    """

    def __init__(self):
        self._temp_files: List[Path] = []
        self._temp_dirs: List[Path] = []
        self._registered = False

    def create_temp_file(self, suffix: str = "",
                         prefix: str = "sj_das_") -> Path:
        """
        Create a temporary file.

        Args:
            suffix: File suffix (e.g., '.png')
            prefix: File prefix

        Returns:
            Path to temporary file
        """
        fd, path_str = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)  # Close file descriptor

        path = Path(path_str)
        self._temp_files.append(path)

        # Register cleanup on first use
        if not self._registered:
            self.register_cleanup_on_exit()
            self._registered = True

        logger.debug(f"Created temp file: {path}")
        return path

    def create_temp_dir(self, prefix: str = "sj_das_") -> Path:
        """
        Create a temporary directory.

        Args:
            prefix: Directory prefix

        Returns:
            Path to temporary directory
        """
        path_str = tempfile.mkdtemp(prefix=prefix)
        path = Path(path_str)
        self._temp_dirs.append(path)

        if not self._registered:
            self.register_cleanup_on_exit()
            self._registered = True

        logger.debug(f"Created temp dir: {path}")
        return path

    def cleanup_all(self) -> None:
        """Clean up all temporary files and directories."""
        # Clean up files
        for path in self._temp_files:
            if path.exists():
                try:
                    path.unlink()
                    logger.debug(f"Deleted temp file: {path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {path}: {e}")

        # Clean up directories
        for path in self._temp_dirs:
            if path.exists():
                try:
                    shutil.rmtree(path)
                    logger.debug(f"Deleted temp dir: {path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp dir {path}: {e}")

        self._temp_files.clear()
        self._temp_dirs.clear()
        logger.info("Temp file cleanup complete")

    def register_cleanup_on_exit(self) -> None:
        """Register cleanup to run on program exit."""
        atexit.register(self.cleanup_all)
        logger.debug("Registered temp file cleanup on exit")

    def get_temp_count(self) -> tuple[int, int]:
        """
        Get count of temporary files and directories.

        Returns:
            Tuple of (file_count, dir_count)
        """
        return len(self._temp_files), len(self._temp_dirs)


# Global instance
_temp_manager = TempFileManager()


def get_temp_manager() -> TempFileManager:
    """Get the global temp file manager."""
    return _temp_manager


def safe_delete(path: Path) -> bool:
    """
    Safely delete a file.

    Args:
        path: Path to file

    Returns:
        True if deleted, False otherwise
    """
    try:
        if path.exists() and path.is_file():
            path.unlink()
            logger.debug(f"Deleted file: {path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete {path}: {e}")
        return False


def safe_move(src: Path, dst: Path) -> bool:
    """
    Safely move a file.

    Args:
        src: Source path
        dst: Destination path

    Returns:
        True if moved, False otherwise
    """
    try:
        shutil.move(str(src), str(dst))
        logger.debug(f"Moved {src} to {dst}")
        return True
    except Exception as e:
        logger.error(f"Failed to move {src} to {dst}: {e}")
        return False


def ensure_directory(path: Path) -> bool:
    """
    Ensure directory exists, create if needed.

    Args:
        path: Directory path

    Returns:
        True if directory exists/created, False on error
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def get_file_size_mb(path: Path) -> float:
    """
    Get file size in megabytes.

    Args:
        path: File path

    Returns:
        Size in MB
    """
    try:
        return path.stat().st_size / (1024 * 1024)
    except Exception:
        return 0.0


def is_path_safe(path: Path, allowed_dir: Optional[Path] = None) -> bool:
    """
    Check if path is safe (no traversal).

    Args:
        path: Path to check
        allowed_dir: Optional allowed directory

    Returns:
        True if safe, False otherwise
    """
    try:
        resolved = path.resolve()

        if allowed_dir:
            allowed_resolved = allowed_dir.resolve()
            return resolved.is_relative_to(allowed_resolved)

        return True
    except Exception:
        return False
