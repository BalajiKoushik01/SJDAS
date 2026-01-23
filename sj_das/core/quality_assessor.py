"""
Quality Assessment Tool
Evaluates generated designs for loom-readiness and pattern quality
"""
from pathlib import Path

import cv2
import numpy as np


class QualityAssessor:
    """Assess quality of generated textile patterns"""

    def __init__(self):
        self.criteria = {
            'graph_paper_style': 0.3,  # Pixel-perfect, no anti-aliasing
            'pattern_complexity': 0.2,  # Not too simple, not too noisy
            'color_consistency': 0.2,   # Limited palette
            'symmetry': 0.15,            # Repeating patterns
            'edge_sharpness': 0.15      # Crisp edges
        }

    def assess(self, image_path):
        """
        Assess image quality
        Returns: score (0-10) and breakdown
        """
        img = cv2.imread(str(image_path))
        if img is None:
            return 0, "Failed to load image"

        scores = {}

        # 1. Graph paper style (no anti-aliasing)
        scores['graph_paper'] = self._check_pixel_perfect(img)

        # 2. Pattern complexity
        scores['complexity'] = self._check_complexity(img)

        # 3. Color consistency
        scores['colors'] = self._check_color_limit(img)

        # 4. Symmetry
        scores['symmetry'] = self._check_symmetry(img)

        # 5. Edge sharpness
        scores['sharpness'] = self._check_edges(img)

        # Calculate weighted score
        total = sum(scores[k] * self.criteria[list(self.criteria.keys())[i]]
                    for i, k in enumerate(scores.keys()))

        return total * 10, scores

    def _check_pixel_perfect(self, img):
        """Check for pixel-perfect rendering (no anti-aliasing)"""
        # Convert to LAB color space for better edge detection
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        edges = cv2.Canny(lab[:, :, 0], 50, 150)

        # Count sharp transitions vs gradual
        sharp_pixels = np.sum(edges > 200)
        total_edge_pixels = np.sum(edges > 0)

        if total_edge_pixels == 0:
            return 0.5

        sharpness_ratio = sharp_pixels / total_edge_pixels
        return min(1.0, sharpness_ratio * 1.2)

    def _check_complexity(self, img):
        """Check pattern has good detail level"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Use variance as proxy for detail
        variance = np.var(gray)

        # Ideal range: 1000-5000
        if variance < 1000:
            return variance / 1000  # Too simple
        elif variance > 5000:
            return max(0, 1 - (variance - 5000) / 5000)  # Too noisy
        else:
            return 1.0  # Perfect

    def _check_color_limit(self, img):
        """Check uses limited color palette"""
        # Count unique colors
        pixels = img.reshape(-1, 3)
        unique_colors = np.unique(pixels, axis=0)
        num_colors = len(unique_colors)

        # Ideal: 4-16 colors
        if num_colors <= 16:
            return 1.0
        elif num_colors <= 32:
            return 0.8
        elif num_colors <= 64:
            return 0.5
        else:
            return max(0, 1 - (num_colors - 64) / 200)

    def _check_symmetry(self, img):
        """Check for repeating patterns"""
        h, w = img.shape[:2]

        # Check horizontal symmetry
        left = img[:, :w // 2]
        right = img[:, w // 2:]
        right_flipped = cv2.flip(right, 1)

        if left.shape == right_flipped.shape:
            diff = np.mean(
                np.abs(
                    left.astype(float) -
                    right_flipped.astype(float)))
            h_symmetry = max(0, 1 - diff / 128)
        else:
            h_symmetry = 0

        # Check vertical symmetry
        top = img[:h // 2, :]
        bottom = img[h // 2:, :]
        bottom_flipped = cv2.flip(bottom, 0)

        if top.shape == bottom_flipped.shape:
            diff = np.mean(
                np.abs(
                    top.astype(float) -
                    bottom_flipped.astype(float)))
            v_symmetry = max(0, 1 - diff / 128)
        else:
            v_symmetry = 0

        return max(h_symmetry, v_symmetry)

    def _check_edges(self, img):
        """Check edge sharpness"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = np.var(laplacian)

        # Normalize (empirically determined range)
        return min(1.0, sharpness / 500)


# Test
if __name__ == "__main__":
    assessor = QualityAssessor()

    print("Quality Assessment Tool")
    print("=" * 50)

    # Test available images
    test_images = [
        "test_ensemble_output.png",
        "production_test_ai.png",
        "production_test_patch.png"
    ]

    results = []
    for img_path in test_images:
        path = Path(img_path)
        if path.exists():
            score, breakdown = assessor.assess(path)
            results.append((img_path, score, breakdown))
            print(f"\n{img_path}:")
            print(f"  Overall Score: {score:.1f}/10")
            print(f"  Graph Paper: {breakdown['graph_paper']:.2f}")
            print(f"  Complexity: {breakdown['complexity']:.2f}")
            print(f"  Colors: {breakdown['colors']:.2f}")
            print(f"  Symmetry: {breakdown['symmetry']:.2f}")
            print(f"  Sharpness: {breakdown['sharpness']:.2f}")

    if results:
        # Find best
        best = max(results, key=lambda x: x[1])
        print(f"\n✓ Best Quality: {best[0]} ({best[1]:.1f}/10)")

    print("\n✅ Quality assessment complete!")
