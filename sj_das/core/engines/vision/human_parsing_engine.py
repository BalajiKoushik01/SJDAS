import os

import cv2
import numpy as np
import onnxruntime as ort

from sj_das.utils.logger import logger


class HumanParsingEngine:
    """
    Human Parsing / Segmentation using U2Net-Human-Seg (ONNX).
    Used for virtual draping and sizing checks.
    """

    def __init__(self):
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'segmentation',
            'u2net_human_seg.onnx')
        self.session = None

    def load_model(self):
        if self.session is not None:
            return True

        if not os.path.exists(self.model_path):
            logger.error(f"Human Parsing model missing: {self.model_path}")
            return False

        try:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.session = ort.InferenceSession(
                self.model_path, providers=providers)
            logger.info("Human Parsing Model Loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load Human Parsing: {e}")
            return False

    def segment_human(self, image: np.ndarray) -> np.ndarray:
        """Returns the human segment (RGBA)."""
        if not self.load_model():
            return image

        try:
            h, w = image.shape[:2]
            img_resized = cv2.resize(
                image, (320, 320)).astype(
                np.float32) / 255.0

            # Normalize
            tmp_img = np.zeros((320, 320, 3), dtype=np.float32)
            tmp_img[:, :, 0] = (img_resized[:, :, 0] - 0.485) / 0.229
            tmp_img[:, :, 1] = (img_resized[:, :, 1] - 0.456) / 0.224
            tmp_img[:, :, 2] = (img_resized[:, :, 2] - 0.406) / 0.225

            tmp_img = tmp_img.transpose((2, 0, 1))
            tmp_img = np.expand_dims(tmp_img, 0)

            # Inference
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name

            result = self.session.run([output_name], {input_name: tmp_img})
            pred = result[0][:, 0, :, :]

            # Postprocess
            ma, mi = np.max(pred), np.min(pred)
            pred = (pred - mi) / (ma - mi)

            mask = cv2.resize(pred.squeeze(), (w, h))
            mask = (mask * 255).astype(np.uint8)

            # RGBA
            if image.shape[2] == 3:
                b, g, r = cv2.split(image)
                rgba = cv2.merge([b, g, r, mask])
            else:
                # If already alpha, replace/multiply
                b, g, r, a = cv2.split(image)
                rgba = cv2.merge([b, g, r, mask])

            return rgba

        except Exception as e:
            logger.error(f"Human parsing failed: {e}")
            return image
