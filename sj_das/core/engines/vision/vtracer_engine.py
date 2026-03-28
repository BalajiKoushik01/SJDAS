import logging
import os

try:
    import vtracer
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

logger = logging.getLogger("SJ_DAS.VTracerEngine")

class VTracerEngine:
    """
    Wrapper for VTracer (Raster to SVG Vectorization).
    """
    def __init__(self):
        pass

    def vectorize(self, input_path: str, output_path: str, mode='spline', colormode='color'):
        """
        Converts raster image to SVG.
        """
        if not _AVAILABLE:
            logger.error("vtracer library not installed. pip install vtracer")
            return False
        
        try:
            vtracer.convert_image_to_svg_py(
                inp=input_path,
                out=output_path,
                colormode=colormode,
                hierarchical='stacked',
                mode=mode,
                filter_speckle=4,
                color_precision=6,
                corner_threshold=60,
                length_threshold=4.0
            )
            return True
        except Exception as e:
            logger.error(f"VTracer error: {e}")
            return False
