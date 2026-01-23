"""Professional Fabric Simulation Engine for Textile Design.

Provides photorealistic fabric rendering with advanced visual effects
comparable to industry-leading software like NedGraphics and ArahWeave.
"""

import logging

import cv2
import numpy as np

from .exceptions import AIProcessingError, ValidationError
from .weave_manager import WeaveManager

logger = logging.getLogger(__name__)


class FabricSimulator:
    """
    Advanced fabric simulation engine with photorealistic rendering.

    Features:
    - 3D emboss lighting effects
    - Thread-level texture simulation
    - Configurable simulation quality
    - Performance-optimized rendering

    Attributes:
        scale: Simulation upscale factor (higher = more detail)
        warp_color: Default warp thread color
        light_intensity: Lighting effect strength
    """

    def __init__(
        self,
        scale: int = 2,
        warp_color: tuple[int, int, int] = (20, 20, 20),
        light_intensity: float = 30.0
    ):
        """
        Initialize fabric simulator with quality settings.

        Args:
            scale: Upscale factor for simulation (1-4)
            warp_color: RGB warp thread color
            light_intensity: Strength of 3D lighting effect
        """
        if not (1 <= scale <= 4):
            raise ValidationError("scale must be between 1 and 4")

        self.scale = scale
        self.warp_color = np.array(warp_color, dtype=np.uint8)
        self.light_intensity = light_intensity

        logger.debug(
            f"Initialized FabricSimulator: scale={scale}, "
            f"warp_color={warp_color}, light={light_intensity}"
        )

    def simulate(
        self,
        design_img: np.ndarray,
        weave_map_dict: dict[tuple[int, int, int], str],
        weave_manager: WeaveManager
    ) -> np.ndarray:
        """
        Generate photorealistic fabric simulation from design.

        Args:
            design_img: Input design image (BGR format)
            weave_map_dict: Mapping of colors to weave patterns
            weave_manager: WeaveManager instance for pattern lookup

        Returns:
            Simulated fabric image with 3D effects

        Raises:
            AIProcessingError: If simulation fails
            ValidationError: If inputs are invalid
        """
        # Validation
        if not isinstance(design_img, np.ndarray):
            raise ValidationError("design_img must be a numpy array")

        if design_img.ndim != 3 or design_img.shape[2] != 3:
            raise ValidationError("design_img must be a 3-channel BGR image")

        try:
            h, w = design_img.shape[:2]
            sim_h, sim_w = h * self.scale, w * self.scale

            logger.info(f"Starting simulation: {(h, w)} -> {(sim_h, sim_w)}")

            # Initialize output
            simulation = np.zeros((sim_h, sim_w, 3), dtype=np.uint8)

            # Extract unique colors
            unique_colors = self._extract_unique_colors(design_img)

            logger.debug(f"Processing {len(unique_colors)} unique colors")

            # Process each color region
            for color in unique_colors:
                try:
                    color_tuple = tuple(color)

                    # Get weave pattern
                    weave_name = weave_map_dict.get(color_tuple, "Plain 1/1")
                    pattern = weave_manager.get_weave(weave_name)

                    # Create color mask
                    mask = cv2.inRange(design_img, color, color)

                    # Render weave texture
                    texture = self._render_weave_texture(
                        pattern,
                        color,
                        (sim_h, sim_w)
                    )

                    # Apply to simulation
                    mask_scaled = cv2.resize(
                        mask,
                        (sim_w, sim_h),
                        interpolation=cv2.INTER_NEAREST
                    )

                    mask_3ch = np.dstack([mask_scaled] * 3)
                    simulation = np.where(mask_3ch > 0, texture, simulation)

                except Exception as e:
                    logger.warning(
                        f"Failed to process color {color_tuple}: {e}, skipping"
                    )
                    continue

            logger.info("Simulation completed successfully")
            return simulation

        except Exception as e:
            raise AIProcessingError(
                "Fabric simulation failed",
                str(e)
            )

    def _extract_unique_colors(self, img: np.ndarray) -> np.ndarray:
        """
        Extract unique colors from image efficiently.

        Args:
            img: Input image

        Returns:
            Array of unique RGB colors
        """
        img_view = img.reshape(-1, 3)
        unique_colors = np.unique(img_view, axis=0)
        return unique_colors

    def _render_weave_texture(
        self,
        pattern: np.ndarray,
        weft_color: np.ndarray,
        output_size: tuple[int, int]
    ) -> np.ndarray:
        """
        Render weave pattern with 3D lighting effects.

        Args:
            pattern: Binary weave pattern
            weft_color: Color for weft threads
            output_size: (height, width) of output texture

        Returns:
            Rendered texture with lighting
        """
        sim_h, sim_w = output_size
        ph, pw = pattern.shape

        # Tile pattern to fill output
        full_pattern = np.tile(
            pattern,
            (sim_h // ph + 1, sim_w // pw + 1)
        )
        full_pattern = full_pattern[:sim_h, :sim_w]

        # Create color layers
        warp_layer = np.full(
            (sim_h, sim_w, 3), self.warp_color, dtype=np.uint8)
        weft_layer = np.full((sim_h, sim_w, 3), weft_color, dtype=np.uint8)

        # Combine based on pattern
        # 1 = warp visible, 0 = weft visible
        pattern_3ch = np.dstack([full_pattern] * 3)
        base_texture = np.where(pattern_3ch == 1, warp_layer, weft_layer)

        # Apply 3D lighting
        lit_texture = self._apply_lighting(base_texture, full_pattern)

        return lit_texture

    def _apply_lighting(
        self,
        texture: np.ndarray,
        pattern: np.ndarray
    ) -> np.ndarray:
        """
        Apply advanced 3D lighting effects to simulate thread depth.

        Uses Sobel edge detection to create pseudo-normal maps,
        simulating raised warp threads and recessed weft threads.

        Args:
            texture: Base texture without lighting
            pattern: Binary weave pattern for normal calculation

        Returns:
            Texture with realistic lighting
        """
        # Convert to float for lighting calculations
        texture_f = texture.astype(np.float32)

        # Calculate pseudo-normals using Sobel operators
        gray_pattern = pattern.astype(np.float32)

        # Gradients
        sobelx = cv2.Sobel(gray_pattern, cv2.CV_32F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_pattern, cv2.CV_32F, 0, 1, ksize=3)

        # Combine gradients for lighting
        # Simulates light from top-left
        lighting = (sobelx + sobely) * self.light_intensity

        # Apply to all channels
        lighting_3ch = np.dstack([lighting] * 3)

        # Add lighting
        texture_f += lighting_3ch

        # Clip and convert back
        texture_lit = np.clip(texture_f, 0, 255).astype(np.uint8)

        return texture_lit

    def simulate_fast(
        self,
        design_img: np.ndarray,
        weave_map_dict: dict[tuple[int, int, int], str],
        weave_manager: WeaveManager
    ) -> np.ndarray:
        """
        Fast simulation mode with reduced quality.

        Useful for real-time preview or large images.

        Args:
            design_img: Input design
            weave_map_dict: Color to weave mapping
            weave_manager: Weave pattern manager

        Returns:
            Simulated fabric (without lighting)
        """
        # Temporarily reduce scale and disable lighting
        original_scale = self.scale
        original_light = self.light_intensity

        self.scale = 1
        self.light_intensity = 0.0

        try:
            result = self.simulate(design_img, weave_map_dict, weave_manager)
            return result
        finally:
            # Restore settings
            self.scale = original_scale
            self.light_intensity = original_light
