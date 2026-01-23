"""
Content-Aware Tools for SJ-DAS.

Photoshop-quality content-aware features including Fill, Scale, and Move.
Uses advanced algorithms like patch-based synthesis and seam carving.
"""

import logging
from typing import Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger("SJ_DAS.ContentAware")


class ContentAwareFill:
    """
    Photoshop's Content-Aware Fill.

    Uses patch-based synthesis to intelligently fill selected areas
    by sampling from surrounding context.
    """

    def __init__(self):
        self.patch_size = 9
        self.search_area = 50

    def fill_selection(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        use_ai: bool = True
    ) -> np.ndarray:
        """
        Fill selection with content-aware algorithm.

        Args:
            image: Source image (RGB)
            mask: Selection mask (255 = fill, 0 = keep)
            use_ai: Use AI model if available (StyleGAN)

        Returns:
            Image with filled selection
        """
        if use_ai:
            # Use StyleGAN for AI-powered fill (if model available)
            return self._ai_fill(image, mask)
        else:
            # Use patch-based synthesis
            return self._patch_fill(image, mask)

    def _patch_fill(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Patch-based content-aware fill."""
        # Use OpenCV's inpainting as base
        result = cv2.inpaint(
            image,
            mask,
            inpaintRadius=self.patch_size,
            flags=cv2.INPAINT_TELEA
        )

        logger.debug("Applied patch-based content-aware fill")
        return result

    def _ai_fill(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        AI-powered fill using StyleGAN.

        Generates a contextual textile pattern and seamlessly blends it
        into the masked region.
        """
        try:
            # Lazy import to avoid circular dependency
            from sj_das.ai.model_manager import ModelManager

            # 1. Get/Load Model
            manager = ModelManager()
            if not manager.load_stylegan():
                logger.warning(
                    "StyleGAN not available - falling back to patch fill")
                return self._patch_fill(image, mask)

            # 2. Analyze Mask Bounding Box
            ys, xs = np.where(mask > 0)
            if len(ys) == 0:
                return image

            y_min, y_max = np.min(ys), np.max(ys)
            x_min, x_max = np.min(xs), np.max(xs)

            h_hole = y_max - y_min
            w_hole = x_max - x_min

            # 3. Generate AI Pattern
            # Use a random seed based on hole position for consistency
            seed = int(x_min * y_min) % 10000
            generated_pattern = manager.generate_textile(
                seed=seed, optimize_seamless=True)

            # 4. Prepare Source Patch
            # Resize or tile generated pattern to cover the hole
            # StyleGAN output is 512x512
            patch_h, patch_w = generated_pattern.shape[:2]

            # If hole is bigger than generation, tile it
            if h_hole > patch_h or w_hole > patch_w:
                # Simple resize for now to fit context
                # Ideally we would tile, but resizing maintains structure
                # better for StyleGAN
                scale = max(h_hole / patch_h, w_hole / patch_w)
                new_size = (int(patch_w * scale * 1.2),
                            int(patch_h * scale * 1.2))  # 20% margin
                source_patch = cv2.resize(generated_pattern, new_size)
            else:
                source_patch = generated_pattern

            # Crop center of patch to fit hole size (plus margin for blending)
            ph, pw = source_patch.shape[:2]
            cy, cx = ph // 2, pw // 2

            # Center of the hole in target image
            center = (x_min + w_hole // 2, y_min + h_hole // 2)

            # 5. Poisson Blending
            # cv2.seamlessClone requires source, destination, mask, center,
            # flags

            # We need a source patch that covers the hole.
            # Let's take the entire generated pattern as source
            # But seamlessClone expects source to be approximately same size as hole area?
            # No, it clones the whole source content into dest at center.
            # We should crop source to be slightly larger than hole.

            # Crop source to hole size
            # Actually, let's use the full generated pattern if it fits reasonably,
            # or crop to bounds.

            # Better approach:
            # 1. Create a transparent layer with generated pattern
            # 2. Use Normal seamless clone for texture transfer

            try:
                # Normal Clone: Preserves texture
                # Mixed Clone: Transparency handling

                # Check bounds
                if source_patch.shape[0] < h_hole or source_patch.shape[1] < w_hole:
                    source_patch = cv2.resize(
                        source_patch, (w_hole + 20, h_hole + 20))

                # We need a mask for the SOURCE patch.
                # All white = copy everything
                src_mask = 255 * \
                    np.ones(source_patch.shape, source_patch.dtype)

                # Seamless Clone
                result = cv2.seamlessClone(
                    source_patch,
                    image,
                    src_mask,
                    center,
                    cv2.NORMAL_CLONE
                )

                logger.info(f"AI Fill applied successfully at {center}")
                return result

            except Exception as e:
                logger.error(
                    f"Poisson blending failed: {e}. Falling back to overly.")
                # Fallback: simple copy
                res = image.copy()
                # Determine region
                y1 = max(0, center[1] - ph // 2)
                y2 = min(image.shape[0], y1 + ph)
                x1 = max(0, center[0] - pw // 2)
                x2 = min(image.shape[1], x1 + pw)

                res[y1:y2, x1:x2] = source_patch[:(y2 - y1), :(x2 - x1)]
                return res

        except Exception as e:
            logger.error(f"AI Fill failed: {e}")
            return self._patch_fill(image, mask)

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Content-Aware Fill",
            "Content-Aware Fill settings coming soon.")


class ContentAwareScale:
    """
    Seam Carving for intelligent image scaling.

    Preserves important content while resizing by removing/adding
    low-energy seams.
    """

    def __init__(self):
        self.protect_mask = None

    def scale(
        self,
        image: np.ndarray,
        target_size: Tuple[int, int],
        protect_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Scale image using seam carving.

        Args:
            image: Source image
            target_size: (width, height) target size
            protect_mask: Mask of areas to protect (255 = protect)

        Returns:
            Scaled image
        """
        h, w = image.shape[:2]
        target_w, target_h = target_size

        result = image.copy()

        # Horizontal seam carving
        if target_w < w:
            result = self._remove_vertical_seams(
                result, w - target_w, protect_mask)
        elif target_w > w:
            result = self._add_vertical_seams(
                result, target_w - w, protect_mask)

        # Vertical seam carving
        h_current = result.shape[0]
        if target_h < h_current:
            result = self._remove_horizontal_seams(
                result, h_current - target_h, protect_mask)
        elif target_h > h_current:
            result = self._add_horizontal_seams(
                result, target_h - h_current, protect_mask)

        logger.debug(
            f"Content-aware scaled from {w}x{h} to {target_w}x{target_h}")
        return result

    def show_dialog(self):
        """Show parameters dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Content-Aware Scale",
            "Content-Aware Scale settings coming soon.")

    def _calculate_energy(self, image: np.ndarray) -> np.ndarray:
        """Calculate energy map using gradient magnitude."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Sobel gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        # Energy = gradient magnitude
        energy = np.abs(grad_x) + np.abs(grad_y)

        return energy

    def _find_vertical_seam(self, energy: np.ndarray) -> np.ndarray:
        """Find minimum energy vertical seam using dynamic programming."""
        h, w = energy.shape

        # DP table
        dp = energy.copy()

        # Fill DP table
        for i in range(1, h):
            for j in range(w):
                # Check three possible previous positions
                if j == 0:
                    dp[i, j] += min(dp[i - 1, j], dp[i - 1, j + 1])
                elif j == w - 1:
                    dp[i, j] += min(dp[i - 1, j - 1], dp[i - 1, j])
                else:
                    dp[i, j] += min(dp[i - 1, j - 1],
                                    dp[i - 1, j], dp[i - 1, j + 1])

        # Backtrack to find seam
        seam = np.zeros(h, dtype=int)
        seam[-1] = np.argmin(dp[-1])

        for i in range(h - 2, -1, -1):
            j = seam[i + 1]
            if j == 0:
                seam[i] = j if dp[i, j] <= dp[i, j + 1] else j + 1
            elif j == w - 1:
                seam[i] = j - 1 if dp[i, j - 1] < dp[i, j] else j
            else:
                idx = np.argmin([dp[i, j - 1], dp[i, j], dp[i, j + 1]])
                seam[i] = j + idx - 1

        return seam

    def _remove_vertical_seams(
        self,
        image: np.ndarray,
        num_seams: int,
        protect_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Remove vertical seams to reduce width."""
        result = image.copy()

        for _ in range(num_seams):
            energy = self._calculate_energy(result)

            # Increase energy for protected areas
            if protect_mask is not None:
                energy[protect_mask > 0] = energy.max() * 2

            seam = self._find_vertical_seam(energy)

            # Remove seam
            h, w = result.shape[:2]
            mask = np.ones((h, w), dtype=bool)
            for i, j in enumerate(seam):
                mask[i, j] = False

            result = result[mask].reshape(h, w - 1, 3)

        return result

    def _add_vertical_seams(
        self,
        image: np.ndarray,
        num_seams: int,
        protect_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Add vertical seams to increase width."""
        # Find seams to duplicate
        seams = []
        temp_image = image.copy()

        for _ in range(num_seams):
            energy = self._calculate_energy(temp_image)
            seam = self._find_vertical_seam(energy)
            seams.append(seam)

            # Remove seam from temp for next iteration
            h, w = temp_image.shape[:2]
            mask = np.ones((h, w), dtype=bool)
            for i, j in enumerate(seam):
                mask[i, j] = False
            temp_image = temp_image[mask].reshape(h, w - 1, 3)

        # Add seams to original
        result = image.copy()
        for seam in reversed(seams):
            h, w = result.shape[:2]
            new_image = np.zeros((h, w + 1, 3), dtype=result.dtype)

            for i in range(h):
                j = seam[i]
                new_image[i, :j] = result[i, :j]
                # Average with neighbor
                if j < w - 1:
                    new_image[i, j] = (result[i, j].astype(
                        int) + result[i, j + 1].astype(int)) // 2
                else:
                    new_image[i, j] = result[i, j]
                new_image[i, j + 1:] = result[i, j:]

            result = new_image

        return result

    def _remove_horizontal_seams(
        self,
        image: np.ndarray,
        num_seams: int,
        protect_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Remove horizontal seams (transpose, remove vertical, transpose back)."""
        transposed = np.transpose(image, (1, 0, 2))
        if protect_mask is not None:
            protect_mask = protect_mask.T
        result = self._remove_vertical_seams(
            transposed, num_seams, protect_mask)
        return np.transpose(result, (1, 0, 2))

    def _add_horizontal_seams(
        self,
        image: np.ndarray,
        num_seams: int,
        protect_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Add horizontal seams."""
        transposed = np.transpose(image, (1, 0, 2))
        if protect_mask is not None:
            protect_mask = protect_mask.T
        result = self._add_vertical_seams(transposed, num_seams, protect_mask)
        return np.transpose(result, (1, 0, 2))


class ContentAwareMove:
    """
    Move objects with automatic background fill.

    Combines selection moving with content-aware fill.
    """

    def __init__(self):
        self.filler = ContentAwareFill()

    def move_object(
        self,
        image: np.ndarray,
        selection_mask: np.ndarray,
        offset: Tuple[int, int]
    ) -> np.ndarray:
        """
        Move selected object and fill original area.

        Args:
            image: Source image
            selection_mask: Object selection (255 = selected)
            offset: (dx, dy) movement offset

        Returns:
            Image with moved object
        """
        h, w = image.shape[:2]
        dx, dy = offset

        # Extract selected object
        object_pixels = image.copy()
        object_pixels[selection_mask == 0] = 0

        # Fill original area
        filled = self.filler.fill_selection(image, selection_mask)

        # Create moved object
        moved_mask = np.zeros_like(selection_mask)
        moved_object = np.zeros_like(image)

        # Calculate valid region for moved object
        src_y1 = max(0, -dy)
        src_y2 = min(h, h - dy)
        src_x1 = max(0, -dx)
        src_x2 = min(w, w - dx)

        dst_y1 = max(0, dy)
        dst_y2 = min(h, h + dy)
        dst_x1 = max(0, dx)
        dst_x2 = min(w, w + dx)

        # Move object
        moved_object[dst_y1:dst_y2,
                     dst_x1:dst_x2] = object_pixels[src_y1:src_y2,
                                                    src_x1:src_x2]
        moved_mask[dst_y1:dst_y2,
                   dst_x1:dst_x2] = selection_mask[src_y1:src_y2,
                                                   src_x1:src_x2]

        # Composite moved object over filled background
        result = filled.copy()
        result[moved_mask > 0] = moved_object[moved_mask > 0]

        logger.debug(f"Moved object by offset ({dx}, {dy})")
        return result
