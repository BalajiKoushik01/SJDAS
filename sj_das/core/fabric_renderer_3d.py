import cv2
import numpy as np

from sj_das.utils.logger import logger


class FabricRenderer3D:
    """
    Hyper-Real Fabric Simulator.
    Uses 2.5D Normal Mapped rendering to simulate 3D thread interlacing.
    """

    def render(self, loom_graph: np.ndarray, color_image: np.ndarray,
               scale: int = 4) -> np.ndarray:
        """
        Renders the loom graph as realistic fabric.

        Args:
            loom_graph: Binary map (0=Weft, 255=Warp).
            color_image: Original Color design (BGR).
            scale: Zoom level (pixels per thread).

        Returns:
            Rendered image (BGR).
        """
        h, w = loom_graph.shape

        # Resize inputs to render resolution
        render_w = w * scale
        render_h = h * scale

        # 1. Create Base Colors
        # Nearest neighbor resize to keep crisp edges
        colors = cv2.resize(color_image, (render_w, render_h),
                            interpolation=cv2.INTER_NEAREST)

        # 2. Generate Thread Normal Map
        # We need a cylinder shape for each thread.
        # Warp (Vertical) vs Weft (Horizontal).

        # Create a single thread tile (Cylinder gradient)
        # Vertical (Warp)
        grad_x = np.linspace(-1, 1, scale)
        grad_x = np.tile(grad_x, (scale, 1))  # shape (scale, scale)
        # Z = sqrt(1 - x^2)
        # This gives a round profile

        # This is getting complex for pure numpy fast.
        # Simplified Trick: Use pre-baked textures or simple shading mask.

        # Simple Thread Shading Mask
        # Vertical Gradient (for Weft)
        # V-shape: 1, 0, 1. Darker in middle? No, brighter in middle.
        g_weft = np.abs(np.linspace(-1, 1, scale))
        g_weft = 1.0 - (g_weft**2)  # Parabola: 0->1->0
        # Horizontal bar has gradient along Y axis
        tile_weft = np.tile(g_weft.reshape(scale, 1), (1, scale))

        # Horizontal Gradient (for Warp) - threads run vertical, so gradient is
        # along X axis
        g_warp = np.abs(np.linspace(-1, 1, scale))
        g_warp = 1.0 - (g_warp**2)
        tile_warp = np.tile(g_warp.reshape(1, scale), (scale, 1))

        # 3. Construct Full Shading Map
        # Upscale loom graph
        graph_up = cv2.resize(
            loom_graph, (render_w, render_h), interpolation=cv2.INTER_NEAREST)

        # Normalize graph to 0..1
        mask_warp = (graph_up > 127).astype(np.float32)  # 1 where Warp
        mask_weft = 1.0 - mask_warp

        # Tiling the shading textures
        # This is the slow part if done purely pixel-wise.
        # Instead, we just multiply by a global tiled texture?
        # A global grid of 'warp shading' and 'weft shading'

        # Can indicate slight mismatch if dimensions odd.
        full_warp_shade = np.tile(tile_warp, (h, w))
        # Ensure exact fit
        full_warp_shade = full_warp_shade[:render_h, :render_w]

        full_weft_shade = np.tile(tile_weft, (h, w))
        full_weft_shade = full_weft_shade[:render_h, :render_w]

        # Combine
        # Final Shade = (WarpMask * WarpShade) + (WeftMask * WeftShade)
        shading = (mask_warp * full_warp_shade) + (mask_weft * full_weft_shade)

        # 4. Apply Lighting
        # Colors * Shading
        # Bump up ambient light so it's not pitch black at edges
        lighting = 0.5 + (0.5 * shading)

        # Apply to 3 channels
        final = colors.astype(np.float32)
        final[:, :, 0] *= lighting
        final[:, :, 1] *= lighting
        final[:, :, 2] *= lighting

        # 5. Add Shadows (Ambient Occlusion) at crossing points?
        # Maybe too slow. Phong highlighting?
        # Add specular highlight
        specular = np.clip((shading - 0.7) * 3, 0, 1) * 40  # Simple shine
        final += np.dstack([specular] * 3)

        return np.clip(final, 0, 255).astype(np.uint8)
