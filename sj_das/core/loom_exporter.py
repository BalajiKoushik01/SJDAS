"""Loom Exporter - Final BMP Generation.

Generates loom-ready BMP files with embedded metadata and proper formatting
for jacquard loom machines.
"""

import logging

import cv2
import numpy as np

from sj_das.core.bmp_metadata import BMPMetadata
from sj_das.core.weave_manager import WeaveManager

logger = logging.getLogger(__name__)


class LoomExporter:
    """
    Professional loom BMP exporter.

    Generates machine-ready BMP files with:
    - Exact dimensions (hooks × picks)
    - Embedded metadata
    - Float safety validation
    - Proper color indexing
    """

    def __init__(self):
        """Initialize loom exporter."""
        self.weave_manager = WeaveManager()

    def export(
        self,
        image: np.ndarray,
        output_path: str,
        hooks: int,
        picks: int,
        reed: int,
        component: str,
        weave_map: dict[int, dict[str, str]],
        khali: int = 1,
        locking: int = 0,
        validate_float: bool = True,
        auto_fix_floats: bool = False,
        max_float: int = 20,
        designer: str = "Unknown",
        notes: str = ""
    ) -> bool:
        """
        Export image as loom-ready BMP.

        Args:
            image: Design image (numpy array)
            output_path: Output BMP file path
            hooks: Total warp threads
            picks: Total weft shots
            reed: Thread density
            component: Component type
            weave_map: Color index to weave pattern mapping
            khali: Pattern repeats (default 1)
            locking: Overlap pixels (default 0)
            validate_float: Check float safety (default True)
            designer: Designer name
            notes: Additional notes

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting loom export: {hooks}×{picks}")

            # Resize to exact dimensions using NEAREST for graph paper style
            # This preserves sharp pixel boundaries (no anti-aliasing)
            resized = cv2.resize(
                image,
                (hooks, picks),
                interpolation=cv2.INTER_NEAREST
            )

            # Enforce strict palette (Graph Paper Style)
            # Snap all colors to nearest palette color (no gradients)
            if len(resized.shape) == 3:
                resized = self._enforce_strict_palette(resized)

            # Auto-Fix Floats (Locking)
            if auto_fix_floats and len(image.shape) == 2:
                logger.info(f"Running float auto-fix (max {max_float}px)...")
                fixed_img, fixes = self.weave_manager.auto_lock_floats(
                    resized, max_float=max_float)
                if fixes > 0:
                    logger.info(f"Auto-locked {fixes} float violations.")
                    resized = fixed_img

            # Validate float safety if requested
            if validate_float and len(image.shape) == 2:
                is_safe, problem_areas = self.weave_manager.check_float_safety(
                    resized,
                    max_float=20
                )

                if not is_safe:
                    logger.warning(
                        f"Float safety issues detected in {len(problem_areas)} areas")
                    # Continue anyway but log warning

            # Save as BMP (Force 8-bit Indexed for Loom)
            # Loom machines ignore RGB, they need values 1,2,3... pointing to
            # hooks/weaves.

            # If RGB, convert to Indexed
            if len(resized.shape) == 3:
                # Quantize/Index
                # Find unique colors
                unique_colors, indices = np.unique(
                    resized.reshape(-1, 3), axis=0, return_inverse=True)

                # Limit to 256 colors
                if len(unique_colors) > 256:
                    logger.warning(
                        "Reducing colors to 256 for BMP index limit")
                    # (Simple truncation for now, real app should dither or error)
                    unique_colors = unique_colors[:256]
                    indices = np.clip(indices, 0, 255)

                # Store Palette
                yarn_colors = [color.tolist() for color in unique_colors]

                # Reshape indices to 2D
                indexed_img = indices.reshape((picks, hooks)).astype(np.uint8)

                # We can't use cv2.imwrite for indexed images easily without a palette.
                # Use PIL for saving Indexed BMP
                from PIL import Image
                pil_img = Image.fromarray(indexed_img, mode='P')

                # Prepare Palette (Flattened [R,G,B, R,G,B...])
                # CV2 is BGR, PIL needs RGB
                flat_palette = []
                for b, g, r in unique_colors:
                    flat_palette.extend([r, g, b])

                # Pad palette to 768
                flat_palette.extend([0] * (768 - len(flat_palette)))
                pil_img.putpalette(flat_palette)

                pil_img.save(output_path)
            else:
                # Already grayscale/indexed
                cv2.imwrite(output_path, resized)

            # Create and embed metadata
            # yarn_colors already populated above if RGB, else handle grayscale
            if len(yarn_colors) == 0 and len(image.shape) == 2:
                # Assume grayscale 0-255 are the indices
                yarn_colors = [[i, i, i] for i in range(256)]

            metadata = BMPMetadata.create_metadata(
                hooks=hooks,
                picks=picks,
                reed=reed,
                component=component,
                khali=khali,
                locking=locking,
                weave_map=weave_map,
                yarn_colors=yarn_colors,
                designer=designer,
                notes=notes
            )

            # Validate metadata
            if not BMPMetadata.validate_metadata(metadata):
                logger.error("Metadata validation failed")
                return False

            # Embed metadata
            if not BMPMetadata.embed(output_path, metadata):
                logger.error("Failed to embed metadata")
                return False

            logger.info(f"Successfully exported to {output_path}")
            logger.info(f"Dimensions: {hooks}×{picks}, Component: {component}")

            return True

        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            return False

    def _enforce_strict_palette(
            self, image: np.ndarray, max_colors: int = 16) -> np.ndarray:
        """
        Enforce strict color palette by quantizing to nearest colors.

        This ensures graph paper style with no gradients or anti-aliasing.
        Uses k-means clustering to find optimal palette, then snaps all pixels.

        Args:
            image: BGR image
            max_colors: Maximum number of colors (default 16)

        Returns:
            Image with strict palette (no gradients)
        """
        h, w, c = image.shape

        # Reshape for clustering
        pixels = image.reshape(-1, 3).astype(np.float32)

        # Use k-means to find optimal palette
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixels,
            max_colors,
            None,
            criteria,
            10,
            cv2.KMEANS_PP_CENTERS
        )

        # Round centers to exact integer values (no sub-pixel colors)
        centers = np.round(centers).astype(np.uint8)

        # Map each pixel to its cluster center
        quantized = centers[labels.flatten()]

        # Reshape back to image
        return quantized.reshape(h, w, c)

    def validate_dimensions(
        self,
        hooks: int,
        picks: int
    ) -> tuple[bool, str | None]:
        """
        Validate loom dimensions.

        Args:
            hooks: Warp threads
            picks: Weft shots

        Returns:
            (is_valid, error_message)
        """
        if hooks < 100:
            return False, "Hooks must be at least 100"

        if hooks > 4800:
            return False, "Hooks cannot exceed 4800 (machine limit)"

        if picks < 50:
            return False, "Picks must be at least 50"

        if picks > 10000:
            return False, "Picks cannot exceed 10000 (practical limit)"

        return True, None

    def estimate_file_size(self, hooks: int, picks: int,
                           bit_depth: int = 8) -> int:
        """
        Estimate output BMP file size.

        Args:
            hooks: Width
            picks: Height
            bit_depth: 1 or 8

        Returns:
            Approximate file size in bytes
        """
        # BMP header: 54 bytes
        # Palette (if 8-bit): 256 * 4 bytes
        # Pixel data: width * height * (bit_depth / 8)

        header_size = 54
        palette_size = 1024 if bit_depth == 8 else 0

        if bit_depth == 1:
            # 1-bit: 8 pixels per byte, rows padded to 4-byte boundary
            row_bytes = ((hooks + 31) // 32) * 4
            pixel_data = row_bytes * picks
        else:
            # 8-bit: 1 byte per pixel, rows padded to 4-byte boundary
            row_bytes = ((hooks + 3) // 4) * 4
            pixel_data = row_bytes * picks

        return header_size + palette_size + pixel_data
