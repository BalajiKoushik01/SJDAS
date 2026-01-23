import cv2
import numpy as np

from sj_das.utils.logger import logger


class FabricRealityEngine:
    """
    Competitive Feature: 2.5D Fabric Simulation (ArahWeave Competitor).
    Renders a flat 2D textile design into a realistic, lit fabric surface.
    """

    def __init__(self):
        self.textures = {}

    def render_simulation(self, image_bgr: np.ndarray,
                          weave_type='satin', zoom=1.0) -> np.ndarray:
        """
        Render 2.5D simulation of the fabric.

        Args:
            image_bgr: Source design (OpenCV BGR)
            weave_type: Texture style ('satin', 'twill', 'plain')
            zoom: Simulation zoom level (affects thread visibility)

        Returns:
            Rendered high-res fabric image (BGR)
        """
        try:
            h, w = image_bgr.shape[:2]

            # 1. Upscale for Thread Definition (Simulate individual yarns)
            scale = 2  # 2x internal resolution for detail
            sim_w, sim_h = int(w * scale), int(h * scale)

            # Resize source pattern (Nearest Neighbor to keep sharp pixels)
            base_color = cv2.resize(
                image_bgr, (sim_w, sim_h), interpolation=cv2.INTER_NEAREST)

            # 2. Generate Normal Map (Bump Map) based on Weave
            # This creates the illusion of depth (yarns going up/down)
            normal_map = self._generate_weave_normals(sim_w, sim_h, weave_type)

            # 3. Apply Lighting (Blinn-Phong Shading)
            lit_fabric = self._apply_lighting(base_color, normal_map)

            # 4. Add Yarn Texture (Micro-noise)
            final_fabric = self._add_fiber_noise(lit_fabric)

            return final_fabric

        except Exception as e:
            logger.error(f"Fabric Simulation Failed: {e}")
            return image_bgr  # Fallback to original

    def _generate_weave_normals(self, w, h, weave_type):
        """Generates a normal map representing the thread structure."""
        # Create a tiling normal map pattern
        # Values: B=Z(Depth), G=Y, R=X

        # Simple procedural patterns for now
        # Ideally these are loaded from 'textures/' folder

        tile_size = 8
        tile = np.zeros((tile_size, tile_size, 3), dtype=np.float32)
        tile[:, :] = [0.5, 0.5, 1.0]  # Flat normal

        if weave_type == 'satin':
            # Long floats (smooth) with distinct points
            # Simulate a 5-end satin
            for i in range(tile_size):
                tile[i, :, 0] = np.sin(np.linspace(
                    0, np.pi, tile_size))  # Curvature X
                tile[:, i, 1] = np.cos(np.linspace(
                    0, np.pi, tile_size))  # Curvature Y

        elif weave_type == 'twill':
            # Diagonal ridges
            for i in range(tile_size):
                roll = np.roll(np.linspace(0, 1, tile_size), i)
                tile[i, :, 0] = roll

        else:  # Plain
            # Checkerboard normals
            tile[:4, :4] = [0.4, 0.4, 1.0]
            tile[4:, 4:] = [0.4, 0.4, 1.0]
            tile[:4, 4:] = [0.6, 0.6, 1.0]
            tile[4:, :4] = [0.6, 0.6, 1.0]

        # Normalize
        norm = np.linalg.norm(tile, axis=2, keepdims=True)
        tile = tile / (norm + 1e-5)

        # Tile it across the image
        # Using numpy tiling is faster than cv2
        tiles_x = (w // tile_size) + 1
        tiles_y = (h // tile_size) + 1

        full_map = np.tile(tile, (tiles_y, tiles_x, 1))
        return full_map[:h, :w]

    def _apply_lighting(self, color_map, normal_map):
        """Applies lighting model to the surface."""
        # Light Vector (Top Left, coming towards screen)
        # L = [0.5, -0.5, 1.0] normalized
        L = np.array([-0.5, -0.5, 0.8])
        L = L / np.linalg.norm(L)

        # Convert Colors to float
        diffuse_color = color_map.astype(np.float32) / 255.0

        # Normals are already normalized in _generate (mapped 0..1? No, vectors)
        # Need to remap normal_map from [0,1] or similar if it was image?
        # In _generate we made actual vectors.
        # But wait, tile was float.

        # Dot Product N . L for Diffuse
        # N is (h,w,3), L is (3,)
        intensity = np.sum(normal_map * L, axis=2)
        intensity = np.clip(intensity, 0, 1)
        intensity = intensity[:, :, np.newaxis]  # Expand for broadcasting

        # Ambient Light
        ambient = 0.4

        # Specular (Gloss for Silk)
        # View Vector V = [0,0,1]
        # H = (L+V)/2
        # For simplicity, just enhance bright spots (Glossy Saree)
        specular_intensity = np.power(intensity, 10)  # Shininess

        # Combine
        # Result = (Ambient + Diffuse) * Color + Specular * White
        lit_color = (ambient + intensity * 0.7) * \
            diffuse_color + (specular_intensity * 0.3)

        return np.clip(lit_color * 255, 0, 255).astype(np.uint8)

    def _add_fiber_noise(self, image):
        """Adds microscopic grain to look like fiber."""
        h, w, c = image.shape
        noise = np.random.normal(0, 5, (h, w)).astype(np.float32)  # scale 5
        noise = noise[:, :, np.newaxis]

        noisy_img = image.astype(np.float32) + noise
        return np.clip(noisy_img, 0, 255).astype(np.uint8)
