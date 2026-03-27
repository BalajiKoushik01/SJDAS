# Core utilities (optional imports)
try:
    from .design_utils import DesignUtils
except Exception:
    DesignUtils = None

try:
    from .palette_manager import PaletteManager
except Exception:
    PaletteManager = None

try:
    from .undo_system import UndoSystem
except Exception:
    UndoSystem = None

# Try new modular structure first, fallback to old
try:
    # Try importing from new modular structure
    from .engines.enhancement.controlnet_engine import ControlNetEngine
    from .engines.enhancement.real_esrgan_upscaler import RealESRGANUpscaler
    from .engines.enhancement.style_transfer import StyleTransferEngine
    from .engines.enhancement.upscaler import AIUpscaler
    from .engines.llm.agent_engine import AgentEngine
    from .engines.llm.crew_engine import Agent, Crew, LocalLLMEngine, Task
    from .engines.segmentation.magic_eraser import MagicEraserEngine
    from .engines.segmentation.quantizer import ColorQuantizerEngine
    from .engines.vision.advanced_vision import AdvancedVisionEngine
    from .engines.vision.clip_engine import CLIPEngine
    from .engines.vision.midas_depth import MiDaSDepth
    from .engines.vision.sam_engine import SAMEngine
except Exception:
    # Fallback to old structure
    try:
        from .agent_engine import AgentEngine
    except Exception:
        AgentEngine = None

    try:
        from .crew_engine import Agent, Crew, LocalLLMEngine, Task
    except Exception:
        Crew = Agent = Task = LocalLLMEngine = None

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
        from .advanced_vision import AdvancedVisionEngine
    except Exception:
        AdvancedVisionEngine = None

    try:
        from .upscaler import AIUpscaler
    except Exception:
        AIUpscaler = None

    try:
        from .real_esrgan_upscaler import RealESRGANUpscaler
    except Exception:
        RealESRGANUpscaler = None

    try:
        from .style_transfer import StyleTransferEngine
    except Exception:
        StyleTransferEngine = None

    try:
        from .controlnet_engine import ControlNetEngine
    except Exception:
        ControlNetEngine = None

    try:
        from .magic_eraser import MagicEraserEngine
    except Exception:
        MagicEraserEngine = None

    try:
        from .quantizer import ColorQuantizerEngine
    except Exception:
        ColorQuantizerEngine = None

# AI Orchestrator
try:
    from .ai_orchestrator import AIOrchestrator
except Exception:
    AIOrchestrator = None

# Manufacturing Engines
try:
    from .loom_engine import LoomEngine
except Exception:
    LoomEngine = None

try:
    from .fabric_renderer_3d import FabricRenderer3D
except Exception:
    FabricRenderer3D = None

try:
    from .costing import CostingEngine
except Exception:
    CostingEngine = None

# Voice
try:
    from .voice_engine import VoiceCommandEngine
except Exception:
    VoiceCommandEngine = None

# Recovery
try:
    from .design_recovery import DesignRecoveryEngine
except Exception:
    DesignRecoveryEngine = None

# Utilities
try:
    from .defect_scanner import DefectScannerEngine
except Exception:
    DefectScannerEngine = None

# Export all available modules
__all__ = [
    'DesignUtils', 'PaletteManager', 'UndoSystem',
    'AgentEngine', 'Crew', 'Agent', 'Task', 'LocalLLMEngine',
    'CLIPEngine', 'SAMEngine', 'MiDaSDepth', 'AdvancedVisionEngine',
    'AIUpscaler', 'RealESRGANUpscaler', 'StyleTransferEngine', 'ControlNetEngine',
    'MagicEraserEngine', 'ColorQuantizerEngine',
    'AIOrchestrator', 'LoomEngine', 'FabricRenderer3D', 'CostingEngine',
    'VoiceCommandEngine', 'DesignRecoveryEngine', 'DefectScannerEngine'
]
