import cv2
import numpy as np


class ColorEngine:
    def __init__(self):
        pass

    def reduce_colors(self, image_path, n_colors=8):
        """
        Reduces the image to n_colors using K-Means clustering.
        Returns the quantized image and the palette.
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not load image")

        # Convert to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize for K-Means (speed optimization)
        h, w = img.shape[:2]
        max_dim = 256  # Sufficient for color palette extraction
        scale = min(1.0, max_dim / max(h, w))
        small_img = cv2.resize(
            img, (0, 0), fx=scale, fy=scale) if scale < 1.0 else img

        pixels_small = small_img.reshape(-1, 3)
        pixel_data = np.float32(pixels_small)

        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixel_data, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Convert centers to uint8
        centers = np.uint8(centers)

        # Now apply to full image
        # We need to find the nearest center for each pixel in the original image
        # Using broadcasting can be memory intensive for large images, so we
        # process in chunks or use a simple loop if N is small

        full_pixels = img.reshape(-1, 3).astype(np.float32)

        # Efficient assignment for small N (n_colors is usually < 16)
        # Distance matrix: (NumPixels, N)
        # We can do this in chunks to save memory
        labels_full = np.zeros(full_pixels.shape[0], dtype=np.uint8)
        chunk_size = 10000

        centers_float = centers.astype(np.float32)

        for i in range(0, len(full_pixels), chunk_size):
            chunk = full_pixels[i:i + chunk_size]
            # Distances: ||a - b||^2 = ||a||^2 + ||b||^2 - 2<a, b>
            # But for small N, simple broadcasting is fine for chunk
            # chunk: (B, 3), centers: (N, 3) -> (B, 1, 3) - (1, N, 3) -> (B, N,
            # 3)
            dists = np.linalg.norm(
                chunk[:, None] - centers_float[None, :], axis=2)
            labels_full[i:i + chunk_size] = np.argmin(dists, axis=1)

        quantized_data = centers[labels_full]
        quantized_img = quantized_data.reshape(img.shape)

        # Convert back to BGR
        quantized_img_bgr = cv2.cvtColor(quantized_img, cv2.COLOR_RGB2BGR)

        return quantized_img_bgr, centers

    def get_dominant_colors(self, image_path, n_colors=5):
        """
        Returns the top n_colors from the image.
        """
        img, centers = self.reduce_colors(image_path, n_colors)
        return centers
