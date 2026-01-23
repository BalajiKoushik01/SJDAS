"""Advanced Weave Management System for Jacquard Design.

Provides professional weave pattern library, validation, and production safety checks
comparable to industry leaders like ArahWeave and NedGraphics.
"""

import logging

import numpy as np

from .exceptions import ValidationError, WeaveGenerationError

logger = logging.getLogger(__name__)


class WeaveManager:
    """
    Professional weave structure management system.

    Features:
    - Extensive weave pattern library
    - Production safety validation (float detection)
    - Pattern generation and manipulation
    - Industry-standard weave structures

    Attributes:
        library: Dictionary of predefined weave patterns
    """

    def __init__(self):
        """Initialize weave library with industry-standard patterns."""
        self.library: dict[str, np.ndarray] = self._build_weave_library()
        logger.debug(
            f"Initialized WeaveManager with {len(self.library)} patterns")

    def _build_weave_library(self) -> dict[str, np.ndarray]:
        """
        Build comprehensive weave pattern library.

        Returns:
            Dictionary mapping weave names to binary pattern matrices
        """
        return {
            # Basic weaves
            "Plain 1/1": np.array([
                [1, 0],
                [0, 1]
            ], dtype=np.uint8),

            # Twill weaves
            "Twill 2/1 S": np.array([
                [1, 1, 0],
                [0, 1, 1],
                [1, 0, 1]
            ], dtype=np.uint8),

            "Twill 2/1 Z": np.array([
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 1]
            ], dtype=np.uint8),

            "Twill 3/1": np.array([
                [1, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 1, 1],
                [1, 1, 0, 1]
            ], dtype=np.uint8),

            # Satin weaves
            "Satin 5": np.array([
                [1, 0, 0, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1],
                [0, 0, 1, 0, 0]
            ], dtype=np.uint8),

            "Satin 8": np.array([
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0]
            ], dtype=np.uint8),

            # Basket weaves
            "Basket 2/2": np.array([
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1]
            ], dtype=np.uint8),
        }

    def get_weave(self, name: str) -> np.ndarray:
        """
        Get weave pattern by name.

        Args:
            name: Weave pattern name

        Returns:
            Binary weave pattern matrix

        Raises:
            ValidationError: If weave name is invalid
        """
        if not isinstance(name, str):
            raise ValidationError("Weave name must be a string")

        pattern = self.library.get(name)

        if pattern is None:
            logger.warning(f"Unknown weave '{name}', using Plain 1/1")
            return self.library["Plain 1/1"]

        return pattern.copy()  # Return copy to prevent mutation

    def list_weaves(self) -> list[str]:
        """Get list of all available weave patterns."""
        return sorted(self.library.keys())

    def check_float_safety(
        self,
        weave_matrix: np.ndarray,
        max_float: int = 20
    ) -> tuple[bool, np.ndarray | None]:
        """
        Validate production safety by detecting long floats.

        Long floats can cause fabric snagging and loom damage.
        Industry standard validates both warp and weft directions.

        Args:
            weave_matrix: Binary weave pattern to validate
            max_float: Maximum allowed consecutive float length

        Returns:
            Tuple of (is_safe, error_map)
            - is_safe: True if no dangerous floats detected
            - error_map: Binary array marking problematic regions

        Raises:
            ValidationError: If inputs are invalid
        """
        # Validation
        if weave_matrix is None:
            return True, None

        if not isinstance(weave_matrix, np.ndarray):
            raise ValidationError("weave_matrix must be a numpy array")

        if weave_matrix.ndim != 2:
            raise ValidationError("weave_matrix must be 2-dimensional")

        if not (5 <= max_float <= 100):
            raise ValidationError(f"max_float must be 5-100, got {max_float}")

        # Ensure binary
        bin_mat = (weave_matrix > 0).astype(np.uint8)
        rows, cols = bin_mat.shape

        errors = np.zeros_like(bin_mat)
        is_safe = True

        # Check warp floats (vertical - columns)
        for c in range(cols):
            col_data = bin_mat[:, c]
            run_lengths, run_starts = self._calculate_run_lengths(col_data)

            # Mark dangerous floats
            dangerous_runs = run_lengths > max_float
            if np.any(dangerous_runs):
                is_safe = False
                for length, start in zip(run_lengths[dangerous_runs],
                                         run_starts[dangerous_runs], strict=False):
                    errors[start:start + length, c] = 1

        # Check weft floats (horizontal - rows)
        for r in range(rows):
            row_data = bin_mat[r, :]
            run_lengths, run_starts = self._calculate_run_lengths(row_data)

            dangerous_runs = run_lengths > max_float
            if np.any(dangerous_runs):
                is_safe = False
                for length, start in zip(run_lengths[dangerous_runs],
                                         run_starts[dangerous_runs], strict=False):
                    errors[r, start:start + length] = 1

        if not is_safe:
            logger.warning(
                f"Float safety check failed: "
                f"{np.sum(errors)} pixels exceed {max_float}px limit"
            )

        return is_safe, errors if not is_safe else None

    @staticmethod
    def _calculate_run_lengths(
            data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Calculate run lengths using efficient RLE algorithm.

        Args:
            data: 1D binary array

        Returns:
            Tuple of (run_lengths, run_starts)
        """
        # Find changes
        diffs = np.diff(data)
        changes = np.where(diffs != 0)[0] + 1

        # Add boundaries
        changes = np.concatenate(([0], changes, [len(data)]))

        # Calculate lengths and starts
        run_lengths = np.diff(changes)
        run_starts = changes[:-1]

        return run_lengths, run_starts

    def generate_custom_weave(
        self,
        size: int,
        pattern_type: str = "twill"
    ) -> np.ndarray:
        """
        Generate custom weave pattern.

        Args:
            size: Pattern size (e.g., 3 for 3x3)
            pattern_type: Type of pattern to generate

        Returns:
            Generated weave pattern

        Raises:
            WeaveGenerationError: If generation fails
        """
        if not (2 <= size <= 16):
            raise ValidationError("size must be between 2 and 16")

        if pattern_type == "twill":
            # Simple twill generation
            pattern = np.zeros((size, size), dtype=np.uint8)
            for i in range(size):
                for j in range(size):
                    pattern[i, (i + j) % size] = 1
            return pattern

        elif pattern_type == "satin":
            # Basic satin generation
            pattern = np.zeros((size, size), dtype=np.uint8)
            step = (size + 1) // 2
            for i in range(size):
                pattern[i, (i * step) % size] = 1
            return pattern

            raise WeaveGenerationError(
                f"Unknown pattern type: {pattern_type}",
                "Supported types: 'twill', 'satin'"
            )

    def auto_lock_floats(
        self,
        weave_matrix: np.ndarray,
        max_float: int = 20
    ) -> tuple[np.ndarray, int]:
        """
        Automatically fix float violations by inserting binding points (locking).

        Args:
            weave_matrix: Binary weave pattern
            max_float: Maximum allowed float length

        Returns:
            Tuple (corrected_matrix, num_fixes)
        """
        if weave_matrix is None:
            return None, 0

        # Work on copy
        fixed_matrix = weave_matrix.copy()
        # Ensure binary
        bin_mat = (fixed_matrix > 0).astype(np.uint8)
        rows, cols = bin_mat.shape
        fixes = 0

        # Helper to break floats
        def break_run(data, axis_idx, is_row):
            mutations = 0
            # RLE logic
            run_val = data[0]
            current_run = 0

            for i in range(len(data)):
                if data[i] == run_val:
                    current_run += 1
                else:
                    run_val = data[i]
                    current_run = 1

                if current_run > max_float:
                    # Break float!
                    # Insert binding point (flip bit)
                    # For aesthetic, break at max_float step? Or middle?
                    # Industry standard: Break at max_float intervals.

                    # Flip current pixel
                    new_val = 1 - run_val
                    data[i] = new_val

                    # Updates main matrix
                    if is_row:
                        fixed_matrix[axis_idx, i] = new_val
                    else:
                        fixed_matrix[i, axis_idx] = new_val

                    mutations += 1
                    current_run = 1  # Reset run (since we flipped)
                    run_val = new_val

            return mutations

        # Check warp floats (cols)
        for c in range(cols):
            col_data = (fixed_matrix[:, c] > 0).astype(
                np.uint8)  # Refresh from fixed_matrix
            fixes += break_run(col_data, c, is_row=False)

        # Check weft floats (rows)
        for r in range(rows):
            row_data = (fixed_matrix[r, :] > 0).astype(np.uint8)
            fixes += break_run(row_data, r, is_row=True)

        return fixed_matrix, fixes
