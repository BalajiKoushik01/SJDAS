import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QColorDialog, QInputDialog

from sj_das.utils.logger import logger


class DesignerViewPSPMethods:
    """
    Mixin class implementing PaintShop Pro / Photoshop equivalent features.
    Merged into PremiumDesignerView.
    """

    # ============================
    # 1. MAGIC WAND (Selection)
    # ============================
    def activate_magic_wand(self, *args):
        """Enable Magic Wand tool"""
        self.editor.set_tool('magic_wand')
        if hasattr(self, 'status_label'):
            self.status_label.setText(
                "Tool: Magic Wand - Click to select color areas")
        # Visual feedback: Custom cursor
        # self.setCursor(Qt.CursorShape.CrossCursor)

    def perform_magic_wand_selection(self, pos, tolerance=30):
        """
        Executes Flood Fill algorithm to generate a selection mask
        """
        if not self.current_image_path:
            return

        try:
            # Get current pixel color
            image = self.editor.get_image()  # QImage
            # Convert to CV2/Numpy
            ptr = image.bits()
            ptr.setsize(image.sizeInBytes())
            arr = np.array(ptr).reshape(image.height(), image.width(), 4)

            # Target seed point
            x, y = int(pos.x()), int(pos.y())
            if x < 0 or x >= image.width() or y < 0 or y >= image.height():
                return

            # Create mask
            h, w = image.height(), image.width()
            mask = np.zeros((h + 2, w + 2), np.uint8)

            # Flood Fill
            # Flags: Connectivity (4), Mask Value (255), Fixed Range
            flags = 4 | (
                255 << 8) | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE

            # Tolerance range
            lo_diff = (tolerance,) * 4
            up_diff = (tolerance,) * 4

            cv2.floodFill(arr, mask, (x, y), (0, 0, 0),
                          lo_diff, up_diff, flags)

            # Extract actual mask (remove +2 padding)
            final_mask = mask[1:-1, 1:-1]

            # Apply to Editor (Selection Layer)
            self.editor.set_selection(final_mask)
            self.status_label.setText(f"Magic Wand: Selected area at {x},{y}")

        except Exception as e:
            logger.error(f"Magic Wand error: {e}")

    def select_segment_by_name(self, target_name):
        """
        Selects a specific semantic region (Body, Border, Pallu) via Menu.
        """
        try:
            from sj_das.core.unified_ai_engine import get_engine
            engine = get_engine()

            image_q = self.editor.get_image()
            if image_q.isNull():
                return

            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            if hasattr(self, 'status_label'):
                self.status_label.setText(f"AI: Finding {target_name}...")

            masks = engine.predict_segmentation(img_bgr)

            if not masks:
                return

            target_key = target_name.lower()
            if target_key in masks:
                self.editor.set_selection(masks[target_key])
                if hasattr(self, 'status_label'):
                    self.status_label.setText(f"AI Selected: {target_name}")
                self.editor.mask_updated.emit()
            else:
                if hasattr(self, 'status_label'):
                    self.status_label.setText(
                        f"AI: Segment '{target_name}' not found.")

        except Exception as e:
            logger.error(f"Selection Error: {e}")

    def perform_smart_selection(self, pos):
        """
        AI-Powered Selection: Click to Segment using SAM (Async).
        """
        if not hasattr(self, 'ai_service'):
            return

        # Get Image
        image_q = self.editor.get_image()
        if image_q.isNull():
            return

        # Convert to Numpy (BGR) - Optimized
        ptr = image_q.bits()
        ptr.setsize(image_q.sizeInBytes())
        arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)

        # SAM Engine expects numpy array.
        # We pass the heavy array.
        # (In future, optimization: pass reference or hash if cached context)
        # But here we just pass it.

        x, y = int(pos.x()), int(pos.y())

        self.status_label.setText("AI: Segmenting...")
        # Call Async
        self.ai_service.segment_image(
            arr, point_coords=[[x, y]], point_labels=[1])
        # Result will be handled in _on_ai_generation_complete

    # ============================
    # 2. TEXT TOOL
    # ============================
    def activate_text_tool(self, *args):
        """Enable Text Tool"""
        text, ok = QInputDialog.getText(self, "Add Text", "Enter Text:")
        if ok and text:
            # In V1 this would just bake pixels. V2 adds a layer.
            # For this quick implementation, we bake it with "Move" capability
            # preview
            self.editor.add_text_layer(text)
            self.status_label.setText("Text added. Click to place.")

    # ============================
    # 3. CLONE STAMP
    # ============================
    def activate_clone_stamp(self, *args):
        """Enable Clone Stamp Tool"""
        self.editor.set_tool('clone')
        if hasattr(self, 'status_label'):
            self.status_label.setText(
                "Tool: Clone Stamp - Shift+Click to define source")

    # ============================
    # 4. IMAGE ADJUSTMENTS
    # ============================
    def apply_brightness_contrast(self, *args):
        """Adjust Brightness and Contrast"""
        # Simple Dialog (In real app, custom widget)
        # We'll use input dialog for demo
        val, ok = QInputDialog.getInt(
            self, "Brightness", "Value (-100 to 100):", 0, -100, 100)
        if ok:
            self._apply_cv2_op(self._op_brightness, val)

    def _op_brightness(self, img, val):
        """CV2 Brightness/Contrast implementation"""
        # alpha = contrast (1.0-3.0), beta = brightness (0-100)
        # Simplified: just brightness
        return cv2.convertScaleAbs(img, alpha=1.0, beta=val)

    def apply_invert(self, *args):
        """Invert Colors"""
        self._apply_cv2_op(lambda img, _: cv2.bitwise_not(img), None)

    def apply_blur(self, *args):
        """Gaussian Blur"""
        val, ok = QInputDialog.getInt(
            self, "Gaussian Blur", "Radius (odd):", 3, 1, 21, 2)
        if ok:
            self._apply_cv2_op(
                lambda img, v: cv2.GaussianBlur(
                    img, (v, v), 0), val)

    def apply_sharpen(self, *args):
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        self._apply_cv2_op(lambda img, _: cv2.filter2D(img, -1, kernel), None)

    def apply_find_edges(self, *args):
        self._apply_cv2_op(lambda img, _: cv2.Canny(img, 100, 200), None)

    # ============================
    # 5. TRANSFORMS
    # ============================
    def apply_rotate_90(self, *args):
        self._apply_cv2_op(
            lambda img, _: cv2.rotate(
                img, cv2.ROTATE_90_CLOCKWISE), None)

    def apply_flip_h(self, *args):
        self._apply_cv2_op(lambda img, _: cv2.flip(img, 1), None)

    # ============================
    # 6. TEXTILE PRO TOOLS
    # ============================
    def apply_quantization(self, *args):
        """Reduce colors (K-Means)"""
        k, ok = QInputDialog.getInt(
            self, "Reduce Colors", "Number of Yarns (k):", 8, 2, 256)
        if ok:
            self._apply_cv2_op(self._op_quantize, k)

    def _op_quantize(self, img, k):
        """K-Means Quantization"""
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, label, center = cv2.kmeans(
            data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        res = center[label.flatten()]
        return res.reshape(img.shape)

    def apply_replace_color(self, *args):
        """Smart Color Replacement"""
        # 1. Pick Source Color
        color_src = QColorDialog.getColor(title="Select Color to Replace")
        if not color_src.isValid():
            return

        # 2. Pick Target Color
        color_dst = QColorDialog.getColor(title="Select New Color")
        if not color_dst.isValid():
            return

        # 3. Apply
        self._apply_cv2_op(self._op_replace_color, color_src, color_dst)

    def _op_replace_color(self, img, src, dst):
        """Replace color range"""
        # Convert QColor to BGR/RGB tuple
        # img is RGB because _apply_cv2_op converts it
        s = np.array([src.red(), src.green(), src.blue()])
        d = np.array([dst.red(), dst.green(), dst.blue()])

        # Create mask (exact match or small tolerance)
        tolerance = 30
        lower = np.clip(s - tolerance, 0, 255)
        upper = np.clip(s + tolerance, 0, 255)

        mask = cv2.inRange(img, lower, upper)
        img[mask > 0] = d
        return img

    def show_seamless_preview(self, *args):
        """Generate 3x3 Tiled Preview"""
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtWidgets import QDialog, QLabel, QScrollArea, QVBoxLayout

        if not hasattr(self, 'editor'):
            return
        img = self.editor.get_image()  # QImage
        w, h = img.width(), img.height()

        # Create big canvas (3x3)
        big_img = QImage(w * 3, h * 3, img.format())
        painter = QPainter(big_img)

        # Tile
        for x in range(3):
            for y in range(3):
                painter.drawImage(x * w, y * h, img)
        painter.end()

        # Show Dialog
        d = QDialog(self)
        d.setWindowTitle(f"Seamless Mode Preview ({w*3}x{h*3})")
        d.resize(800, 600)
        lay = QVBoxLayout(d)

        scroll = QScrollArea()
        lbl = QLabel()
        lbl.setPixmap(QPixmap.fromImage(big_img))
        scroll.setWidget(lbl)
        lay.addWidget(scroll)

        d.exec()

    def activate_magic_eraser(self):
        """Remove Background (Simple Hue Heuristic)"""
        # Assumption: Background is the most common color
        self._apply_cv2_op(self._op_remove_bg)

    def _op_remove_bg(self, img, *args):
        # Naive implementation: Find dominant color and make transparency mask
        # But _apply_cv2_op handles RGB. Transparency requires Alpha.
        # This is complex in current pipeline.
        # Let's do a 'White to Black' conversion for now as a placeholder for 'Removal'
        # Or better: aggressive grabcut? Too slow.
        return img  # Semantic Placeholder

    def apply_content_aware_fill(self, *args):
        """
        AI Inpainting: Fills the selected area with generated texture.
        """
        sel = self.editor.get_selection()
        if sel is None:
            self.status_label.setText("Select an area first!")
            return

        # 1. Get Prompt Suggestion (Context Aware)
        # In a full flow, we might ask AI "What fits here?"
        # For now, ask User or use current classification
        text, ok = QInputDialog.getText(
            self, "Content Aware Fill", "Describe fill (or leave empty for auto):")
        if not ok:
            return

        prompt = text if text else "saree texture pattern matching surrounding"

        self.status_label.setText(f"AI Inpainting: Generating '{prompt}'...")

        # 2. Call Generative Engine
        # We need access to GenerativeEngine instance.
        # It's usually in `self.generative` or similar in the main view.
        # If not, create one or grab singleton if available.
        try:
            # Assuming singleton access or lazy import like UnifiedEngine
            # But GenerativeDesignEngine isn't a singleton in original code?
            # Let's instantiate (it's lightweight wrapper) or fix architecture later.
            # Actually, let's use UnifiedAIEngine if it had inpainting, but it generates whole images.
            # GenerativeDesignEngine has `inpaint_design`.

            from sj_das.core.generative_engine import GenerativeDesignEngine
            gen_engine = GenerativeDesignEngine()
            # Configure if needed

            image_q = self.editor.get_image()
            ptr = image_q.bits()
            ptr.setsize(image_q.sizeInBytes())
            arr = np.array(ptr).reshape(image_q.height(), image_q.width(), 4)
            img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            # Run Inpaint
            result_bgr = gen_engine.inpaint_design(img_bgr, sel, prompt)

            # Convert back
            h, w, c = result_bgr.shape
            final = QImage(result_bgr.data, w, h, 3 *
                           w, QImage.Format.Format_RGB888).rgbSwapped()

            self.editor.commit_image_change(final, "Content Aware Fill")
            self.status_label.setText("Inpainting Complete")

        except Exception as e:
            logger.error(f"Inpainting Failed: {e}")
            self.status_label.setText("Inpainting Failed")
    # CORE: CV2 BRIDGE
    # ============================

    def _apply_cv2_op(self, func, *args):
        """Applies a CV2 function to the editor image"""
        if not hasattr(self, 'editor'):
            return

        # 1. Get QImage
        qimg = self.editor.get_image()
        if qimg.isNull():
            return

        # 2. Convert to Numpy
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        arr = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)

        # 3. Process (Drop Alpha for processing usually, or keep it)
        # Most CV2 ops work on BGR. QImage is RGBA or ARGB.
        # Let's convert to RGB for safety.
        rgb = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

        # 4. Apply Op
        try:
            res = func(rgb, *args)

            # Check result shape (grayscale vs color)
            if len(res.shape) == 2:
                res = cv2.cvtColor(res, cv2.COLOR_GRAY2RGB)

            # 5. Convert back to QImage
            h, w, ch = res.shape
            bytes_per_line = ch * w
            # Make a copy to decouple from numpy
            final_qimg = QImage(
                res.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888).copy()

            # 6. Set back to editor
            self.editor.commit_image_change(final_qimg, "Apply Filter")
            self.status_label.setText("Effect Applied")

        except Exception as e:
            logger.error(f"CV2 Op Error: {e}")
            self.status_label.setText("Effect Failed")
