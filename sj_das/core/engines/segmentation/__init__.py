# Segmentation Engines Module
"""
Image segmentation and color quantization engines.
"""

try:
    from .magic_eraser import MagicEraserEngine
except ImportError:
    MagicEraserEngine = None

try:
    from .quantizer import ColorQuantizerEngine
except ImportError:
    ColorQuantizerEngine = None

__all__ = ['MagicEraserEngine', 'ColorQuantizerEngine']
