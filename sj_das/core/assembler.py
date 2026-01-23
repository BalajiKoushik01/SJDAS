import cv2
import numpy as np


class AssemblerEngine:
    """
    Handles the assembly of saree components (Body, Borders, Pallu, Skirt)
    based on loom specifications (Acchu, Kali, Locking).

    Industry-Standard Saree Assembly:
    - Acchu: Total loom width in hooks/pixels
    - Kali: Number of vertical panels (body is divided into kali sections)
    - Locking: Overlap between adjacent kali panels for weave interlocking
    - Border: Fixed width decorative bands on left and right edges
    - Body: Central section, may be tiled vertically into kali panels
    - Pallu: Decorative end piece, appended vertically
    """

    def __init__(self):
        pass

    def assemble_saree(self, components, config):
        """
        Assembles the saree image according to jacquard loom specifications.

        Args:
            components (dict): Dictionary containing image paths or arrays for:
                               'body', 'border_l', 'border_r', 'pallu', 'skirt'.
            config (dict): Dictionary containing:
                           'acchu': Total width in hooks (pixels).
                           'kali': Number of body panels (vertical repeats).
                           'locking': Overlap pixels between kali panels.

        Returns:
            np.array: Assembled image (BGR).
        """
        # Load all components
        loaded_imgs = {}

        for key, val in components.items():
            if val is not None:
                img = cv2.imread(val) if isinstance(val, str) else val

                if img is not None:
                    loaded_imgs[key] = img

        if not loaded_imgs:
            raise ValueError("No valid components provided.")

        # Configuration
        total_width = config.get('acchu', 2400)  # Total loom width
        kali = config.get('kali', 1)  # Number of vertical panels
        locking = config.get('locking', 4)  # Overlap between panels

        # Step 1: Determine Border Widths
        # Borders are fixed-width decorative bands on edges
        border_l_img = loaded_imgs.get('border_l')
        border_r_img = loaded_imgs.get('border_r')

        border_l_w = border_l_img.shape[1] if border_l_img is not None else 0
        border_r_w = border_r_img.shape[1] if border_r_img is not None else 0

        # Step 2: Calculate Body Space
        # Body occupies the space between borders
        body_space = total_width - border_l_w - border_r_w

        if body_space <= 0:
            raise ValueError(
                f"Borders too wide ({border_l_w + border_r_w} px) for Acchu ({total_width} px).")

        # Step 3: Process Body with Kali
        # Kali = number of vertical panels, each with potential locking overlap
        body_img = loaded_imgs.get('body')
        skirt_img = loaded_imgs.get('skirt')

        if body_img is None and skirt_img is None:
            raise ValueError("At least Body or Skirt must be provided.")

        # Use body if available, otherwise use skirt as body
        primary_body = body_img if body_img is not None else skirt_img

        # Calculate panel dimensions
        # Each kali panel has width = body_space
        # Panels are stacked vertically with locking overlap
        # Total height = (panel_height * kali) - (locking * (kali - 1))

        # Resize body width?
        # Requirement: "Xerox Mode" usually implies maintaining the exact weave structure.
        # If Body Image < Space, we should TILE (REPEAT) it.
        # If Body Image > Space, we should CROP or error. Resizing destroys the weave.
        # We will TILE horizontally.

        body_h, body_w = primary_body.shape[:2]

        # Step 3a: Create the "Panel" for one vertical repeat
        # We tile primary_body horizontally to fill body_space
        if body_w < body_space:
            # Calculate horizontal repeats
            repeats_x = int(np.ceil(body_space / body_w))
            raw_panel = np.tile(primary_body, (1, repeats_x, 1))
            # Crop to exact space
            resized_body_panel = raw_panel[:, :body_space]
        else:
            # Crop or Resize? For Loom files, Crop is safer to preserve pixel grid.
            # Or Resize if user intends to scale.
            # Given "Xerox", we assume scaling might be unwanted, but if it's a photo...
            # Let's stick to CROP for precision or RESIZE if drastically different?
            # Let's CROP for now to "intended output".
            resized_body_panel = primary_body[:, :body_space]
            # Note: A real "Smart" system might ask, but Tiling/Cropping is
            # standard for repetitive texturing.

        # Calculate total body section height
        panel_height = resized_body_panel.shape[0]
        total_body_height = (panel_height * kali) - (locking * (kali - 1))

        # Create body canvas
        body_canvas = np.zeros(
            (total_body_height, body_space, 3), dtype=np.uint8)

        # Tile body panels vertically with locking overlap
        for k in range(kali):
            y_start = k * (panel_height - locking)
            y_end = y_start + panel_height

            # Ensure we don't exceed canvas
            if y_end > total_body_height:
                y_end = total_body_height

            h_to_place = y_end - y_start
            if h_to_place <= 0:
                continue

            panel_to_place = resized_body_panel[:h_to_place, :]

            # Place on canvas
            # Locking: In Loom/Index mode, we simply Overwrite (Last wins).
            # No averaging.
            body_canvas[y_start:y_end, :] = panel_to_place

        # Step 4: Add Skirt Overlay (if separate from body)
        if skirt_img is not None and body_img is not None:
            # Skirt is a bottom overlay
            s_h, s_w = skirt_img.shape[:2]
            skirt_resized = cv2.resize(skirt_img, (body_space, s_h))

            # Place at bottom of body canvas
            y_offset = total_body_height - s_h
            if y_offset < 0:
                y_offset = 0
                skirt_resized = skirt_resized[:total_body_height, :]

            body_canvas[y_offset:, :] = skirt_resized

        # Step 5: Create Full Width Canvas (with borders)
        full_width_canvas = np.zeros(
            (total_body_height, total_width, 3), dtype=np.uint8)

        # Place left border (tile vertically to match height)
        if border_l_img is not None:
            border_l_img.shape[0]
            # Tile or stretch to match height
            border_l_tiled = self._tile_vertical(
                border_l_img, total_body_height)
            full_width_canvas[:, :border_l_w] = border_l_tiled

        # Place body in center
        full_width_canvas[:, border_l_w:border_l_w + body_space] = body_canvas

        # Place right border (tile vertically to match height)
        if border_r_img is not None:
            border_r_img.shape[0]
            border_r_tiled = self._tile_vertical(
                border_r_img, total_body_height)
            full_width_canvas[:, total_width - border_r_w:] = border_r_tiled

        # Step 6: Append Pallu
        final_saree = full_width_canvas

        pallu_img = loaded_imgs.get('pallu')
        if pallu_img is not None:
            # Pallu spans full width (acchu)
            # Maintain aspect ratio for pallu height
            p_h, p_w = pallu_img.shape[:2]
            p_aspect = p_h / p_w
            pallu_height = int(total_width * p_aspect)

            pallu_resized = cv2.resize(pallu_img, (total_width, pallu_height))

            # Append pallu at the bottom
            final_saree = np.vstack([full_width_canvas, pallu_resized])

        return final_saree

    def _tile_vertical(self, img, target_height):
        """
        Tile an image vertically to reach target height.

        Args:
            img: Source image
            target_height: Desired height

        Returns:
            Tiled image
        """
        h, w = img.shape[:2]

        if h >= target_height:
            # Crop if too tall
            return img[:target_height, :]

        # Calculate number of tiles needed
        num_tiles = int(np.ceil(target_height / h))

        # Tile
        tiled = np.tile(img, (num_tiles, 1, 1))

        # Crop to exact height
        return tiled[:target_height, :]
