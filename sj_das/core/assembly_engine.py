"""Assembly Engine - Multi-component saree assembly.

Combines Border, Body, and Pallu components with Khali repeats and Locking overlap.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class AssemblyEngine:
    """
    Professional saree assembly engine.

    Handles:
    - Multi-component assembly (Border|Body|Border)
    - Khali (repeat) multiplication
    - Locking (overlap) for seamless joins
    - Broket pattern preservation
    """

    def __init__(self):
        """Initialize assembly engine."""
        pass

    def assemble(
        self,
        components: dict[str, dict],
        assembly_type: str,
        khali: int,
        locking: int = 0
    ) -> np.ndarray:
        """
        Assemble components into final saree design.

        Args:
            components: Dict with 'border', 'body', 'pallu' components
            assembly_type: "Border | Body | Border" etc.
            khali: Number of repeats (3-32)
            locking: Overlap pixels for seamless join

        Returns:
            Assembled image array
        """
        logger.info(
            f"Starting assembly: {assembly_type}, Khali={khali}, Locking={locking}")

        if "Border | Body | Border" in assembly_type:
            return self._assemble_border_body_border(
                components, khali, locking)
        elif "Body Only" in assembly_type:
            return self._assemble_body_only(components, khali, locking)
        elif "Body | Pallu" in assembly_type:
            return self._assemble_body_pallu(components, khali, locking)
        else:
            raise ValueError(f"Unknown assembly type: {assembly_type}")

    def _assemble_border_body_border(
        self,
        components: dict,
        khali: int,
        locking: int
    ) -> np.ndarray:
        """
        Assemble Border|Body|Border pattern.

        Formula: (Border + Body + Border) × Khali - Locking×(Khali-1)
        """
        border_img = components['border']['image']
        body_img = components['body']['image']

        border_w = border_img.shape[1]
        body_w = body_img.shape[1]
        height = body_img.shape[0]

        # Single unit width
        unit_width = border_w + body_w + border_w

        # Total width with repeats and locking
        total_width = unit_width * khali - (locking * (khali - 1))

        # Create output image
        if len(body_img.shape) == 3:
            assembled = np.zeros((height, total_width, 3), dtype=np.uint8)
        else:
            assembled = np.zeros((height, total_width), dtype=np.uint8)

        # Assemble repeats
        current_x = 0
        for repeat in range(khali):
            # Left border
            end_x = min(current_x + border_w, total_width)
            if end_x > current_x:
                assembled[:,
                          current_x:end_x] = border_img[:,
                                                        :end_x - current_x]
                current_x = end_x

            # Body
            end_x = min(current_x + body_w, total_width)
            if end_x > current_x:
                assembled[:, current_x:end_x] = body_img[:, :end_x - current_x]
                current_x = end_x

            # Right border
            end_x = min(current_x + border_w, total_width)
            if end_x > current_x:
                assembled[:,
                          current_x:end_x] = border_img[:,
                                                        :end_x - current_x]
                current_x = end_x

            # Apply locking (overlap) for next repeat
            if repeat < khali - 1 and locking > 0:
                current_x -= locking

        logger.info(f"Assembled Border|Body|Border: {total_width}×{height}")

        return assembled

    def _assemble_body_only(
        self,
        components: dict,
        khali: int,
        locking: int
    ) -> np.ndarray:
        """Assemble Body only with repeats."""
        body_img = components['body']['image']

        body_w = body_img.shape[1]
        height = body_img.shape[0]

        # Total width with repeats
        total_width = body_w * khali - (locking * (khali - 1))

        # Create output
        if len(body_img.shape) == 3:
            assembled = np.zeros((height, total_width, 3), dtype=np.uint8)
        else:
            assembled = np.zeros((height, total_width), dtype=np.uint8)

        # Repeat body
        current_x = 0
        for repeat in range(khali):
            end_x = min(current_x + body_w, total_width)
            if end_x > current_x:
                assembled[:, current_x:end_x] = body_img[:, :end_x - current_x]
                current_x = end_x

            # Locking
            if repeat < khali - 1 and locking > 0:
                current_x -= locking

        return assembled

    def _assemble_body_pallu(
        self,
        components: dict,
        khali: int,
        locking: int
    ) -> np.ndarray:
        """Assemble Body with Pallu end piece."""
        body_img = components['body']['image']
        pallu_img = components['pallu']['image']

        # Concatenate vertically
        assembled = np.vstack([body_img, pallu_img])

        # Apply khali repeats horizontally
        return self._assemble_body_only(
            {'body': {'image': assembled}}, khali, locking)

    def calculate_dimensions(
        self,
        components: dict,
        assembly_type: str,
        khali: int,
        locking: int
    ) -> tuple[int, int]:
        """
        Calculate final dimensions without creating image.

        Returns:
            (total_hooks, total_picks)
        """
        if "Border | Body | Border" in assembly_type:
            if 'border' not in components or 'body' not in components:
                return (0, 0)

            border_w = components['border']['width']
            body_w = components['body']['width']
            unit_width = border_w * 2 + body_w

            total_hooks = unit_width * khali - (locking * (khali - 1))
            total_picks = components['body']['height']

            return (total_hooks, total_picks)

        elif "Body Only" in assembly_type:
            if 'body' not in components:
                return (0, 0)

            body_w = components['body']['width']
            total_hooks = body_w * khali - (locking * (khali - 1))
            total_picks = components['body']['height']

            return (total_hooks, total_picks)

        return (0, 0)
