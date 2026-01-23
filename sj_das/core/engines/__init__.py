# AI Engines Module
"""
Centralized AI engines with modular organization.
"""

# LLM Engines
try:
    from .llm import Agent, AgentEngine, Crew, LocalLLMEngine, Task
except ImportError:
    pass

# Vision Engines
try:
    from .vision import AdvancedVisionEngine, CLIPEngine, MiDaSDepth, SAMEngine
except ImportError:
    pass

# Enhancement Engines
try:
    from .enhancement import (AIUpscaler, ControlNetEngine, RealESRGANUpscaler,
                              StyleTransferEngine)
except ImportError:
    pass

# Segmentation Engines
try:
    from .segmentation import ColorQuantizerEngine, MagicEraserEngine
except ImportError:
    pass

# Orchestrator
try:
    from ..ai_orchestrator import AIOrchestrator
except ImportError:
    pass
