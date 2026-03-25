import numpy as np
from PIL import Image

def export_to_indexed_bmp(master_matrix, stock_colors, output_filename="saree_production_file.bmp"):
    """
    Converts a 2D NumPy array (from the Kali engine) into a strict 8-bit Indexed BMP.
    This ensures the file is instantly readable by modern Stäubli or Bonas software.
    
    Args:
        master_matrix (np.array): The 2D array containing thread indexes (e.g., 0, 1, 2).
        stock_colors (list of tuples): The RGB values of the physical threads from the Stock API.
                                       Format: [(R, G, B), (R, G, B), ...]
        output_filename (str): The desired output file path.
    """
    
    # 1. Validate the matrix (Ensure it only contains uint8 data to prevent overflow)
    clean_matrix = master_matrix.astype(np.uint8)
    
    # 2. Convert the NumPy array directly into a Pillow Image object
    # 'P' stands for Palette (Indexed Color mode), which forces the 8-bit constraint
    loom_image = Image.fromarray(clean_matrix, mode='P')
    
    # 3. Construct the strict Machine Palette Header
    # Pillow expects a flattened list of RGB values: [R1, G1, B1, R2, G2, B2...]
    flat_palette = []
    for color in stock_colors:
        flat_palette.extend(color)
        
    # Jacquard BMP palettes require exactly 256 color slots (768 integers).
    # We must pad the rest of the unused palette with zeros (black) to prevent header corruption.
    padding_needed = 768 - len(flat_palette)
    flat_palette.extend([0] * padding_needed)
    
    # 4. Inject the palette into the image header
    loom_image.putpalette(flat_palette)
    
    # 5. Export as a native BMP file
    # We disable compression because many loom interfaces cannot decompress BMPs.
    loom_image.save(output_filename, format="BMP", compress_level=0)
    
    return output_filename
