import numpy as np
import cv2

def generate_tapered_kali(base_pattern, top_hooks, bottom_hooks, picks_height):
    """
    Warps a rectangular design into a mathematically perfect trapezoidal Kali panel.
    CRITICAL: Uses INTER_NEAREST to prevent the creation of un-weaveable "blended" colors.
    """
    kali_canvas = np.zeros((picks_height, bottom_hooks), dtype=np.uint8)
    row_widths = np.linspace(top_hooks, bottom_hooks, picks_height, dtype=int)

    pattern_stretched = cv2.resize(
        base_pattern, 
        (bottom_hooks, picks_height), 
        interpolation=cv2.INTER_NEAREST
    )

    for y in range(picks_height):
        current_width = row_widths[y]
        row = pattern_stretched[y, :]
        row_2d = row.reshape(1, -1)
        
        squeezed_row = cv2.resize(
            row_2d, 
            (current_width, 1), 
            interpolation=cv2.INTER_NEAREST
        ).flatten()

        start_x = (bottom_hooks - current_width) // 2
        kali_canvas[y, start_x : start_x + current_width] = squeezed_row

    return kali_canvas

def stitch_master_file(kali_panel, number_of_kalis):
    """
    Stitches the generated Kali panels into a single, continuous Master Loom File.
    """
    master_saree_file = np.hstack([kali_panel] * number_of_kalis)
    return master_saree_file
