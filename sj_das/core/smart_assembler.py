import cv2
import numpy as np


class SmartAssembler:
    """
    Intelligent Assembler for Saree Components.
    Features:
    - Gradient Blending for Seamless Stitching (Seam Hiding)
    - Auto-Resizing
    """

    def stitch_border_body(self, body_img, border_img,
                           vertical=True, overlap=0):
        """
        Intelligently stitches Body and Border.
        Supports 'Overlap' and 'Gradient Blending' for smooth transitions.
        """
        if body_img is None or border_img is None:
            return None

        # Ensure types (CV2 BGR)
        # Resize border to match body dimension (Hooks/Width or Picks/Height)
        h_body, w_body = body_img.shape[:2]
        h_border, w_border = border_img.shape[:2]

        if vertical:
            # Vertical Stitch (Border Top, Body Bottom)
            # Match Width
            if w_border != w_body:
                # Use Lanczos4 for high quality resizing of patterns
                border_resized = cv2.resize(
                    border_img, (w_body, h_border), interpolation=cv2.INTER_LANCZOS4)
            else:
                border_resized = border_img

            total_h = h_body + h_border - overlap
            canvas = np.zeros((total_h, w_body, 3), dtype=np.uint8)

            # Place Border (Top)
            canvas[0:h_border, :] = border_resized

            # Start Y for Body
            start_y = h_border - overlap

            if overlap > 0:
                # Gradient Blend the Overlap Region
                roi_border = border_resized[-overlap:, :]
                roi_body = body_img[0:overlap, :]

                # Vertical Gradient (0 to 1)
                alpha = np.linspace(0, 1, overlap).reshape(-1, 1, 1)

                # Blend: Body * Alpha + Border * (1 - Alpha)
                # Note: We want Border to fade out (1->0) and Body to fade in (0->1) as we go down?
                # Actually, standard is simple linear cross-fade.
                blended = (roi_body * alpha + roi_border *
                           (1 - alpha)).astype(np.uint8)

                # Copy Blended Zone
                canvas[start_y: start_y + overlap, :] = blended

                # Copy Rest of Body
                canvas[start_y + overlap:, :] = body_img[overlap:, :]
            else:
                # No overlap, simple stacking
                canvas[h_border:, :] = body_img

            return canvas

        else:
            # Horizontal Stitch (Body Left, Border Right)
            # Match Height
            if h_border != h_body:
                border_resized = cv2.resize(
                    border_img, (w_border, h_body), interpolation=cv2.INTER_LANCZOS4)
            else:
                border_resized = border_img

            total_w = w_body + w_border - overlap
            canvas = np.zeros((h_body, total_w, 3), dtype=np.uint8)

            # Place Body (Left)
            canvas[:, 0:w_body] = body_img

            start_x = w_body - overlap

            if overlap > 0:
                # Gradient Blend
                roi_body = body_img[:, -overlap:]
                roi_border = border_resized[:, 0:overlap]

                # Horizontal Gradient
                alpha = np.linspace(0, 1, overlap).reshape(1, -1, 1)

                # Blend
                blended = (roi_border * alpha + roi_body *
                           (1 - alpha)).astype(np.uint8)

                canvas[:, start_x: start_x + overlap] = blended
                canvas[:, start_x + overlap:] = border_resized[:, overlap:]
            else:
                canvas[:, w_body:] = border_resized

            return canvas

    def assemble_saree_layout(self, body_img, border_img,
                              pallu_img, loom_width=480, border_mode="double_sided"):
        """
        Assembles a full Saree Design BMP from components.
        Structure: [Pallu] + [Body with Borders].

        Args:
            body_img (np.array): Pattern for the main body.
            border_img (np.array): Pattern for the border.
            pallu_img (np.array): Pattern for the pallu (head).
            loom_width (int): Target width in hooks (e.g., 240, 480, 960).
            border_mode (str): 'top_bottom', 'single', or 'sidebar'.

        Returns:
            np.array: Full assembled Saree BMP (Vertical strip).
        """
        # 1. Resize/Normalize Widths
        # Pallu dictates the width usually, or Loom Width is king.
        # Let's force everything to Loom Width.

        # --- PREPARE PALLU ---
        if pallu_img is not None:
            h_pallu, w_pallu = pallu_img.shape[:2]
            if w_pallu != loom_width:
                pallu_final = cv2.resize(
                    pallu_img, (loom_width, h_pallu), interpolation=cv2.INTER_LANCZOS4)
            else:
                pallu_final = pallu_img
        else:
            pallu_final = None

        # --- PREPARE BORDER ---
        border_top = None
        border_bottom = None

        if border_img is not None:
            h_border, w_border = border_img.shape[:2]
            # Is border horizontal or vertical?
            # Assuming standard border strip: Height is "Border Width".
            # We scale border to be proportionally nice? Or keep original?
            # Usually keep original height unless huge.

            # If width != loom_width, we assume we need to REPEAT it horizontally?
            # Or Resize?
            # Usually border is repeating pattern.
            # Smart Tile Logic:
            border_final = self._tile_horizontally(border_img, loom_width)

            if border_mode == "top_bottom" or border_mode == "double_sided":
                border_top = border_final
                border_bottom = cv2.flip(
                    border_final, 0)  # Mirror for bottom usually
            elif border_mode == "single":
                border_bottom = border_final

        # --- PREPARE BODY ---
        # Body needs to fill the space between borders.
        if body_img is not None:
            # Space available
            h_b, w_b = body_img.shape[:2]

            border_h_total = 0
            if border_top is not None:
                border_h_total += border_top.shape[0]
            if border_bottom is not None:
                border_h_total += border_bottom.shape[0]

            body_target_h = max(h_b, 100)  # Minimum height

            # Tile/Resize Body to fit WIDTH (Loom Width)
            # Body is usually a repeating tile.
            body_final = self._tile_horizontally_and_vertically(
                body_img, loom_width, body_target_h)

            # Composite Body Area
            # Create Canvas for "Body Section"
            body_section_h = body_final.shape[0] + border_h_total
            body_section = np.zeros(
                (body_section_h, loom_width, 3), dtype=np.uint8)

            y_cursor = 0
            # Place Top Border
            if border_top is not None:
                h_bt = border_top.shape[0]
                body_section[0:h_bt, :] = border_top
                y_cursor += h_bt

            # Place Main Body
            h_main = body_final.shape[0]
            body_section[y_cursor: y_cursor + h_main, :] = body_final
            y_cursor += h_main

            # Place Bottom Border
            if border_bottom is not None:
                h_bb = border_bottom.shape[0]
                body_section[y_cursor: y_cursor + h_bb, :] = border_bottom

        else:
            body_section = None

        # --- FINAL ASSEMBLY ---
        # [PALLU]
        # [BODY SECTION]

        parts = []
        if pallu_final is not None:
            parts.append(pallu_final)
        if body_section is not None:
            parts.append(body_section)

        if not parts:
            return None

        # VStack
        return np.vstack(parts)

    def _tile_horizontally(self, img, target_w):
        """Tiles an image horizontally to fill target width."""
        h, w = img.shape[:2]
        if w >= target_w:
            return img[:, 0:target_w]  # Crop

        # Tile
        repeats = (target_w // w) + 1
        tiled = np.tile(img, (1, repeats, 1))
        return tiled[:, 0:target_w]

    def _tile_horizontally_and_vertically(self, img, w, h):
        # 1. Tile Horz
        img_h = self._tile_horizontally(img, w)
        # 2. Tile Vert
        curr_h = img_h.shape[0]
        if curr_h >= h:
            return img_h[0:h, :]

        repeats = (h // curr_h) + 1
        tiled = np.tile(img_h, (repeats, 1, 1))
        return tiled[0:h, :]

    def detect_regions(self, full_saree_img):
        """
        Auto-detects Pallu and Border vs Body using Texture Analysis.
        Logic: Pallu is usually high-entropy/complex. Body is repeating.
        """
        # Convert to Grayscale
        gray = cv2.cvtColor(full_saree_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 1. Detect Borders (Horizontal Strips at Top/Bottom)
        # Scanline variance?
        # Variance of rows.
        np.var(gray, axis=1)
        # Border areas might have different variance profile than body.
        # But for now, let's just use heuristic: Top 15% and Bottom 15%?

        # 2. Detect Pallu (Usually Left or Right side, or Top?)
        # In Loom BMP, Pallu is usually at the TOP (Start).
        # We can look for a "Change Point" in the pattern along Y axis.

        # Calculate row-wise correlation with the first row?
        # Or simpler: Split into chunks and compare color histograms.

        # Heuristic for now:
        pallu_h = int(h * 0.2)  # First 20%
        body_y = pallu_h

        return {
            "pallu": (0, 0, w, pallu_h),
            "body": (0, body_y, w, h - body_y)
        }
