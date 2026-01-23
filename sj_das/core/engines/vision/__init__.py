# Vision Engines Module
"""
Computer vision engines for understanding and analysis.
"""

try:
    from .clip_engine import CLIPEngine
except ImportError:
    CLIPEngine = None

try:
    from .sam_engine import SAMEngine
except ImportError:
    SAMEngine = None

try:
    from .midas_depth import MiDaSDepth
except ImportError:
    MiDaSDepth = None

try:
    from .advanced_vision import AdvancedVisionEngine
except ImportError:
    AdvancedVisionEngine = None

__all__ = ['CLIPEngine', 'SAMEngine', 'MiDaSDepth', 'AdvancedVisionEngine']
