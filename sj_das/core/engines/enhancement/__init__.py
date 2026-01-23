# Enhancement Engines Module
"""
Image enhancement and transformation engines.
"""

try:
    from .upscaler import AIUpscaler
except ImportError:
    AIUpscaler = None

try:
    from .real_esrgan_upscaler import RealESRGANUpscaler
except ImportError:
    RealESRGANUpscaler = None

try:
    from .style_transfer import StyleTransferEngine
except ImportError:
    StyleTransferEngine = None

try:
    from .controlnet_engine import ControlNetEngine
except ImportError:
    ControlNetEngine = None

__all__ = [
    'AIUpscaler',
    'RealESRGANUpscaler',
    'StyleTransferEngine',
    'ControlNetEngine']
