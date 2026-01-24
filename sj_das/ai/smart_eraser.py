
import numpy as np
from rembg import remove
from PIL import Image
import io
from sj_das.utils.logger import logger

class SmartEraser:
    """
    World-Class Background Remover.
    Uses U2Net (via rembg) for one-click subject isolation.
    """
    
    def remove_background(self, image_data: np.ndarray) -> np.ndarray:
        """
        Remove background from numpy image.
        Returns RGBA numpy array.
        """
        try:
            # Convert to PIL/Bytes for rembg
            is_bgr = True
            if len(image_data.shape) == 3 and image_data.shape[2] == 3:
                # Assuming BGR from OpenCV
                img_pil = Image.fromarray(image_data[..., ::-1]) # BGR to RGB
            else:
                img_pil = Image.fromarray(image_data)
                is_bgr = False
            
            # Execute U2Net
            logger.info("Running Smart Background Removal...")
            output_pil = remove(img_pil)
            
            # Convert back to Numpy
            output_arr = np.array(output_pil)
            
            # Fix channels if needed (Output is RGBA)
            if is_bgr:
                # Convert RGBA to BGRA
                r, g, b, a = output_arr[:,:,0], output_arr[:,:,1], output_arr[:,:,2], output_arr[:,:,3]
                output_arr = np.dstack([b, g, r, a])
                
            return output_arr
            
        except Exception as e:
            logger.error(f"Background Removal Failed: {e}")
            return image_data

_eraser = None
def get_smart_eraser():
    global _eraser
    if _eraser is None:
        _eraser = SmartEraser()
    return _eraser
