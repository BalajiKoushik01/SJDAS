# SJDAS — Smart Jacquard Design Automation System
## Complete Upgrade Specification v2.0
### Prepared by: Balaji Koushik · Product Lead
### For: Software Development Team
### Date: March 2026 | Status: DRAFT FOR IMPLEMENTATION

---

> **North Star:** SJDAS must be the world's most capable Indian jacquard design platform — beating TCS, WeaverAI, Pointcarré, and NedGraphics on every axis. The core differentiator is the **Screenshot → Design Decode pipeline**: upload any messy photo of a saree, get a clean editable vector trace with all design layers separated, ready for power loom export. Everything else is a feature race we win by going deeper on India-specific intelligence.

---

## Table of Contents

1. [Current State Audit](#1-current-state-audit)
2. [Competitor Intelligence](#2-competitor-intelligence)
3. [Architecture Upgrade Plan](#3-architecture-upgrade-plan)
4. [AI Model Stack — Free & Open Source Only](#4-ai-model-stack--free--open-source-only)
5. [Feature Spec: All Modules](#5-feature-spec-all-modules)
   - 5.1 Screenshot Decode Pipeline
   - 5.2 Design Editor (Photoshop-Grade)
   - 5.3 Weave Builder & Loom Engine
   - 5.4 AI Assistant (Background, Silent)
   - 5.5 Color Intelligence
   - 5.6 Pattern Generation & Variations
   - 5.7 Loom Export Engine
   - 5.8 Factory Monitor
   - 5.9 Design Library & Asset Management
   - 5.10 Analytics Dashboard
6. [UI/UX Design System](#6-uiux-design-system)
7. [Tech Stack Decisions](#7-tech-stack-decisions)
8. [Implementation Roadmap — 4 Phases](#8-implementation-roadmap--4-phases)
9. [Testing & Quality Standards](#9-testing--quality-standards)
10. [Open Questions for Balaji](#10-open-questions-for-balaji)

---

## 1. Current State Audit

### What exists in the repo (as of March 2026)

**Folder structure confirmed:**
```
SJDAS/
├── backend/          — Python FastAPI or Flask backend (to be confirmed)
├── docs/             — Documentation, MINIMAX_INTEGRATION.md
├── examples/         — Usage examples for AI features
├── scripts/          — Utility scripts
├── sj_das/           — Core Python application
│   ├── ai/           — StyleGAN2-ADA, segmentation models
│   ├── core/         — loom_exporter.py, weave_manager.py, exceptions.py
│   ├── ui/           — PyQt6 components, editor_widget.py, commands.py
│   └── utils/        — geometry_utils.py (Bresenham, math)
├── tests/            — Unit + integration tests (100% coverage on core utils)
├── tools/            — Dev tools
├── web/              — Web frontend (JavaScript 1.6% — minimal)
├── launcher.py       — Entry point
└── requirements.txt  — Dependencies
```

**Languages:** Python 98.2%, JavaScript 1.6%, other 0.2%

**What is working (from README):**
- PyQt6 desktop UI launching correctly (9 bugs fixed Dec 2025)
- Pixel editor with undo/redo (Command pattern, O(1))
- BMP export for Jacquard looms (Udayravi Creations compatible)
- Auto-segmentation via OpenCV (body/border/pallu detection — basic)
- StyleGAN2-ADA pattern generation (variation synthesis)
- MiniMax M2.1 AI integration for conversational design assistance
- Weave structure library (Plain, Twill 2/2 / 3/1 / 3/3, Satin 4H / 8H)
- Hook configuration 1000–4000
- Color palette with yarn library

**Critical gaps vs. competitors:**
- No web app — desktop-only, Windows primary. Eliminates 60% of potential B2B clients
- No screenshot → trace decode pipeline (zero competitors have this either — this is our moat)
- No real-time loom monitoring / factory floor integration
- No repeat pattern engine (straight, half-drop, mirror)
- No 3D fabric simulation / drape preview
- No multi-format export (JC5, WIF, DXF, SVG, PDF production sheet)
- No regional language UI
- No design library / asset management
- UI is PyQt6 desktop — not premium or modern enough for B2B sales

---

## 2. Competitor Intelligence

### TCS (Most dangerous — launched Feb 2026, not commercially deployed yet)

**Platform:** "Intelligent Design Platform" + "Smart Weaver Assist"
- Voice input → loom-ready design
- Sketch / reference image → digital design → 3D output
- LED-guided thread movement system for real-time weaver guidance
- Piloted: Kanjivaram cluster, Kanchipuram
- Status: In discussions with Handloom Corporation of India + Ministry of Textiles
- **NOT commercially available — this is our 6–12 month window**
- Gap: No screenshot decode, no web platform, no multi-loom factory monitor

### WeaverAI (India, NTUitive Singapore-backed)

- Moodboard → seamless repeat → separated color layers in-browser
- Jacquard BMP generation: automated weave assignment, float checking, palette reduction
- Intelligent color separation with 300 DPI export
- Fashion virtual try-on, product draping
- Gap: No saree-specific intelligence, no screenshot decode, no India regional styles, no loom API

### Pointcarré (France, 40 years old)

- **Design Maker AI:** text/image prompt → design proposals in repeat
- **Jacquard Maker:** any image → jacquard design, yarn type selection, colorway + tech sheet export
- **Repeat Maker (Oct 2024):** automated pattern repetition — straight, half-drop, mirror, multidirectional
- **Color Separation Engine:** tonal separation, up to 255 combos, QTX/CxF support
- **Layers System:** non-destructive editing, rotate/resize without quality loss
- **Fabric Simulation:** 3D bump maps, Browzwear/Orchid export
- **LoomNet:** distributed production management, real-time factory collaboration
- **Pantone Textile Library:** 5,760 colors (Archroma partnership)
- Integrates with Adobe Photoshop + Illustrator
- Gap: Western-focused, no India saree context, expensive, desktop-heavy, no screenshot decode

### NedGraphics (Netherlands, 45 years, global market leader)

- Jacquard CAD/CAM: design, color, usage estimation, simulation, loom export
- **Jacquard Connect SDK:** integration with Stäubli, Bonas, Grosse loom controllers
- **NEDHub Cloud:** flexible licensing, ERP/PLM integration
- **AI Auto-tagging (NEDTag):** smart metadata on design files
- **NedGraphics 2026:** AI creativity tools, 3D fabric viewer (U3M format), drape/texture from any angle
- Real-time fabric simulation replacing physical sampling
- Automatic warp/weft scale generation, float checking
- Universal loom format conversion
- Gap: Expensive enterprise software, no India context, no screenshot decode

### WveCAD (New entrant, online)

- Browser-based jacquard + dobby design
- Artwork module: color-mapped weaves on images, 256 shafts
- Realistic fabric simulation, 3D model draping
- Gap: Generic, no AI intelligence, no India context, no loom machine integration

### Feature Gap Summary Table

| Feature | SJDAS (now) | TCS | WeaverAI | Pointcarré | NedGraphics |
|---|---|---|---|---|---|
| Screenshot → Decode | ❌ | ❌ | ❌ | ❌ | ❌ |
| India saree AI | partial | ✅ | ❌ | ❌ | ❌ |
| Web platform | ❌ | ❌ | ✅ | partial | ❌ |
| Repeat engine | ❌ | ❌ | ✅ | ✅ | ✅ |
| Color separation | partial | ❌ | ✅ | ✅ | ✅ |
| 3D simulation | ❌ | ✅ | partial | ✅ | ✅ |
| Loom machine API | partial | ❌ | ❌ | ✅ | ✅ |
| Factory monitor | ❌ | ❌ | ❌ | ✅ | ✅ |
| AI pattern gen | ✅ | ✅ | ✅ | ✅ | ✅ |
| Regional language | ❌ | ❌ | ❌ | ❌ | ❌ |
| Voice input | ❌ | ✅ | ❌ | ❌ | ❌ |

**SJDAS v2 must hit every green cell above plus own Screenshot → Decode exclusively.**

---

## 3. Architecture Upgrade Plan

### Decision: Migrate from PyQt6 Desktop → Web Platform

**Rationale:**
- B2B factory owners use Windows machines but don't install desktop software anymore
- Web = no deployment friction, instant updates, works on any device in a factory
- Existing Python backend is reusable — move to FastAPI microservices
- Keep PyQt6 as optional offline mode for loom controller machines without internet

**New Architecture:**

```
┌──────────────────────────────────────────────────┐
│                  FRONTEND                         │
│   Next.js 14 (App Router) + TypeScript            │
│   Konva.js (canvas editor) + Fabric.js            │
│   TailwindCSS + Framer Motion                     │
│   React Query + Zustand                           │
└────────────────────┬─────────────────────────────┘
                     │ REST + WebSocket
┌────────────────────▼─────────────────────────────┐
│                  BACKEND                          │
│   FastAPI (Python 3.13+)                          │
│   Celery + Redis (async AI job queue)             │
│   WebSocket server (loom live status)             │
└──────┬──────────────────────┬────────────────────┘
       │                      │
┌──────▼──────┐      ┌────────▼────────┐
│  AI PIPELINE│      │  LOOM SERVICES  │
│  (GPU node) │      │  TCP/IP bridge  │
│  SAM2       │      │  USB HID driver │
│  Real-ESRGAN│      │  BMP/JC5 gen   │
│  VTracer    │      │  Float checker  │
│  CLIP       │      │  WebSocket push │
│  StyleGAN2  │      └─────────────────┘
│  YOLOv8    │
└─────────────┘
       │
┌──────▼──────────────────────────────────────────┐
│                  STORAGE                         │
│  PostgreSQL (designs, users, loom configs)        │
│  MinIO / S3 (design files, BMP exports)          │
│  Redis (job queue, loom status cache)            │
└──────────────────────────────────────────────────┘
```

### Migration Strategy

- Phase 1: Build web frontend against existing backend endpoints
- Phase 2: Move AI pipeline to async Celery workers
- Phase 3: Add loom TCP/IP bridge as separate microservice
- Phase 4: PyQt6 desktop becomes thin client hitting the same API (offline mode)

---

## 4. AI Model Stack — Free & Open Source Only

All models below are free, open source, and self-hostable. No paid API dependencies.

### 4.1 Image Segmentation & Region Detection

**Model: SAM2 (Segment Anything Model 2) by Meta FAIR**
- License: Apache 2.0 — free for commercial use
- Checkpoint: `facebook/sam2.1-hiera-large` (224M params)
- Speed: 24.2 FPS on GPU, 6× faster than SAM1
- Use case: Automatic region detection — body / border / pallu / motif isolation
- Installation: `pip install sam2` or via HuggingFace Transformers
- CPU fallback: `sam2.1-hiera-tiny` (38.9M params) at 47.2 FPS
- Input: image + optional bounding box or point click prompts
- Output: high-quality segmentation masks per region

```python
from sam2.sam2_image_predictor import SAM2ImagePredictor
predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2.1-hiera-large")
with torch.inference_mode():
    predictor.set_image(image)
    masks, scores, _ = predictor.predict(
        point_coords=[[x, y]],
        point_labels=[1],
        multimask_output=True
    )
```

**Supplementary: YOLOv8-seg (Ultralytics)**
- License: AGPL-3.0 (free for open source / research)
- Use case: Real-time motif bounding box detection within each region
- Speed: ~20ms per image on GPU
- Custom-trainable on saree motif dataset

### 4.2 Image Enhancement & Upscaling

**Model: Real-ESRGAN by Tencent ARC Lab**
- License: BSD-3-Clause — free commercial use
- Use case: Upscale blurry/low-res phone screenshots 4× before decode pipeline
- Models available: `RealESRGAN_x4plus` (photos), `RealESRGAN_x4plus_anime_6B` (illustration-style sarees)
- Installation: `pip install basicsr; pip install realesrgan`
- Supports: 16-bit images, alpha channels, gray images, tile mode for large images
- CPU + GPU support (NCNN Vulkan for Intel/AMD)

```python
from realesrgan import RealESRGANer
upsampler = RealESRGANer(scale=4, model_path='weights/RealESRGAN_x4plus.pth')
output, _ = upsampler.enhance(img_array, outscale=4)
```

### 4.3 Vectorization (Raster → SVG Trace)

**Primary: VTracer by VisionCortex**
- License: MIT — free commercial use
- PyPI: `pip install vtracer` (0.6.15, updated March 2026)
- Use case: Convert SAM2 mask regions → clean SVG paths for designer editing
- Key advantage over Potrace: handles full-color input (not just B&W), O(n) algorithm, more compact output than Adobe Illustrator Image Trace

```python
import vtracer
vtracer.convert_image_to_svg_py(
    inp="mask_region.png",
    out="motif_border.svg",
    colormode='color',      # full color preservation
    hierarchical='stacked', # stacking strategy (no holes in output)
    mode='spline',          # smooth Bézier curves
    filter_speckle=4,       # remove noise smaller than 4px
    color_precision=6,      # bits per RGB channel
    corner_threshold=60,    # minimum angle to be a corner
    length_threshold=4.0    # minimum path length
)
```

**Fallback / Binary regions: Potrace**
- License: GPL-2.0
- Use case: High-contrast border regions, geometric motifs
- Output: SVG, DXF, EPS, PDF, GeoJSON
- Integration: call via `subprocess` from Python backend

### 4.4 Color Intelligence

**Dominant Color Extraction: ColorThief (Python)**
- License: MIT
- PyPI: `pip install colorthief`
- Use case: Extract dominant colors and build yarn palette from uploaded design
- Algorithm: Median cut clustering

```python
from colorthief import ColorThief
ct = ColorThief('design.jpg')
dominant = ct.get_color(quality=1)
palette = ct.get_palette(color_count=8)  # returns top 8 yarn colors
```

**Advanced Clustering: scikit-learn KMeans**
- License: BSD-3-Clause
- Use case: Intelligent color reduction for loom (reduce 16M colors → N yarn colors)
- User-configurable N from 2–256 (loom limit)

**Color Harmony Analysis: colorsys (Python stdlib)**
- Use case: Complementary, triadic, analogous palette suggestions
- No installation needed — built into Python

**Pantone/RAL matching: colour-science**
- License: BSD-3-Clause
- PyPI: `pip install colour-science`
- Use case: Match extracted colors to nearest Pantone Textile code

### 4.5 Pattern Recognition & Style Classification

**CLIP (Contrastive Language-Image Pretraining) by OpenAI**
- License: MIT
- HuggingFace: `openai/clip-vit-base-patch32`
- Use case: Zero-shot saree style classification — "Is this Kanjivaram, Banarasi, Pochampally?"
- No fine-tuning needed for classification prompts

```python
from transformers import CLIPProcessor, CLIPModel
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

inputs = processor(
    text=["Kanjivaram silk saree", "Banarasi zari saree", "Pochampally ikat saree"],
    images=image, return_tensors="pt", padding=True
)
outputs = model(**inputs)
style = ["Kanjivaram", "Banarasi", "Pochampally"][outputs.logits_per_image.argmax()]
```

**Custom YOLOv8 — Motif Detector (to be trained)**
- Training data: Scrape + label 500 saree images per style (Kanjivaram, Banarasi, Pochampally, Paithani)
- Classes: peacock, lotus, mango/paisley, temple border, geometric, floral, zari stripe
- Tool: Roboflow for labeling (free tier: 10K images)
- Expected mAP: 80%+ after 200 epochs on NVIDIA T4

### 4.6 Pattern Generation & Synthesis

**StyleGAN2-ADA (already in repo)**
- Keep existing integration
- Add fine-tuning on Indian saree dataset (500 images minimum)

**Seamless Repeat Generation: Custom algorithm**
- Implement: straight repeat, half-drop, mirror, multidirectional (matching Pointcarré Repeat Maker)
- Use numpy + PIL for tiling operations
- No external dependency needed

**Texture Synthesis: scikit-image**
- `skimage.texture` module for Gabor filter-based texture analysis
- Use case: Detect weave texture type from uploaded image

### 4.7 Image Processing (General)

**OpenCV (already in repo)**
- Core: denoising, thresholding, morphological ops, contour detection
- Additional use cases: deskew scanned designs, correct perspective distortion on phone photos

**Pillow / PIL**
- Core image I/O, format conversion, resize, crop, color mode conversion

**scikit-image**
- Advanced: Gabor filters for texture, Canny edge detection for pattern outlines, watershed segmentation

---

## 5. Feature Spec: All Modules

### 5.1 Screenshot → Design Decode Pipeline

**This is the product. Everything else supports this.**

#### What it must do
User uploads: a blurry phone photo, a WhatsApp-forwarded saree image, a torn catalog scan, or a high-res studio photo. Output: clean, editable, layer-separated SVG with body / border / pallu / individual motifs as separate layers, plus a warp/weft matrix, plus a loom-ready BMP — all automatically, in under 10 seconds on GPU.

#### Pipeline Steps (in order)

**Step 1: Ingest & Preprocess**
- Accept: PNG, JPG, WEBP, PDF scan, phone screenshot (any aspect ratio)
- Perspective correction: detect saree edges, apply homography transform (OpenCV `findHomography`)
- Deskew: detect rotation angle, auto-rotate
- Noise reduction: OpenCV `fastNlMeansDenoisingColored`
- Upscale if width < 1200px: Real-ESRGAN 4× upscale
- Normalize to sRGB color space

**Step 2: Global Segmentation (SAM2)**
- Run SAM2 AutomaticMaskGenerator on full image
- Post-process: merge small fragments (<50px²), classify regions by position and size ratio
- Classify each region: body (largest center region), border (horizontal bands), pallu (right/end section), motifs (small repeated elements)
- Output: 4 masked regions as separate numpy arrays

**Step 3: Motif Detection (YOLOv8)**
- Run custom-trained YOLOv8-seg on body and border regions
- Detect and localize: individual motifs (peacock, lotus, paisley, temple, geometric)
- Output: bounding boxes + class labels + confidence scores

**Step 4: Vectorization (VTracer)**
- For each SAM2 region mask: run VTracer → SVG paths
- For each YOLOv8 motif crop: run VTracer with higher precision settings
- Clean SVG: remove artifacts smaller than 3px, simplify paths with Douglas-Peucker algorithm
- Output: layered SVG file with named layers: `#layer-body`, `#layer-border`, `#layer-pallu`, `#layer-motif-1..n`

**Step 5: Color Separation**
- Run ColorThief on each region to extract dominant yarn colors
- Run KMeans with user-specified N clusters (default: 6, max: 256)
- Map each pixel to nearest cluster centroid → color-indexed regions
- Output: separated color channels, one image per color, exportable at 300 DPI

**Step 6: Style Classification (CLIP)**
- Classify full image: Kanjivaram / Banarasi / Pochampally / Paithani / Other
- Output: style label + confidence score + recommended weave structure for that style

**Step 7: Weave Matrix Generation**
- Based on detected style + complexity: assign weave type per region
  - Body: Plain weave (2-harness)
  - Border: Twill 2/2 (4-harness)
  - Pallu: Satin 8-harness
  - Motifs: Compound Jacquard (based on hook count)
- Generate warp/weft interlacement matrix as numpy bool array
- Run float checker: max float length, binding point percentage
- Output: weave matrix + float check report

**Step 8: BMP Compilation**
- Map weave matrix + color separation → BMP pixel grid
- Dimensions: hook_count × pattern_length
- Color depth: 2–256 colors (user config)
- Output: `design_loom_ready.bmp` at 300 DPI

#### Robustness Requirements
- Must handle images as low as 320×240px (upscale first)
- Must handle off-angle photos (up to 30° tilt) via perspective correction
- Must handle JPEG compression artifacts (denoise before processing)
- Must handle partial/cropped saree images (auto-detect available regions only)
- Must handle solid-color or very simple designs (graceful fallback — output what is detectable)
- Processing timeout: 30 seconds maximum, with progress streaming to frontend via WebSocket
- Confidence threshold: if any step scores below 0.6 confidence, flag for human review rather than silently producing wrong output

#### User Controls (visible in UI)
- Style override: user can correct the auto-detected style
- Hook count slider: 1000–4000
- Color count slider: 2–64 (with preview update)
- Layer visibility toggles: show/hide body / border / pallu / motifs
- Region editor: user can draw custom region boundaries to override SAM2
- Motif editor: user can delete false positive detections, add missed motifs

#### AI Assist (silent, background)
After decode completes, the AI assistant automatically (without being asked) generates:
- A brief analysis card: "Detected Kanjivaram style · 3 peacock motifs · 6 colors · high complexity"
- One weave recommendation: "Satin 8-harness for pallu will give maximum zari lustre"
- One alert if there are issues: "Border repeat gap detected — motif spacing inconsistent at x=340px"

---

### 5.2 Design Editor (Photoshop-Grade)

The editor must match Adobe Photoshop's core toolset for raster editing plus Illustrator's vector capabilities for the SVG layers. All tools must work on both raster (BMP grid) and vector (SVG trace) modes simultaneously.

#### Canvas Modes
- **Raster mode:** pixel-level BMP editing (existing, improve)
- **Vector mode:** SVG path editing with Bezier handles
- **Hybrid mode:** overlay both layers, edit independently

#### Complete Tool List

**Selection Tools**
- Rectangular marquee
- Elliptical marquee
- Lasso (freehand)
- Polygonal lasso
- Magnetic lasso (edge-snapping)
- Magic wand (tolerance-based color select)
- Quick select (AI-assisted: click to select entire motif)
- Select by color range
- Select by saree region (body / border / pallu — shortcut keys B / D / P)
- Invert selection
- Feather selection edges (0–250px)
- Expand / contract selection
- Save / load selection as mask

**Drawing Tools**
- Brush (size 1–500px, hardness, opacity, flow, angle, roundness)
- Pencil (aliased, hard edge)
- Eraser (brush / block / background eraser modes)
- Fill (flood fill with tolerance)
- Gradient fill (linear, radial, angle, reflected, diamond; custom color stops)
- Pattern stamp (textile-specific pattern library)
- Healing brush (clone + blend for fixing scan artifacts)
- Spot healing brush (one-click artifact removal)
- Clone stamp
- History brush (paint from any history state)

**Shape Tools**
- Rectangle, rounded rectangle, ellipse, polygon, line, custom shape
- Path operations: unite, subtract, intersect, exclude
- All shapes editable as vector paths

**Transform Tools**
- Move, rotate, scale, skew, perspective, warp
- Free transform with numeric input
- Content-aware scale (stretch design without distorting motifs)
- Puppet warp (pin-based mesh deformation for motif reshaping)
- Liquify filter (push, pull, twirl, pucker, bloat — motif warping)

**Vector / Path Tools (for SVG layers)**
- Pen tool (Bezier path creation)
- Freeform pen
- Add / delete / convert anchor point
- Direct selection (individual path points)
- Path selection (entire path)
- All standard SVG path operations

**View Tools**
- Zoom (1%–6400%)
- Hand / pan
- Eyedropper (sample color, sample size 1px / 3×3 / 5×5 avg)
- Measure tool (distances in px, mm, inches)
- Grid overlay (configurable grid size, snap to grid)
- Ruler guides (drag from rulers, custom placement)
- Smart guides (auto-snap to edges and centers of objects)

**Text Tool**
- Add text annotations on designs (for production notes)
- Font size, family, weight, spacing

#### Layer System
- Unlimited layers (body, border, pallu, motif1..n, weave grid, notes)
- Layer groups (collapse / expand)
- Layer blend modes: Normal, Multiply, Screen, Overlay, Soft Light, Hard Light, Color, Luminosity
- Layer opacity 0–100%
- Layer masks (non-destructive — paint black to hide, white to reveal)
- Clipping masks
- Layer locking (position lock, pixel lock, all lock)
- Duplicate layer
- Merge layers / flatten
- Smart Objects: embed vector SVG as non-destructive smart layer
- Drag-and-drop layer reordering

#### Adjustments (Non-Destructive, via Adjustment Layers)
- Brightness / Contrast
- Levels (RGB channels individually or combined)
- Curves (full curve editor per channel)
- Exposure
- Vibrance
- Hue / Saturation (including targeted color range adjustment)
- Color Balance (shadows / midtones / highlights)
- Photo Filter (warm/cool/custom)
- Channel Mixer
- Gradient Map
- Selective Color
- Invert
- Posterize (reduce to N colors — useful for loom color reduction)
- Threshold

#### Filters
- Blur (Gaussian, Motion, Radial, Surface, Smart Blur)
- Sharpen (Unsharp Mask, Smart Sharpen)
- Noise (Add Noise, Reduce Noise, Despeckle)
- Distort (Wave, Ripple, Polar Coordinates — for pattern warping)
- Stylize (Find Edges — useful for tracing outlines, Emboss, Solarize)
- Texture (Grain, Mosaic Tiles — for weave preview)
- Render (Clouds, Fibers — for design base generation)

#### Undo / History
- Unlimited undo (Ctrl+Z / Cmd+Z)
- History panel: 100 states visible, click any to jump back
- History brush: paint from any past state
- Snapshot: save current state as named checkpoint

#### Textile-Specific Tools (unique to SJDAS, no competitor has these)
- **Motif Extractor:** click any motif → auto-select + isolate into new layer
- **Repeat Preview:** toggle live repeat mode — see design tiled in straight, half-drop, or mirror mode
- **Weave Overlay:** toggle warp/weft grid overlay on any design layer
- **Yarn Color Lock:** pin a color to a specific yarn — edits to that color region propagate to loom config
- **Float Visualizer:** highlight any warp or weft floats exceeding user-set limit (colored red)
- **Mirror Axis:** draw design on one side, mirror propagates to other side in real time
- **Region Sync:** changes to motif layer auto-propagate to repeat instances

---

### 5.3 Weave Builder & Loom Engine

#### Visual Weave Matrix Editor
- Grid display: N×M cells (configurable, up to 256×256 for jacquard)
- Click to toggle warp raised (gold) / weft raised (dark)
- Brush: paint multiple cells in one stroke
- Fill row / fill column shortcuts
- Copy / paste rectangular selections within matrix

#### Weave Structure Library (pre-built)
Every structure is editable after loading.

| Structure | Harness | Typical Use in Saree |
|---|---|---|
| Plain weave | 2 | Body — lightweight silk |
| Twill 2/2 | 4 | Border — diagonal sheen |
| Twill 3/1 | 4 | Border — satin-like face |
| Twill 3/3 | 6 | Body — heavy silk |
| Satin 4H | 4 | Pallu — moderate lustre |
| Satin 8H | 8 | Pallu — maximum lustre |
| Satin 12H | 12 | Zari motif — maximum float |
| Compound Twill | 8 | Complex motifs |
| Compound Satin | 16 | Fine Kanjivaram motifs |
| Crepe | 6 | Body — textured |
| Hopsack 2/2 | 4 | Background texture |
| Double weave | 8 | Reversible pallu |
| Velvet (cut pile) | 16 | Luxury border |
| Custom | user-defined | Any |

#### Weave Validation (runs silently on every edit)
- **Float checker:** flag any warp or weft float exceeding user-set limit (default: 8)
- **Binding point analysis:** calculate % of interlacement points (minimum safe: 25%)
- **Color balance:** warn if too many consecutive same-color picks
- **Loom compatibility:** check against selected machine's max harness count
- **Repeatability:** verify the structure tiles without visible seam

#### Fabric Simulation Preview (real-time)
- Render woven fabric texture using weave matrix + yarn colors
- Update live as user edits matrix cells (debounce: 300ms)
- 3D drape simulation (simplified — flat with shading, not full physics)
- Toggle: flat view / 45° drape view
- Export simulation as PNG for client presentations

#### Loom Parameters Panel
- Machine selector: Stäubli JC5 / JC6 / JC7, Bonas, Grosse, Udayravi, Custom
- Hook count: 1000–4000 (slider + numeric input)
- Ends per inch (EPI): 40–240
- Picks per inch (PPI): 40–200
- Warp and weft yarn type: silk, cotton, linen, zari (gold), zari (silver), synthetic
- Reed count
- Repeat width × height in mm

---

### 5.4 AI Assistant (Background, Silent, Seamless)

**Design philosophy:** The AI must never feel like a separate chatbot you have to prompt. It observes what the user is doing and surfaces the right suggestion at the right moment — exactly like a senior textile designer looking over your shoulder. Explicit chat is available but secondary.

#### Silent Background Intelligence (no prompt needed)

**On decode complete:**
- Auto-generates style card: "Detected: Kanjivaram silk · Peacock motif × 3 · Border: temple repeat · Colors: 6 · Complexity score: 87/100"
- Auto-suggests weave structure assignment for each region
- Auto-flags any decode quality issues

**While editing:**
- When user adjusts a motif: "This peacock tail has 7 float threads. Your Udayravi loom max is 8. You're close to the limit."
- When user changes colors: "These 2 colors (Δ=4.2) may appear as a single color in 300 DPI print. Consider increasing contrast."
- When user draws an asymmetric border: "Border motif spacing uneven — left gap 12px, right gap 18px. Want me to equalize?"

**Proactive alerts panel (right sidebar):**
- List of AI-generated suggestions, each dismissible or one-click-applicable
- Severity: Info (blue) / Warning (amber) / Error (red)
- Example alerts:
  - ⚠ "Float length 9 detected at row 142 — exceeds JC5 limit of 8"
  - ℹ "Kanjivaram pallu typically uses 12-harness satin for this motif density"
  - ✅ "Design validated — loom-ready"

**On export:**
- Auto-checks: float compliance, color count vs. hook count, repeat integrity, file size
- Generates production sheet notes: estimated weaving time, yarn requirements estimate

#### Explicit AI Chat (when user opens it)
- Context-aware: knows what design is open, what tool is active, what region is selected
- Example queries supported:
  - "Analyze this motif" → pattern type ID, cultural context, weave recommendation
  - "Suggest colors for a wedding saree" → palette with yarn codes
  - "What's the traditional Banarasi border for this body pattern?"
  - "Generate 3 variations of this peacock motif"
  - "Is this design loom-ready?" → full validation report
  - "What's the production time estimate for this design on a JC5?"

#### Voice Input (Phase 3)
- Integrate `whisper` (OpenAI, MIT license) for speech-to-text
- Trigger phrase: double-tap microphone icon or say "Hey SJ-DAS"
- Commands: "Zoom in on the border", "Select the pallu region", "Change body color to deep red", "Export as BMP"

---

### 5.5 Color Intelligence

#### Yarn Color Management
- Master yarn library: 500+ pre-loaded colors with real silk yarn names
- Pantone Textile code matching (via `colour-science`)
- Custom yarn color creation: hex / RGB / HSL input
- Color families: group by hue range for quick browsing
- Seasonal palette templates: bridal (reds/golds), festive, daily wear, export market

#### Color Separation Engine
- Runs automatically after decode, manually triggerable
- Input: full-color design image
- Output: N separate channel images (one per yarn color)
- User control: slider for N (2–64), preview updates in real time
- Color merging: drag colors in palette to merge two similar yarns
- Color splitting: split one color into two with boundary adjustment
- Export: 300 DPI separated channel PNGs + color spec sheet PDF

#### Colorway Generator (like Pointcarré's 255 combos)
- Base design → generate N colorway variations automatically
- Strategies: complementary, analogous, monochromatic, random, seasonal
- Batch export: all colorways as separate files
- Client presentation mode: display all colorways in grid

#### Color Harmony Checker
- Warn if selected yarn colors clash visually at weave scale
- Suggest adjustments based on color theory rules

---

### 5.6 Pattern Generation & Variations

#### Repeat Engine (matching Pointcarré Repeat Maker)
- Straight repeat
- Half-drop repeat (vertical or horizontal)
- Mirror repeat (horizontal, vertical, four-way)
- Brick repeat
- Diamond repeat
- Toss (random rotation/flip — for all-over body patterns)
- User sets: repeat width × height in mm, overlap amount
- Live preview: see full repeat tile in canvas

#### AI Variation Generator (StyleGAN2-ADA — existing, improve)
- Input: one base motif or full design
- Output: N variations (configurable, default 6)
- Variation modes:
  - Shape variation (keep colors, alter geometry)
  - Color variation (keep shape, alter palette)
  - Style transfer (keep motif, transfer style of another regional saree)
  - Complexity variation (simplify for lower hook counts, or enrich for higher)
- User selects preferred variation → opens in editor

#### Motif Library
- 200+ pre-built Indian textile motifs (SVG, editable):
  - Peacock, lotus, mango/paisley, elephant, deer, temple gopuram
  - Geometric: diamond, chevron, hexagon, check, stripe
  - Zari patterns: gold chain, silver vine, border keyline
  - Regional specific: Kanjivaram korvai, Banarasi jangla, Pochampally diamond ikat
- Searchable by name, style, complexity
- Drag-drop any motif onto canvas
- Resize, rotate, recolor without quality loss (SVG)
- User-contributed motifs (upload + tag)

---

### 5.7 Loom Export Engine

This is the pipeline from finished design to machine-ready file.

#### Export Formats (all free/open implementations)

| Format | Machine | Implementation |
|---|---|---|
| BMP | Universal jacquard | Existing + upgrade |
| JC5 / JC6 / JC7 | Stäubli machines | Reverse-engineered from spec |
| WIF (Weave Info File) | ArahWeave, WveCAD, universal | PyWIF library (MIT) |
| DAT / HIF | Bonas machines | Binary format encoder |
| SVG | Design editing | VTracer output |
| DXF | CAD systems | `ezdxf` library (MIT) |
| PDF Production Sheet | Factory floor | `reportlab` (BSD) |
| PNG (300 DPI) | Client presentation | Pillow |

#### Pre-Export Validation (mandatory, auto-runs)
1. Float check: flag all floats > machine limit
2. Color count check: must not exceed loom's color capability
3. Repeat integrity: verify tiling with no gaps or overlaps
4. Dimension check: width must match hook count exactly
5. Binding point minimum: warn if < 25%
6. File size estimate: calculate final BMP size before export

#### Transfer Methods
- Download to computer (USB to loom controller)
- TCP/IP direct send (for network-connected loom controllers)
  - User enters loom IP:port in settings
  - SJDAS sends file via TCP socket, receives confirmation
- Email to factory (ZIP attachment, auto-notify)
- Cloud sync: store in MinIO, factory retrieves by job ID

#### Production Sheet (PDF auto-generated)
One-page PDF per design containing:
- Design thumbnail
- Style, complexity, detected motifs
- Weave structure per region
- Color spec table (yarn name, hex, Pantone code, quantity estimate)
- Hook count, EPI, PPI settings
- Float validation result
- Estimated weaving time (formula-based)
- QR code linking to live design file in SJDAS

---

### 5.8 Factory Monitor

#### Loom Connection
- Add looms via: IP address (TCP/IP), USB serial, or manual status entry
- Loom profile: name, machine type, hook count, location in factory
- Ping loom every 30s, update status via WebSocket

#### Live Status Dashboard
- Status cards per loom: running / idle / error / maintenance
- Status indicator: animated green dot (running), static gray (idle), pulsing red (error)
- Per running loom:
  - Current design name
  - Progress bar (picks completed / total picks)
  - ETA
  - Current speed (picks per minute)
  - Color sequence progress
- Per error loom:
  - Error code + description
  - Error location (pick number, hook number)
  - Recommended action

#### Job Queue Management
- Queue multiple designs per loom
- Drag-and-drop reorder
- Schedule jobs: set start time
- Job history: all past jobs with duration, completion status

#### Alerts & Notifications
- Thread break detected → push notification (browser + email)
- Design complete → push notification
- Loom offline → push notification
- Color change required → push notification with instructions

#### Analytics
- Loom utilization % per day / week / month
- Designs produced per loom
- Most common error types
- Average job duration by design complexity

---

### 5.9 Design Library & Asset Management

#### Design Storage
- All decoded and created designs stored in PostgreSQL + MinIO
- Metadata: style, motifs detected, hook count, colors, creation date, last modified, tags, export status
- Full-text search across all metadata
- Filter by: style, date range, status, color count, complexity

#### Version Control
- Every save creates a new version (like Git)
- Version history panel: see all versions, revert to any
- Named versions: "Client approved v3", "Before color change"
- Compare two versions side-by-side

#### Collections
- Group designs into named collections (by client, season, style)
- Share collection link with client (view-only)
- Client can leave comments on designs

#### Import
- Import from: local file (SVG, PNG, JPG, BMP, WIF, DXF)
- Import from competitor formats (if provided by user — no reverse engineering needed, user uploads)

---

### 5.10 Analytics Dashboard

#### Business Metrics
- Designs decoded this month / vs last month (% change)
- Average decode time trend
- Export count by format
- Loom utilization rate (requires factory monitor integration)
- Most-used design styles

#### AI Performance Metrics
- Decode confidence scores over time
- User correction rate (how often users override AI segmentation — indicates accuracy)
- Most common AI alerts generated

#### Charts
- Bar: decodes per day (last 30 days)
- Pie: design style breakdown
- Line: decode time trend
- Stacked bar: loom utilization by machine

---

## 6. UI/UX Design System

### Design Philosophy
**Premium · Clean · Sleek · Modern · Purposeful**

The UI must feel like a mix of Figma (professional creative tool, dark mode, precise), Linear (fast, keyboard-first, minimal chrome), and a high-end B2B SaaS dashboard. Not generic — contextual to Indian textile manufacturing but globally professional.

### Color System (Dark Theme — Primary)

```css
--bg-base:          #0a0b0f;   /* deepest background */
--bg-surface:       #0f1117;   /* sidebar, navbar */
--bg-elevated:      #141620;   /* cards */
--bg-hover:         #1a1d2a;   /* hover states */
--bg-active:        #1f2333;   /* active/selected */

--accent-gold:      #c9a84c;   /* primary accent — zari gold */
--accent-gold-light:#e8c97a;   /* hover state for gold */
--accent-gold-dim:  rgba(201,168,76,0.15); /* subtle background tint */

--accent-teal:      #2dd4b0;   /* success, running, positive */
--accent-red:       #f04c5f;   /* error, alert, danger */
--accent-purple:    #8b6ff5;   /* AI features, secondary */
--accent-blue:      #4fa3ff;   /* info, links */

--text-primary:     #e8e9f0;
--text-secondary:   #9a9db0;
--text-muted:       #5a5e78;

--border:           rgba(255,255,255,0.06);
--border-hover:     rgba(255,255,255,0.12);
--border-focus:     rgba(201,168,76,0.5);  /* gold focus ring */

--radius-sm:        8px;
--radius-md:        12px;
--radius-lg:        18px;
--radius-xl:        24px;
```

Light theme: white base (`#ffffff`), surfaces `#f8f9fc`, same accent colors. Toggle in settings.

### Typography

- **Primary:** `DM Sans` — clean geometric sans, modern, excellent at small sizes
- **Monospace:** `DM Mono` — for hex codes, file sizes, loom parameters
- **Display:** `DM Serif Display` — for marketing/onboarding screens only

```css
--font-sans:  'DM Sans', system-ui, sans-serif;
--font-mono:  'DM Mono', 'Fira Code', monospace;
--font-display: 'DM Serif Display', Georgia, serif;

/* Scale */
--text-xs:   11px / 1.4;
--text-sm:   13px / 1.5;
--text-base: 14px / 1.6;
--text-md:   15px / 1.6;
--text-lg:   18px / 1.4;
--text-xl:   22px / 1.3;
--text-2xl:  28px / 1.2;
--text-3xl:  36px / 1.1;
```

### Spacing System (8px base grid)
```
4px  — micro gaps (icon to label)
8px  — small (within components)
12px — medium-small
16px — medium (between components)
20px — medium-large
24px — large (card padding)
32px — section gap
48px — major section break
```

### Motion & Animation

- **Default transition:** `150ms ease-out` for hover states
- **Page transitions:** `200ms cubic-bezier(0.4, 0, 0.2, 1)` — fade + 6px translateY
- **Sidebar expand/collapse:** `250ms cubic-bezier(0.4, 0, 0.2, 1)`
- **Modal appear:** `200ms` scale from 0.96 + fade
- **Toast notifications:** slide in from bottom-right, `300ms spring`
- **AI pipeline progress:** each step animates in sequentially (stagger 150ms)
- **Loom status pulse:** `2s ease-in-out infinite` for running indicator
- **Decode result reveal:** `fadeInUp 300ms` staggered per element
- **Canvas operations:** no animation — immediate response is critical
- **Reduced motion:** wrap all non-essential animations in `@media (prefers-reduced-motion: no-preference)`
- **Library:** Framer Motion for React component animations, CSS transitions for simple states

### Layout

```
┌─────────────────────────────────────────────────┐
│ TOPBAR (56px) — breadcrumb, search, actions      │
├──────────┬──────────────────────────────────────┤
│ SIDEBAR  │  MAIN CONTENT (scrollable)           │
│ (220px)  │                                      │
│          │  ┌─ CANVAS / PAGE CONTENT ──────┐   │
│ Nav items│  │                               │   │
│          │  │                               │   │
│          │  └───────────────────────────────┘   │
│          │                                      │
│ User pill│  ┌─ RIGHT PANEL (contextual) ───┐   │
└──────────┴──┴───────────────────────────────┴───┘
```

For the editor specifically:
```
┌─ TOPBAR ────────────────────────────────────────┐
├─ TOOLS (44px vertical left) ── CANVAS ── PANELS ┤
│                               (flex:1)  (280px) │
│  tool buttons                          Layers   │
│                                        Colors   │
│                                        Properties│
└─────────────────────────────────────────────────┘
```

### Component Standards

**Cards:**
- Background: `--bg-elevated`
- Border: `1px solid var(--border)`
- Radius: `var(--radius-lg)` (18px)
- Padding: 20px
- Hover: border transitions to `--border-hover`
- Active/selected: border `1px solid var(--accent-gold)`, background `var(--accent-gold-dim)`

**Buttons:**
- Primary: gold fill (`--accent-gold`), dark text, `font-weight: 600`
- Secondary: transparent, `--border-hover` border, `--text-secondary` color
- Danger: transparent, red border, red text
- All buttons: `height: 36px`, `padding: 0 16px`, `border-radius: var(--radius-sm)`, `font-size: 13px`
- Hover: 10% brightness increase
- Active: scale(0.98)
- Disabled: 40% opacity, no pointer events

**Form Inputs:**
- Background: `--bg-hover`
- Border: `1px solid var(--border)`
- Focus: border `1px solid var(--border-focus)` (gold)
- Height: 36px
- Padding: `0 12px`
- Font: `--font-sans`, 13px

**Chips / Badges:**
- Inline status indicators
- Variants: gold (active), teal (success), red (error), purple (AI), blue (info)
- Background: dim variant of color, text: light variant
- Border radius: 20px (pill)
- Padding: `4px 10px`, font-size: 11px, font-weight: 500

**Data Tables:**
- Header: 11px, uppercase, `letter-spacing: 0.5px`, `--text-muted`
- Row: 13px, `--text-secondary`, hover: subtle background tint
- First column: bold, `--text-primary`
- Border: bottom only, `1px solid rgba(255,255,255,0.03)`

**Progress Bars:**
- Track: `--bg-active` (4px height)
- Fill: gold (default), teal (running), red (error)
- Border radius: 2px

**Toast Notifications:**
- Appear bottom-right, stack vertically with 8px gap
- Auto-dismiss: 4s (info), 6s (warning), stays until dismissed (error)
- Types: success (teal), info (blue), warning (gold), error (red)
- Contains: icon + title + optional description + close button

### Keyboard Shortcuts (required)

| Shortcut | Action |
|---|---|
| Ctrl+Z / Cmd+Z | Undo |
| Ctrl+Shift+Z | Redo |
| Ctrl+S | Save |
| Ctrl+E | Export |
| B | Body region select |
| D | Border/Pallu select |
| V | Selection tool |
| M | Marquee tool |
| L | Lasso tool |
| W | Magic wand |
| B | Brush |
| E | Eraser |
| G | Fill/gradient |
| S | Clone stamp |
| Ctrl+T | Free transform |
| Ctrl+D | Deselect |
| Ctrl+A | Select all |
| [ / ] | Decrease / increase brush size |
| Spacebar | Pan (hold) |
| Ctrl+0 | Fit to window |
| Ctrl+1 | 100% zoom |
| +/- | Zoom in/out |

---

## 7. Tech Stack Decisions

### Frontend
| Technology | Choice | Reason |
|---|---|---|
| Framework | Next.js 14 (App Router) | Server components, excellent performance, Vercel deploy |
| Language | TypeScript | Type safety for complex design state |
| Canvas | Konva.js + react-konva | 2D canvas with React integration, high performance |
| Vector editing | Fabric.js | SVG manipulation, path editing |
| Animations | Framer Motion | Smooth, spring-based animations |
| State management | Zustand | Simple, performant, no boilerplate |
| Server state | TanStack Query | Caching, background refetch, optimistic updates |
| Styling | TailwindCSS + CSS variables | Utility-first + custom design tokens |
| WebSocket | socket.io-client | Loom live status, AI progress streaming |
| File handling | react-dropzone | Drag-drop file upload |
| Charts | Recharts | Analytics dashboard |
| Testing | Vitest + Playwright | Unit + E2E |

### Backend
| Technology | Choice | Reason |
|---|---|---|
| Framework | FastAPI (Python 3.13+) | Async, auto-docs, type hints, fast |
| Task queue | Celery + Redis | Async AI jobs (decode pipeline takes 5–30s) |
| WebSocket | FastAPI WebSockets | Real-time loom status push |
| Database | PostgreSQL (via SQLAlchemy + Alembic) | Relational, migrations |
| File storage | MinIO (self-hosted S3) | Designs, BMP exports, no cloud dependency |
| Cache | Redis | Session, job status, loom status |
| Auth | FastAPI-Users + JWT | License-based B2B auth |
| Testing | pytest + pytest-asyncio | Maintain existing test coverage |
| Linting | ruff (existing) | Keep |
| Type checking | mypy (existing) | Keep |

### AI / ML
| Model | Use Case | License |
|---|---|---|
| SAM2 (facebook/sam2.1-hiera-large) | Image segmentation | Apache 2.0 |
| Real-ESRGAN | Image upscaling | BSD-3-Clause |
| VTracer | Raster → SVG | MIT |
| CLIP (openai/clip-vit-base-patch32) | Style classification | MIT |
| YOLOv8 (custom-trained) | Motif detection | AGPL-3.0 |
| StyleGAN2-ADA (existing) | Pattern generation | Nvidia custom (non-commercial OK) |
| Whisper (openai/whisper-base) | Voice input (Phase 3) | MIT |
| ColorThief | Palette extraction | MIT |
| colour-science | Pantone matching | BSD-3-Clause |
| scikit-learn | KMeans clustering | BSD-3-Clause |
| OpenCV (existing) | Image processing | Apache 2.0 |

### Infrastructure
| Component | Choice |
|---|---|
| Deployment | Vercel (frontend) + Railway/Fly.io (backend) |
| GPU inference | Modal.com (serverless GPU, pay-per-second) or on-prem NVIDIA T4 |
| CI/CD | GitHub Actions (existing .github/workflows) |
| Monitoring | Sentry (errors) + Posthog (analytics) |
| Secrets | GitHub Secrets + .env files |

---

## 8. Implementation Roadmap — 4 Phases

### Phase 1 — Foundation Web Platform (Weeks 1–6)
**Goal:** Existing PyQt6 features, now in browser. Ship to first B2B client.

**Deliverables:**
- Next.js app scaffolding with full design system (tokens, components, layouts)
- Sidebar navigation, topbar, all 10 pages (empty shells)
- FastAPI backend: expose existing `loom_exporter.py` and `weave_manager.py` as REST endpoints
- BMP export working through web UI
- Weave matrix editor (canvas-based)
- Yarn color palette (with ColorThief integration)
- Basic design upload + display
- User auth (JWT, B2B license tier)
- Deploy to Vercel + Railway

**Team assignments:**
- Frontend dev 1: Design system, components, layout, sidebar, topbar
- Frontend dev 2: Weave matrix editor (Konva.js), color palette
- Backend dev 1: FastAPI setup, wrap existing Python modules as endpoints, auth
- Backend dev 2: PostgreSQL schema, MinIO setup, file upload/download
- ML dev: Environment setup, test existing StyleGAN2 and OpenCV via API endpoint

---

### Phase 2 — Screenshot Decode Pipeline (Weeks 7–14)
**Goal:** The core product. The thing no competitor has.

**Deliverables:**
- Real-ESRGAN integration: auto-upscale low-res uploads
- SAM2 integration: automatic region detection (body/border/pallu)
- VTracer integration: mask → SVG layer output
- ColorThief + KMeans: color extraction, N-color reduction
- CLIP: saree style classification
- Weave matrix auto-generation from detected style
- BMP compilation from weave matrix + color-separated regions
- 6-step progress streaming via WebSocket to frontend
- Decode results panel: SVG preview with layer toggles
- Float checker (backend)
- Celery task queue for async processing
- User controls: style override, hook count, color count
- YOLOv8 motif detector: collect training data + label + train (runs in parallel)

**Critical test targets:**
- Upscaling: test on 10 low-res phone photos
- SAM2: test on 20 saree images, verify body/border/pallu separation ≥ 85% accuracy
- VTracer: test on 20 decoded regions, verify SVG path quality
- End-to-end decode time: ≤ 10s on GPU, ≤ 60s on CPU

---

### Phase 3 — Design Editor + AI Assistant (Weeks 15–22)
**Goal:** Full Photoshop-grade editing + seamless background AI.

**Deliverables:**
- Full editor canvas (Konva.js + Fabric.js hybrid)
- All selection tools, drawing tools, transform tools
- Complete layer system (non-destructive)
- All adjustment layers and filters
- History panel (100 states)
- SVG path editing (vector mode)
- Repeat engine: straight, half-drop, mirror, toss
- AI alert panel (proactive suggestions during editing)
- AI chat panel (explicit queries)
- Voice input (Whisper integration)
- StyleGAN2 variation generator UI
- Motif library (200 pre-built SVGs)
- Colorway generator
- 3D drape preview (simplified)

---

### Phase 4 — Production Platform (Weeks 23–30)
**Goal:** Full B2B platform ready for factory deployment and scale.

**Deliverables:**
- Factory Monitor: loom TCP/IP bridge, WebSocket status, job queue
- Multi-format export: JC5, WIF, DAT, DXF, PDF production sheet
- Design library: versions, collections, client sharing
- Analytics dashboard: all metrics and charts
- Regional language UI: Tamil, Telugu, Kannada, Hindi
- PDF export of production sheets (reportlab)
- Email notification system
- Mobile-responsive layout (factory floor use on tablet)
- Performance hardening: lazy load, canvas virtualization, CDN for assets
- Security audit: OWASP top 10, penetration test
- Patent filing prep: document the Screenshot → Decode pipeline with technical claims

---

## 9. Testing & Quality Standards

### Backend
- Maintain existing 100% coverage on `geometry_utils`, `commands`, core utilities
- New modules: ≥ 80% line coverage minimum
- All AI pipeline functions: integration tests with sample images
- Loom export: golden file tests (compare output BMP byte-by-byte against reference)
- Float checker: unit tests with edge cases (zero floats, max floats, invalid structures)

### Frontend
- Component tests: Vitest + React Testing Library for all UI components
- E2E tests: Playwright for complete user flows
  - Upload → decode → edit → export (happy path)
  - Low-res image → upscale → decode
  - Loom connection → job send → status update
- Accessibility: WCAG 2.1 AA minimum (axe-core automated checks)
- Performance: Lighthouse score ≥ 90 on all pages

### AI Pipeline
- Segmentation accuracy benchmark: test set of 50 labeled saree images, target ≥ 85% IoU
- Vectorization quality: manual review of SVG output for 20 test images
- Style classification: test set of 100 images, target ≥ 90% top-1 accuracy
- End-to-end decode confidence: calculate mean confidence score over 100 test images, target ≥ 0.80

### CI/CD (GitHub Actions — existing, extend)
```yaml
on: [push, pull_request]
jobs:
  test:
    - ruff check
    - mypy type check
    - pytest (backend)
    - vitest (frontend)
  e2e:
    - playwright (on staging deploy)
  deploy:
    - vercel deploy (frontend)
    - railway deploy (backend)
    - only on main branch, after all tests pass
```

---

## 10. Open Questions for Balaji

The dev team needs answers to the following before starting Phase 1. Please review and respond.

**Product Scope**
1. Should SJDAS support non-saree textiles (dupattas, furnishing fabrics, menswear)? This affects training data and motif library scope.
2. What is the minimum hook count for your target customers' loom machines? Defines our default export settings.
3. Do target factory customers have existing loom controllers with network connectivity (TCP/IP), or are they all USB-only?

**AI Training Data**
4. Can we use publicly available saree images from Indian e-commerce sites (Nykaa, Taneira, Fab India) to build the YOLOv8 training dataset? Or do we need proprietary images?
5. Do you have access to any existing labeled saree datasets through your DAISE/ISRO network or Ministry of Textiles contacts?

**Platform**
6. Should the web app be SaaS (multi-tenant, cloud) or on-premise install for each factory client?
7. Is there a specific browser requirement? (Chrome-only is fine and simplifies canvas work significantly)
8. Do factory floor users need the full editor, or just decode → export? (Affects Phase 1 scope)

**Business / Legal**
9. Patent filing: has the provisional application for the Screenshot → Decode pipeline been filed? If not, this should happen before Phase 2 ships.
10. What is the target go-live date for the first paying factory client?

**Integrations**
11. Which loom brands are your first clients using? (Determines which export formats to prioritize: Stäubli JC5 vs Udayravi vs Bonas)
12. Should the AI assistant be powered by MiniMax M2.1 (existing) or migrated to a fully open-source LLM (LLaMA 3, Mistral) for zero API cost?

---

## Appendix A: Open Source Library Index

| Library | Version | License | Install | Purpose |
|---|---|---|---|---|
| SAM2 | 2.1 | Apache 2.0 | `pip install sam2` | Segmentation |
| Real-ESRGAN | latest | BSD-3-Clause | `pip install realesrgan` | Upscaling |
| VTracer | 0.6.15 | MIT | `pip install vtracer` | Vectorization |
| CLIP | ViT-B/32 | MIT | `pip install transformers` | Style classification |
| YOLOv8 | 8.x | AGPL-3.0 | `pip install ultralytics` | Motif detection |
| StyleGAN2-ADA | existing | Nvidia | already in repo | Pattern generation |
| Whisper | base | MIT | `pip install openai-whisper` | Voice input |
| ColorThief | latest | MIT | `pip install colorthief` | Palette extraction |
| colour-science | 0.4.4 | BSD-3-Clause | `pip install colour-science` | Pantone matching |
| scikit-learn | 1.4+ | BSD-3-Clause | `pip install scikit-learn` | KMeans clustering |
| scikit-image | 0.22+ | BSD-3-Clause | `pip install scikit-image` | Advanced image ops |
| OpenCV | 4.9+ | Apache 2.0 | already in repo | Image processing |
| ezdxf | 1.3+ | MIT | `pip install ezdxf` | DXF export |
| reportlab | 4.x | BSD-like | `pip install reportlab` | PDF production sheet |
| FastAPI | 0.111+ | MIT | `pip install fastapi` | API framework |
| Celery | 5.x | BSD-3-Clause | `pip install celery` | Task queue |
| SQLAlchemy | 2.x | MIT | `pip install sqlalchemy` | ORM |

---

## Appendix B: Competitor Feature Cross-Reference

For each competitor feature we must match or beat:

| Pointcarré Feature | SJDAS Equivalent | Phase |
|---|---|---|
| Design Maker AI (text → repeat) | AI pattern generation + text prompt | 3 |
| Jacquard Maker (image → BMP) | Screenshot Decode Pipeline | 2 |
| Repeat Maker (straight/half-drop/mirror) | Repeat Engine | 3 |
| Color separation (255 combos) | Color Separation Engine (unlimited) | 2 |
| Layers (non-destructive) | Full layer system | 3 |
| LoomNet (factory distribution) | Factory Monitor + TCP/IP export | 4 |
| Pantone library (5760 colors) | colour-science Pantone matching | 2 |
| Adobe integration | SVG import/export compatible | 3 |
| Portfolio / client presentation | Collections + share link | 4 |

| NedGraphics Feature | SJDAS Equivalent | Phase |
|---|---|---|
| Jacquard CAD/CAM | Weave Builder + BMP export | 1 |
| Float checking | Float Checker (backend) | 2 |
| Machine format conversion | Multi-format export | 4 |
| Real-time fabric simulation | Fabric simulation preview | 3 |
| NEDHub cloud | SJDAS web platform | 1 |
| NEDTag auto-tagging | AI metadata on decode | 2 |
| 3D fabric viewer | 3D drape preview (simplified) | 3 |
| Jacquard Connect SDK | TCP/IP loom bridge | 4 |
| ERP/PLM integration | API + webhook system | 4 |

| WeaverAI Feature | SJDAS Equivalent | Phase |
|---|---|---|
| Moodboard → pattern | Text/image → design via StyleGAN2 | 3 |
| Seamless repeat | Repeat Engine | 3 |
| Color separation (300 DPI) | Color Separation Engine | 2 |
| Jacquard BMP | BMP export (existing + improve) | 1 |
| Virtual try-on | Out of scope (v3) | — |

---

*This document is confidential and intended for the SJDAS development team only.*
*Version 2.0 — March 2026 — Prepared by Balaji Koushik*
*Next review: Phase 1 kickoff meeting*
