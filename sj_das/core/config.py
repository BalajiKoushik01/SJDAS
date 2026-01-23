"""
Configuration Manager
---------------------
Centralizes all application settings, file paths, and constants.
Follows 12-Factor App principles for configuration.
"""

from dataclasses import dataclass, field
from pathlib import Path

import torch


@dataclass
class Paths:
    """Path configurations calculated relative to project root."""
    # Base Paths
    # We assume this file is in sj_das/core/config.py
    # Root is sj_das_project (3 levels up)
    ROOT: Path = Path(__file__).resolve().parent.parent.parent

    # App Directories
    SRC: Path = ROOT / "sj_das"
    CORE: Path = SRC / "core"
    UI: Path = SRC / "ui"
    ASSETS: Path = SRC / "assets"
    LOGS: Path = ROOT / "logs"

    # Data & Models
    DATASET: Path = ROOT / "dataset"
    MODELS: Path = SRC / "models"

    # Specific Model Paths
    STYLEGAN_MODELS: Path = MODELS / "stylegan_advanced"
    GAN_ADVANCED: Path = MODELS / "gan_advanced"

    def __post_init__(self):
        """Ensure critical directories exist."""
        self.LOGS.mkdir(exist_ok=True)
        self.MODELS.mkdir(exist_ok=True)


@dataclass
class ModelConfig:
    """AI Model Parameters."""
    Z_DIM: int = 128
    W_DIM: int = 128
    RESOLUTION: int = 256
    CHANNELS: int = 3
    BATCH_SIZE_INFERENCE: int = 8  # Batch size for CLIP scoring


@dataclass
class AppConfig:
    """Global Application Configuration."""
    NAME: str = "SJ-DAS"
    VERSION: str = "3.1.0 (United AI Hive Mind)"

    # ---------------------------------------------------------
    # VERSION HISTORY:
    # 3.1.0: United AI Hive Mind (StyleGAN + CLIP + Unified)
    # 3.0.0: World Class Foundation (Base Training)
    # ---------------------------------------------------------

    # Hardware
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"

    # Components
    paths: Paths = field(default_factory=Paths)
    models: ModelConfig = field(default_factory=ModelConfig)

    # Palette (Standard Saree Colors)
    PALETTE: list[tuple[int, int, int]] = (
        (40, 0, 60),    # Maroon
        (0, 215, 255),  # Gold
        (255, 100, 0),  # Royal Blue
        (0, 200, 0),    # Parrot Green
        (255, 0, 128),  # Pink
        (255, 255, 255)  # Silver
    )


# Singleton Instance
cfg = AppConfig()

if __name__ == "__main__":
    print(f"Loaded Config for {cfg.NAME} {cfg.VERSION}")
    print(f"Root: {cfg.paths.ROOT}")
    print(f"Device: {cfg.DEVICE}")
