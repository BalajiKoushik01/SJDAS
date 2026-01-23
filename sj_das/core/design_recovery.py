from typing import Any, Callable, Dict, Optional, Tuple

import cv2
import numpy as np

from sj_das.utils.decorators import handle_errors, validate_input
from sj_das.utils.enhanced_logger import get_logger, log_performance
from sj_das.utils.exceptions import ImageProcessingException, InvalidImageError

logger = get_logger(__name__)


class DesignRecoveryEngine:
    """
    Intelligent Design Recovery System with Enhanced Error Handling.
    Transforms low-quality screenshots into clean, usable designs.
    """

    def __init__(self):
        """Initialize design recovery engine."""
        self.orchestrator = None
        logger.info("DesignRecoveryEngine initialized")

    def _get_orchestrator(self):
        """Lazy load orchestrator."""
        if self.orchestrator is None:
            from sj_das.core.ai_orchestrator import AIOrchestrator
            self.orchestrator = AIOrchestrator()
        return self.orchestrator

    @log_performance(logger)
    @validate_input(screenshot=lambda x: x is not None and isinstance(x, np.ndarray))
    def recover(self, screenshot: np.ndarray,
                auto_reconstruct: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Main recovery pipeline.

        Args:
            screenshot: Input image (BGR)
            auto_reconstruct: If True, uses Flux to regenerate if quality too low

        Returns:
            (recovered_image, metadata)
        """
        logger.info("Starting design recovery pipeline")
        metadata = {}

        try:
            # Step 1: Understand
            logger.debug("Step 1/7: Understanding design")
            description = self._understand(screenshot)
            metadata["description"] = description

            # Step 2: Segment
            logger.debug("Step 2/7: Segmenting pattern")
            segmented = self._segment(screenshot)

            # Step 3: Perspective correction
            logger.debug("Step 3/7: Correcting perspective")
            corrected = self._correct_perspective(segmented)

            # Step 4: Enhance
            logger.debug("Step 4/7: Enhancing quality")
            enhanced = self._enhance(corrected)

            # Step 5: Quality check
            logger.debug("Step 5/7: Assessing quality")
            quality = self._assess_quality(enhanced)
            metadata["quality_score"] = quality

            # Step 6: Reconstruct if needed
            if auto_reconstruct and quality < 0.6:
                logger.debug(
                    f"Step 6/7: Quality low ({quality:.2f}), reconstructing")
                reconstructed = self._reconstruct(enhanced, description)
            else:
                logger.debug(f"Step 6/7: Quality acceptable ({quality:.2f})")
                reconstructed = enhanced

            # Step 7: Quantize
            logger.debug("Step 7/7: Quantizing for loom")
            final = self._quantize(reconstructed)

            metadata["pipeline_complete"] = True
            logger.info("Design recovery complete", context=metadata)

            return final, metadata

        except Exception as e:
            logger.error(
                "Design recovery failed",
                context={
                    "error": str(e)},
                exc_info=True)
            raise ImageProcessingException(f"Recovery failed: {e}")

    @log_performance(logger)
    @validate_input(image_path=lambda x: isinstance(x, str) and len(x) > 0)
    def recover_design(self, image_path: str,
                       progress_callback: Optional[Callable] = None) -> np.ndarray:
        """
        Main recovery method - converts screenshot file to clean design.

        Args:
            image_path: Path to screenshot image file
            progress_callback: Optional callback(step, total, message)

        Returns:
            Recovered design as numpy array
        """
        try:
            logger.info(f"Starting design recovery from: {image_path}")

            screenshot = cv2.imread(image_path)
            if screenshot is None:
                raise InvalidImageError(
                    f"Could not load image", context={
                        "path": image_path})

            recovered, metadata = self.recover(
                screenshot, auto_reconstruct=True)

            if progress_callback:
                progress_callback(7, 7, "Recovery complete!")

            return recovered

        except Exception as e:
            logger.error(
                "Design recovery failed",
                context={
                    "path": image_path},
                exc_info=True)
            raise

    @handle_errors(default_return="textile pattern")
    def _understand(self, image: np.ndarray) -> str:
        """Uses CLIP to understand the design."""
        orch = self._get_orchestrator()
        return orch.process("understand", image, {"type": "describe"})

    @handle_errors(default_return=None)
    def _segment(self, image: np.ndarray) -> np.ndarray:
        """Removes background using Magic Eraser."""
        from sj_das.core.magic_eraser import MagicEraserEngine
        eraser = MagicEraserEngine()
        return eraser.remove_background(
            image, refine=True, smoothness=2) or image

    @handle_errors(default_return=None)
    def _correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """Auto-corrects perspective distortion."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return image

        largest = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)

        if len(approx) == 4:
            pts = approx.reshape(4, 2).astype(np.float32)
            rect = self._order_points(pts)

            (tl, tr, br, bl) = rect
            widthA = np.linalg.norm(br - bl)
            widthB = np.linalg.norm(tr - tl)
            maxWidth = max(int(widthA), int(widthB))

            heightA = np.linalg.norm(tr - br)
            heightB = np.linalg.norm(tl - bl)
            maxHeight = max(int(heightA), int(heightB))

            dst = np.array([[0, 0], [maxWidth - 1, 0],
                           [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype=np.float32)

            M = cv2.getPerspectiveTransform(rect, dst)
            return cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return image

    def _order_points(self, pts):
        """Orders points in TL, TR, BR, BL order."""
        rect = np.zeros((4, 2), dtype=np.float32)
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    @handle_errors(default_return=None)
    def _enhance(self, image: np.ndarray) -> np.ndarray:
        """Enhances quality using Real-ESRGAN."""
        orch = self._get_orchestrator()
        return orch.process("upscale", image, {
                            "quality": "high", "scale": 4}) or image

    @handle_errors(default_return=0.5)
    def _assess_quality(self, image: np.ndarray) -> float:
        """Assesses image quality using Laplacian variance."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return min(laplacian_var / 500.0, 1.0)

    @handle_errors(default_return=None)
    def _reconstruct(self, image: np.ndarray, description: str) -> np.ndarray:
        """Reconstructs design using Flux.1."""
        from sj_das.ai.flux_generator import FluxGenerator
        flux = FluxGenerator()
        h, w = image.shape[:2]
        prompt = f"high quality {description}, clean textile design, intricate details"
        return flux.generate(prompt, width=w, height=h) or image

    @handle_errors(default_return=None)
    def _quantize(self, image: np.ndarray) -> np.ndarray:
        """Quantizes to 8 colors for loom."""
        from sj_das.core.quantizer import ColorQuantizerEngine
        quantizer = ColorQuantizerEngine()
        return quantizer.quantize(image, k=8, dither=False) or image
