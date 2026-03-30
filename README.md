# SJDAS v2.2.0: Stabilized AI Jacquard Designer
**The Definitive Jacquard Design & Cloud AI Synergy (Pilot Ready)**

SJDAS (Smart Jacquard Design Automation System) is an enterprise-grade studio designed to revolutionize the textile manufacturing workflow. By fusing a high-performance PyQt6 desktop core with asynchronous Cloud AI workers, SJDAS enables designers to generate, validate, and export 100% production-ready machine files directly to industrial Jacquard looms with unprecedented speed and precision.

---

## 🛡️ Enterprise Security & Reliability
SJDAS is built for the rigors of modern B2B SaaS environments:
- **Encrypted Synchronization:** All network traffic is secured via industry-standard SSL/TLS (v1.2+) with mandatory verification.
- **Tenant Isolation:** Multi-tenant architecture powered by Supabase RLS (Row Level Security), ensuring absolute data privacy for every factory.
- **Fail-Safe Processing:** Asynchronous Celery workers handle heavy AI computations (SAM2, DreamPaint) in the cloud, keeping the desktop UI responsive.
- **Strict Validation:** Proactive float-checking algorithms prevent costly loom snagging.
- **Definitive Stabilization (v2.2.0):** Achieved **100% Pass Rate** in the comprehensive UI/UX and AI test suite, ensuring crash-free Ribbon navigation and tool execution.
- **Architecture Hardening:** Consolidated 5,000+ lines of experimental code into a verified, signal-robust controller for production-grade reliability.

See the [STABILITY_REPORT.md](STABILITY_REPORT.md) for detailed test results and architectural hardening specifics.

---

## ✨ Core Feature Suite

### 🎨 Screenshot → Design Decode Pipeline
The crown jewel of SJDAS. Upload any photo—even a blurry phone screenshot of a saree or a WhatsApp forward—and SJDAS will:
- **Perspective Correction:** Auto-deskew and correct homography for off-angle photos.
- **AI Segmentation:** Utilize **SAM2 (Segment Anything Model 2)** to isolate body, border, and pallu regions.
- **Vectorization:** Convert raster motifs into clean, editable SVG paths using **VTracer**.
- **Color Separation:** Intelligently reduce 16M colors into a production-ready yarn palette (2–256 colors).

- **Modern Ribbon UI:** High-performance category-based navigation (Home, Design, AI, Textile) for an industry-standard "Photoshop-quality" layout.
- **Asynchronous Canvas Intelligence:** A zero-latency environment with fluid micro-animations and background AI suggestions (Cortex & OmniBar).
- **Hybrid Drafting:** Edit raster pixel grids and vector SVG paths simultaneously on a unified canvas.
- **Stock-Aware Recolor:** Real-time CIEDE2000 Delta-E color matching against physical thread inventory.
- **Autonomous Healing:** AI-powered dust removal and pattern-completion tools strictly optimized for woven textile constraints.

### 🧠 Advanced AI Orchestration
- **SAM 2 Magic Tracer:** Instant, high-fidelity motif extraction and vectorization.
- **Conversational Copilot:** Integrated AI Assistant (powered by MiniMax M2.1) for design suggestions and voice-commanded pattern generation.
- **Pattern Diffusion:** Generate high-resolution, tileable patterns directly within the designer workspace using StyleGAN2-ADA.

### 🏭 Industrial Loom Precision
- **DirectJC5 / Staubli / JC5 / WIF:** Native binary export support for major industrial loom controllers.
- **8-Bit Hardware Compliance:** Strict 8-bit indexed BMP compilation for legacy controller compatibility.
- **High-Hook Density:** Optimized for 600 to 12,000+ hook configurations.

---

## 🏗️ System Architecture
SJDAS follows a hybrid architecture to balance performance and accessibility:
- **Desktop Core (PyQt6):** Low-latency editor and direct hardware communication (Loom TCP/IP bridge).
- **Cloud Backend (FastAPI):** High-power AI processing nodes running SAM2 and Real-ESRGAN.
- **Web Portal (Next.js):** B2B management dashboard for design libraries and factory monitoring.

---

## 🚀 Deployment & Installation

### Desktop Application
1. **Clone & Environment:**
   ```bash
   git clone https://github.com/BalajiKoushik01/SJDAS.git
   cd SJDAS
   # Configure .env based on .env.example
   ```
2. **Standard Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python launcher.py
   ```

### Cloud Services (FastAPI + Next.js)
Detailed deployment guides for the **SJDAS Cloud Portal** (Next.js) and the **Worker Engine** (FastAPI) can be found in the `web/` and `backend/` directories respectively. See [DEPLOYMENT.md](DEPLOYMENT.md) for production orchestration via Docker Compose.

---

## 🧪 Quality Assurance
SJDAS maintains 100% coverage on core geometry and command utilities.
```bash
pytest tests/ --cov=sj_das
```

---

## 🏢 Commercial Support & Licensing
SJDAS is a proprietary software solution. For Enterprise Licensing, Custom Loom Driver Integration, or Priority Support, please contact the SJDAS Professional Services team.

**Authors:** [Balaji Koushik](https://github.com/BalajiKoushik01) & The SJDAS Engineering Team
**GitHub:** [BalajiKoushik01/SJDAS](https://github.com/BalajiKoushik01/SJDAS)

---
*Empowering the world's finest weaving houses with Artificial Intelligence.*
