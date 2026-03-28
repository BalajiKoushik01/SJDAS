# Fix for basicsr/realesrgan on newer torchvision versions
try:
    import torchvision
    if not hasattr(torchvision.transforms, 'functional_tensor'):
        torchvision.transforms.functional_tensor = torchvision.transforms.functional
except ImportError:
    pass

try:
    from .clip_engine import CLIPEngine
except Exception:
    CLIPEngine = None

try:
    from .sam_engine import SAMEngine
except Exception:
    SAMEngine = None

try:
    from .midas_depth import MiDaSDepth
except Exception:
    MiDaSDepth = None

try:
    from .realesrgan_engine import RealESRGANEngine
except Exception:
    RealESRGANEngine = None

try:
    from .vtracer_engine import VTracerEngine
except Exception:
    VTracerEngine = None

__all__ = ['CLIPEngine', 'SAMEngine', 'MiDaSDepth', 'AdvancedVisionEngine', 'RealESRGANEngine', 'VTracerEngine']
