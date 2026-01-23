# Core utilities (optional imports)
try:
    from .design_utils import DesignUtils
except ImportError:
    DesignUtils = None

try:
    from .palette_manager import PaletteManager
except ImportError:
    PaletteManager = None

try:
    from .undo_system import UndoSystem
except ImportError:
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
except ImportError:
    # Fallback to old structure
    try:
        from .agent_engine import AgentEngine
    except ImportError:
        AgentEngine = None

    try:
        from .crew_engine import Agent, Crew, LocalLLMEngine, Task
    except ImportError:
        Crew = Agent = Task = LocalLLMEngine = None

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

    try:
        from .magic_eraser import MagicEraserEngine
    except ImportError:
        MagicEraserEngine = None

    try:
        from .quantizer import ColorQuantizerEngine
    except ImportError:
        ColorQuantizerEngine = None

# AI Orchestrator
try:
    from .ai_orchestrator import AIOrchestrator
except ImportError:
    AIOrchestrator = None

# Manufacturing Engines
try:
    from .loom_engine import LoomEngine
except ImportError:
    LoomEngine = None

try:
    from .fabric_renderer_3d import FabricRenderer3D
except ImportError:
    FabricRenderer3D = None

try:
    from .costing import CostingEngine
except ImportError:
    CostingEngine = None

# Voice
try:
    from .voice_engine import VoiceCommandEngine
except ImportError:
    VoiceCommandEngine = None

# Recovery
try:
    from .design_recovery import DesignRecoveryEngine
except ImportError:
    DesignRecoveryEngine = None

# Utilities
try:
    from .defect_scanner import DefectScannerEngine
except ImportError:
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
