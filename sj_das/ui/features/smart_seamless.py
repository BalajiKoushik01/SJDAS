import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSlider,
                             QVBoxLayout)


class SmartSeamlessMaker:
    """
    Intelligent Seamless Texture Creator.

    Features:
    - **Edge Blending**: Automatically blends image edges to create tileable textures.
    - **Overlap Control**: Configurable overlap percentage for tuning blend smoothness.
    - **Context Aware**: Handles Horizontal and Vertical passes for perfect tiling.

    Usage:
    >>> maker = SmartSeamlessMaker(editor_instance)
    >>> maker.show_dialog()
    """

    def __init__(self, editor):
        self.editor = editor

    def show_dialog(self):
        dialog = SeamlessDialog(self.editor)
        if dialog.exec():
            # Get overlap %
            overlap = dialog.get_overlap()
            self._make_seamless(overlap)

    def _make_seamless(self, overlap_percent):
        img_rgb = self._get_cv_img()
        h, w = img_rgb.shape[:2]

        # Calculate pixel overlap
        ox = int(w * overlap_percent / 100.0)
        oy = int(h * overlap_percent / 100.0)

        if ox < 2 or oy < 2:
            return  # Too small

        # We need to blend Right edge into Left edge, Bottom into Top.
        # But for perfect tiling, we usually crop.
        # Strategy:
        # Result size = (W - ox), (H - oy)

        # 1. Horizontal Blend (Left-Right)
        # Main body: 0 to W-ox
        # To make it match right side:
        # We take the RIGHT STRIP (width ox) and blend it onto the LEFT STRIP
        # (width ox).

        # Slices
        img_rgb[:, 0:ox].astype(np.float32)
        img_rgb[:, w - ox:w].astype(np.float32)

        # Gradient Mask for blending (Left to Right: 0 to 1? No.)
        # We want the output Left Edge to match the Right Edge of the original?
        # No, we want Output Left edge == Output Right edge.
        # So we blend RightStrip ON TOP of LeftStrip?
        # Left side of result = Blend(LeftStrip, RightStrip)
        # Right side of result uses the original content just before the
        # RightStrip.

        # Wait, simple "Make Seamless":
        # Overlap the Right edge onto Left edge? But this reduces width.
        # Yes.

        # Linear gradient 0 -> 1
        alpha_x = np.linspace(0, 1, ox).reshape(1, ox, 1)
        alpha_x = np.tile(alpha_x, (h, 1, 3))

        # Blend: (Right * alpha) + (Left * (1-alpha))
        # Wait, if alpha=1 (Right side), we want Left content?
        # Seamless means: Left Edge == Right Edge.
        # So we create a "Seam" zone.
        # Let's say we output image of width W-ox.
        # The region 0..ox is the blended seam.
        # The region ox..W-ox is original.
        # At x=0, pixel should equal x=W-ox in output? No.

        # Correct logic:
        # Crop to (H, W-ox).
        # The "New Left Strip" (0..ox) is a blend of "Old Left" and "Old Right".
        # New Left = Old Left * (1 - Alpha) + Old Right * Alpha.
        # If Alpha goes 0->1:
        # At 0: Old Left.
        # At 1: Old Right.
        # So at x=ox in output, we are at Old Left+ox.
        # At x=0 in output, we are at Old Left (mostly).
        # This makes x=0 and x=W discontinuity?

        # Standard "Tile" alg:
        # 1. Cut image into 4 quadrants.
        # 2. Swap Diagonals (A B -> D C). Center becomes corners.
        # 3. Heal the new "Cross" in the middle.
        # This preserves size.

        # Let's implement Quadrant Swap + Cross Fading.

        # 1. Offset Image (Roll)
        shift_x = w // 2
        shift_y = h // 2

        start_img = np.roll(img_rgb, shift_x, axis=1)  # Horizontal Roll
        start_img = np.roll(start_img, shift_y, axis=0)  # Vertical Roll

        # Now boundaries are in the center (Cross shape).
        # We must blur/crossfade the center cross.

        # Define mask for center cross
        # Variable width based on overlap
        cx = w // 2
        h // 2

        # Vertical Seam Processing
        # Blend region: cx-ox/2 to cx+ox/2
        cx - ox // 2
        cx + ox // 2

        # We need source material to patch this seam?
        # In GIMP/Photoshop "Make Seamless", they usually just blend the edges and crop.
        # But preserving size is nicer.
        # Let's use simple Linear Blending roll-over for center.

        # Actually, standard "Make Seamless" reduces size. It's safer.
        # Let's use Size Reduction.

        # Prepare Result Arrays
        res_h = h - oy
        res_w = w - ox

        # 1. Horizontal Pass
        # Create temp image of size (H, W-ox)
        np.zeros((h, res_w, 3), dtype=np.float32)

        # Body (middle part)
        # We want final image:
        # 0..ox: Blend(Left, Right)
        # ox..res_w: Original(ox..res_w) ??
        # No.
        # Left part of output = Blend(Old Left, Old Right)
        # No, that forces periodicity but changes context.

        # Easier:
        # Output[x] = Input[x] * (1-alpha) + Input[x + res_w] * alpha
        # where alpha goes 0->1 across the overlap zone?
        # If we just linearly blend the overlap:
        # Overlap region is rightmost ox pixels of Input and leftmost ox of
        # Input.

        # Let's do:
        # Crop Left Strip (ox), Crop Right Strip (ox).
        # Center Body (W - 2*ox).

        # Simple algorithm that works:
        # Res = Input[0:res_w]
        # Blend Input[W-ox:W] onto Res[0:ox].
        # Alpha gradient 0->1.
        # Res[0:ox] = Res[0:ox]*(alpha) + Input[W-ox:W]*(1-alpha)
        # Wait, at index 0 (left edge), we want it to match index res_w (right edge).
        # Right edge of Res is Input[res_w].
        # Left edge of Res is Blended.
        # Input[W-ox] is... wait.

        # Let's stick to reliable method:
        # H-Pass:
        # Take Input[:, 0:res_w]
        # Take Overlap Source = Input[:, res_w:w] (width ox)
        # Blend Overlap Source INTO Input[:, 0:ox]
        # Using alpha gradient 0 (left) to 1 (right).
        # At x=0: Blend is Source (Right Edge).
        # At x=ox: Blend is Target (Left content).
        # So Left Edge becomes Right Edge. Seamless!

        # Do H-Pass
        h_pass = img_rgb[:, 0:res_w].astype(np.float32)  # Base
        source = img_rgb[:, res_w:w].astype(
            np.float32)  # The "extra" right strip

        # Gradient: 1.0 at x=0 (Full Source), 0.0 at x=ox (Full Base)
        # So Left Edge (x=0) looks like Right Edge (Source).
        # Right Edge of Base (x=res_w) is untouched.
        # So Left Edge == Source == Right Edge of Original?
        # Source was Right Edge of Original.
        # Yes.

        for i in range(ox):
            alpha = 1.0 - (i / float(ox))  # 1 -> 0
            h_pass[:, i] = h_pass[:, i] * (1.0 - alpha) + source[:, i] * alpha

        h_pass = h_pass.astype(np.uint8)

        # 2. Vertical Pass (on h_pass)
        # Target H: res_h
        # Take h_pass[0:res_h, :]
        # Source = h_pass[res_h:h, :]

        v_pass = h_pass[0:res_h, :].astype(np.float32)
        v_source = h_pass[res_h:h, :].astype(
            np.float32)  # The "extra" bottom strip

        for i in range(oy):
            alpha = 1.0 - (i / float(oy))
            v_pass[i, :] = v_pass[i, :] * \
                (1.0 - alpha) + v_source[i, :] * alpha

        final = np.clip(v_pass, 0, 255).astype(np.uint8)

        self._update_editor(final)

    def _get_cv_img(self):
        qimg = self.editor.get_image()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)  # Use RGB

    def _update_editor(self, rgb_img):
        h, w, ch = rgb_img.shape
        bpl = ch * w
        qimg = QImage(
            rgb_img.data,
            w,
            h,
            bpl,
            QImage.Format.Format_RGB888).copy()
        self.editor.set_image(qimg)
        self.editor.mask_updated.emit()


class SeamlessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Make Seamless (Auto-Tile)")
        self.resize(300, 150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Edge Overlap (%)"))
        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setRange(5, 50)
        self.sl.setValue(15)
        layout.addWidget(self.sl)

        layout.addWidget(
            QLabel("Higher overlap = smoother blend but smaller result."))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_overlap(self):
        return self.sl.value()
