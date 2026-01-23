import os

import cv2
import numpy as np
import onnxruntime as ort

from sj_das.utils.logger import logger


class BackgroundRemovalEngine:
    """
    Removes background using U2Net (ONNX).
    """

    def __init__(self):
        self.model_path = os.path.join(
            os.getcwd(),
            'sj_das',
            'assets',
            'models',
            'segmentation',
            'u2net.onnx')
        self.session = None

    def load_model(self):
        if self.session is not None:
            return True

        if not os.path.exists(self.model_path):
            logger.error(f"U2Net model not found at {self.model_path}")
            return False

        try:
            # Use CPU by default for broader compatibility, or CUDA if
            # available
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.session = ort.InferenceSession(
                self.model_path, providers=providers)
            logger.info("U2Net (ONNX) Loaded Successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load U2Net: {e}")
            return False

    def remove_background(self, image: np.ndarray) -> np.ndarray:
        if not self.load_model():
            return image

        try:
            # Preprocess
            h, w = image.shape[:2]
            # U2Net standard input is 320x320
            img_resized = cv2.resize(image, (320, 320))

            # Normalize
            img_resized = img_resized.astype(np.float32)
            img_resized /= 255.0

            # Normalize (ImageNet mean/std - common for U2Net)
            tmp_img = np.zeros((320, 320, 3), dtype=np.float32)
            tmp_img[:, :, 0] = (img_resized[:, :, 0] - 0.485) / 0.229
            tmp_img[:, :, 1] = (img_resized[:, :, 1] - 0.456) / 0.224
            tmp_img[:, :, 2] = (img_resized[:, :, 2] - 0.406) / 0.225

            # HWC to CHW
            tmp_img = tmp_img.transpose((2, 0, 1))
            tmp_img = np.expand_dims(tmp_img, 0)

            # Inference
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name

            result = self.session.run([output_name], {input_name: tmp_img})

            # Postprocess mask
            pred = result[0][:, 0, :, :]

            # Normalize to 0-1
            ma = np.max(pred)
            mi = np.min(pred)
            pred = (pred - mi) / (ma - mi)

            pred = np.squeeze(pred)
            mask = cv2.resize(pred, (w, h), interpolation=cv2.INTER_LINEAR)

            # Apply Mask
            mask = (mask * 255).astype(np.uint8)

            # Create RGBA
            if image.shape[2] == 3:
                b, g, r = cv2.split(image)
                rgba = cv2.merge([b, g, r, mask])
            else:
                b, g, r, a = cv2.split(image)
                # Combine existing alpha with new mask?
                # For now just replace
                rgba = cv2.merge([b, g, r, mask])

            return rgba

        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            return image
