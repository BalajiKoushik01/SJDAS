# Changelog

All notable changes to the **Smart Jacquard Design Automation System (SJ-DAS)** will be documented in this file.

## [v3.1.0] - 2025-12-23 - "United AI Hive Mind"
### Added
-   **LightStyleGAN Integration:** Added `stylegan_model.py` and `unified_ai_engine.py` logic to load and run high-res texture generation.
-   **Prompt Navigator (CLIP):** Added `clip_guidance.py` for text-based semantic search and rejection sampling.
-   **Global Exception Handler:** Added `sys.excepthook` in `run_sj_das.py` to catch and log all crashes.
-   **Memory Management:** Implemented `unload_models()` to dynamically free VRAM.

### Changed
-   **Configuration:** Moved all hardcoded paths to `sj_das.core.config.AppConfig`.
-   **Logging:** Replaced `print()` statements with centralized `logging_config` (Outputs to `logs/app.log`).
-   **Cleanup:** Archived legacy scripts (`transformer_gan`, notebooks) to `legacy_experiments/`.

### Fixed
-   **Crash:** Fixed Threading crash in `DesignerView` by decoupling QImage from thread logic.
-   **Dependency:** Fixed mutable default argument bug in `config.py`.

---

## [v3.0.0] - 2025-12-22 - "World Class Foundation"
### Added
-   **Training Pipeline:** `train_stylegan.py` with GPU acceleration and Thermal Monitoring.
-   **Dataset:** Massive scrape of 6,100+ textile images.
-   **UI:** Basic integration of "Best Quality" toggle.

## [v2.0.0] - 2025-12-15 - "Smart Patch"
-   Implemented `SmartPatchEngine` for patch-based synthesis.
-   Added Progressive GAN (64x64).

## [v1.0.0] - 2025-11-01 - "Prototype"
-   Initial PyQt6 Interface.
-   Basic Segmentation Tools.
