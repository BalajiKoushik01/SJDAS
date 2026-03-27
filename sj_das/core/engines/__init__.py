# AI Engines Module
"""
Centralized AI engines with modular organization.
"""

# LLM Engines
try:
    from .llm import Agent, AgentEngine, Crew, LocalLLMEngine, Task
except Exception:
    pass

# Vision Engines
try:
    from .vision import AdvancedVisionEngine, CLIPEngine, MiDaSDepth, SAMEngine
except Exception:
    pass

# Enhancement Engines
try:
    from .enhancement import (AIUpscaler, ControlNetEngine, RealESRGANUpscaler,
                              StyleTransferEngine)
except Exception:
    pass

# Segmentation Engines
try:
    from .segmentation import ColorQuantizerEngine, MagicEraserEngine
except Exception:
    pass

# Orchestrator
try:
    from ..ai_orchestrator import AIOrchestrator
except Exception:
    pass
