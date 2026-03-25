# SJDAS — Smart Jacquard Design Automation System
## Product Bible v1.1 — Solo Founder Edition
**Version:** 1.1 | **Date:** March 2026 | **Status:** ACTIVE — Living Document
**Classification:** CONFIDENTIAL — Internal Use Only

---

> **CORE VISION:** If a user uploads a screenshot of a design — often messy — SJDAS automatically decodes every design element, pattern, motif, colour, and structure. It traces and reconstructs the design into a fully editable digital file that designers can refine and send directly to power loom manufacturing. No competitor can do this.

---

## Table of Contents

1. [Executive Summary & Vision](#1-executive-summary--vision)
2. [Competitive Intelligence & Market Analysis](#2-competitive-intelligence--market-analysis)
3. [Core Product Architecture](#3-core-product-architecture)
4. [Tech Stack — End to End](#4-tech-stack--end-to-end)
5. [AI Features & Capabilities — Full Specification](#5-ai-features--capabilities--full-specification)
6. [Screenshot-to-Design Core Feature — Deep Specification](#6-screenshot-to-design-core-feature--deep-specification)
7. [AI Training Dataset Strategy](#7-ai-training-dataset-strategy)
8. [UI/UX Design Language & Premium Interface](#8-uiux-design-language--premium-interface)
9. [Module Breakdown — Web Application](#9-module-breakdown--web-application)
10. [Udayravi & Power Loom Integration — Deep Specification](#10-udayravi--power-loom-integration--deep-specification)
11. [Monetisation & B2B Licensing Model](#11-monetisation--b2b-licensing-model)
12. [Database Schema & Data Architecture](#12-database-schema--data-architecture)
13. [API Architecture](#13-api-architecture)
14. [DevOps, CI/CD & Infrastructure](#14-devops-cicd--infrastructure)
15. [Security & Compliance](#15-security--compliance)
16. [Solo Founder Build Roadmap — Week by Week](#16-solo-founder-build-roadmap--week-by-week)
17. [KPIs & Success Metrics](#17-kpis--success-metrics)
18. [Appendix — File Formats, Motif Taxonomy & Yarn Standards](#18-appendix--file-formats-motif-taxonomy--yarn-standards)

---

## 1. Executive Summary & Vision

### 1.1 What is SJDAS?

SJDAS (Smart Jacquard Design Automation System) is an AI-native, web-first B2B SaaS platform built exclusively for the Indian power loom and Jacquard textile manufacturing industry. It bridges the gap between creative design and physical loom manufacturing by automating the most painful, slow, and error-prone parts of the entire workflow: design interpretation, pattern digitisation, weave structure mapping, and loom file generation.

The platform is built by a solo founder (you), targeting power loom owners and designers in Andhra Pradesh (Nellore, Dharmavaram, Ongole clusters) first, then scaling nationally.

### 1.2 Core Mission

> Transform any design input — a messy phone photo, WhatsApp screenshot, hand-drawn sketch, voice command, or reference image — into a precise, editable, loom-ready digital file in under 60 seconds. Give power loom owners and saree designers a single platform to design, refine, simulate, collaborate, and send to manufacture.

### 1.3 The Problem SJDAS Solves

| Pain Point | Current Reality | SJDAS Solution |
|---|---|---|
| Design digitisation | Designer re-draws reference designs by hand in legacy CAD tools — takes hours/days | Screenshot Decode: upload photo → editable design in 60 seconds |
| Loom file errors | Wrong hook count, colour count, or float length causes expensive re-runs | AI validates design before export. Rejection prediction score. |
| Software complexity | NedGraphics, Pointcarre cost ₹5–15 lakh/year and require training weeks | Premium, intuitive UI. Onboarding in 30 minutes. |
| No mobile access | All legacy tools are Windows desktop-only | PWA — works in Chrome on any device, laptop or phone |
| Language barrier | All tools are English-only | Tamil, Telugu, Hindi interface |
| Disconnected pipeline | Design → USB stick → loom operator → manual file load | Direct machine push via SJDAS Bridge agent |
| No collaboration | Designs emailed as BMP files | Real-time shared canvas, approval workflow |

### 1.4 Primary Target Users

**User 1 — Power Loom Owner (Primary Buyer)**
- Owns 5–100 Jacquard looms in a cluster (Nellore, Dharmavaram, Ongole, Kanchipuram, Varanasi, Surat)
- Currently uses: a combination of legacy Windows CAD software (NedGraphics, Textronic, local tools), USB sticks, and a dedicated design operator
- Pain: design errors cause 2–3 day re-runs, wasted yarn, rejected orders
- Goal: zero-error loom files, faster order turnaround, ability to take more orders
- Will pay: ₹10,000–40,000/month for a platform that provably reduces rejections and speeds up design-to-loom

**User 2 — Saree Designer (Primary Daily User)**
- Creative professional or design department employee
- Currently uses: Photoshop/CorelDraw (non-specialised) or legacy CAD tools
- Pain: translating design intent into loom-compatible files requires technical knowledge they don't have
- Goal: design freely (like Photoshop), export correctly (like a CAD tool), without needing to be a loom engineer
- Will love: screenshot decode (saves hours), AI generation, voice commands, beautiful canvas

**User 3 — Loom Cluster Manager**
- Manages 20–500 looms across a geographic cluster or cooperative
- Pain: no unified view of orders, looms, and design queues
- Goal: production dashboard, order tracking, loom assignment, rejection analytics

### 1.5 What SJDAS Owns That No Competitor Has

1. **Screenshot → Exact Trace Decode** — The only platform that reconstructs any photo/screenshot of a saree design into a fully editable digital file with motifs, zones, colours, and weave assignments. No competitor (TCS, WeaverAI, NedGraphics, or anyone else) has this.
2. **End-to-End Loom File Export** — BMP, Udayravi native format, Staubli, Bonas, Grosse — all generated directly in the browser, no additional software.
3. **Direct Power Loom Machine API** — First Indian SaaS to push design files directly to loom machines over LAN/MQTT via the SJDAS Bridge agent.
4. **Indian Textile DNA in every AI model** — Kanjivaram, Banarasi, Pochampally, Paithani, Jamdani, Dharmavaram motifs, regional colour traditions, saree anatomy (body/border/pallu/endpiece) — baked into every model, not a generic Western tool.
5. **All Competitor Features, Better** — Every feature from TCS, WeaverAI, NedGraphics, Pointcarre, ScotWeave, DigiBunai, WveCAD, and Textronic — implemented with superior UX and mobile-first access.

---

## 2. Competitive Intelligence & Market Analysis

### 2.1 Primary Competitor — TCS Intelligent Design Platform

> **THREAT LEVEL: HIGH — but your window is OPEN.**

TCS launched their Intelligent Design Platform at the AI Impact Summit in February 2026. It is in pilot stage in Kanchipuram and in talks with the Handloom Corporation of India and the Ministry of Textiles. It is **NOT commercially available** as of March 2026. You have a 6–12 month window to capture the market before TCS rolls out.

**What TCS has:**
- Voice command input to generate designs
- Hand sketch → loom-compatible digital format
- 3D visualisation of final saree before weaving
- AR preview of finished fabric
- Reduces design finalisation from days/weeks to minutes
- Government-backed pilot in Kanchipuram

**Where TCS LOSES to SJDAS:**
- No Screenshot Decode / reverse-engineering feature
- Enterprise-only pricing (not accessible to SME loom owners)
- No power loom machine API / direct push
- Handloom focused — not power loom
- Complex enterprise onboarding — SJDAS is 30-minute self-serve
- No production management or order tracking

### 2.2 Full Competitor Matrix

| Competitor | Origin | Key Features | Critical Gaps vs SJDAS |
|---|---|---|---|
| **TCS Intelligent Design Platform** | India (Feb 2026 pilot) | 3D design gen, AR, voice/sketch input, loom export | Not commercial, no screenshot decode, enterprise-only, handloom focus |
| **WeaverAI** (weaverai.in) | India/Singapore | Textile Design Studio, Jacquard BMP gen, colour separation, virtual try-on, fashion draping, browser-based | No screenshot decode, no loom machine API, no production management, no Indian motif intelligence |
| **NedGraphics** (Jacquard + Texcelle) | Netherlands | Industry gold standard — Jacquard CAD, float check, warp/weft scales, weave library, fabric simulation, loom machine export | ₹8–15 lakh/year, Windows desktop only, no AI generation, no screenshot decode, no mobile |
| **Pointcarre** | France | Jacquard/Dobby/Tuft/Carpet, Staubli/Bonas/Itema/Dornier support, AI Jacquard Maker (2025) | Expensive, Western-centric, no Indian motif library, no screenshot decode |
| **ScotWeave** | UK | Jacquard Designer, Artwork Designer, Drape, Presentation, electronic dobby export | Desktop Windows only, no AI, no Indian context |
| **DigiBunai** | India (Govt/MIT Media Lab) | Open source, multi-lingual, Jacquard card punching, digital cloth preview | No AI, no SaaS model, no screenshot decode, poor UX, abandoned |
| **WveCAD** | India | Browser-based Jacquard/Dobby CAD, 256-shaft weave drafts, 3D draping | No AI, no machine export, no screenshot decode |
| **Textronic** | India | Jacquard CAD with machine integration (Bonas, Staubli, Grosse), cast-out facility | Legacy Windows UI, no AI, no SaaS, no mobile |

### 2.3 Feature Ownership — SJDAS vs All Competitors

| Feature | SJDAS | TCS | WeaverAI | NedGraphics | Pointcarre | DigiBunai |
|---|---|---|---|---|---|---|
| Screenshot → Decode | ✅ **UNIQUE** | ❌ | ❌ | ❌ | ❌ | ❌ |
| Voice Command Input | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Hand Sketch → Design | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| AI Pattern Generation | ✅ | Partial | ✅ | ❌ | ✅ | ❌ |
| 3D Fabric Simulation | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| AR Preview | ✅ Ph2 | ✅ | ✅ | ❌ | ❌ | ❌ |
| Colour Separation | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| BMP / Loom Export | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Udayravi Native Format | ✅ **UNIQUE** | ❌ | ❌ | ❌ | ❌ | ❌ |
| Staubli/Bonas/Grosse | ✅ | Unknown | ❌ | ✅ | ✅ | ❌ |
| Direct Machine API Push | ✅ **UNIQUE** | ❌ | ❌ | Partial | ❌ | ❌ |
| Float Checker | ✅ | Unknown | ❌ | ✅ | ✅ | ❌ |
| Yarn Usage Calculator | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Indian Motif Library | ✅ | Partial | ❌ | ❌ | ❌ | Partial |
| Multi-lingual (Tamil/Telugu/Hindi) | ✅ | Unknown | ❌ | ❌ | ❌ | ✅ |
| Real-Time Collaboration | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Production Management | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Rejection Prediction AI | ✅ **UNIQUE** | ❌ | ❌ | ❌ | ❌ | ❌ |
| Browser / Mobile PWA | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| B2B SaaS / Affordable | ✅ | ❌ | Partial | ❌ | ❌ | ❌ |

### 2.4 Market Size & Opportunity

- India has **4.5 million power looms** (as of 2024), concentrated in Surat (Gujarat), Varanasi (UP), Bhiwandi (Maharashtra), Erode/Salem/Kanchipuram (Tamil Nadu), Dharmavaram/Nellore (Andhra Pradesh), Murshidabad (West Bengal)
- Andhra Pradesh alone has ~500,000 power looms — your home market
- The Indian technical textiles and handloom/powerloom software market is estimated at ₹800 crore and growing at 18% CAGR
- Even 0.1% penetration = 4,500 loom factories × ₹15,000/month = ₹6.75 crore MRR

---

## 3. Core Product Architecture

### 3.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER / PWA CLIENT                         │
│         Next.js 14 (App Router) — TypeScript — Tailwind         │
│    Fabric.js Canvas │ Three.js 3D │ Framer Motion Animations    │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS / WebSocket
┌────────────────────────▼────────────────────────────────────────┐
│                     API GATEWAY (Kong)                          │
│         Rate Limiting │ Auth Middleware │ Request Routing        │
└──────┬──────────┬──────────┬──────────┬───────────┬────────────┘
       │          │          │          │           │
  ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌──▼─────┐ ┌──▼──────┐
  │ Design │ │  Auth  │ │ Order  │ │ Collab │ │ Notify  │
  │Service │ │Service │ │Service │ │Service │ │ Service │
  │FastAPI │ │Node.js │ │Node.js │ │Node.js │ │ Node.js │
  │(Python)│ │        │ │        │ │+WS     │ │ +SNS    │
  └────┬───┘ └───┬────┘ └───┬────┘ └──┬─────┘ └──┬──────┘
       │         │          │         │           │
  ┌────▼─────────▼──────────▼─────────▼───────────▼────────┐
  │                   DATA LAYER                             │
  │  PostgreSQL (RDS) │ Redis (Cache) │ S3 (Files)          │
  │  pgvector (AI embeddings) │ Meilisearch (Design Search)  │
  └─────────────────────────────────────────────────────────┘
       │
  ┌────▼───────────────────────────────────────────────────┐
  │              GPU WORKER POOL (Celery + Redis)           │
  │  Screenshot Decode Pipeline │ AI Pattern Generation     │
  │  Motif Detection │ 3D Rendering │ Loom File Export      │
  └────┬───────────────────────────────────────────────────┘
       │
  ┌────▼───────────────────────────────────────────────────┐
  │         SJDAS BRIDGE AGENT (Factory-side)               │
  │  Windows/Linux desktop agent on factory PC              │
  │  Connects looms via TCP/USB Serial/MQTT                 │
  │  Pushes design files, streams telemetry back            │
  └────────────────────────────────────────────────────────┘
```

### 3.2 Key Architectural Decisions & Why

| Decision | Choice | Reason |
|---|---|---|
| Web-first (not desktop) | Next.js PWA | Works on any device in a factory. No installation. Auto-updates. |
| Python for AI services | FastAPI | Best AI/ML ecosystem (PyTorch, OpenCV, HuggingFace). |
| Node.js for business logic | Hono.js | Fast, TypeScript-native, handles real-time WebSocket well. |
| Separate GPU worker pool | Celery + Redis | AI jobs (decode, generation) are slow — must be async. Never block the API. |
| Multi-tenant PostgreSQL | Row-Level Security | Clean data isolation between factories without separate databases. |
| S3 for design files | AWS S3 / MinIO | Design files (BMP, .sjd) can be large. Cheap object storage. On-prem option with MinIO. |
| SJDAS Bridge agent | Lightweight Node.js | Factories often have no public internet. Bridge runs on local PC and tunnels to cloud. |

### 3.3 .SJD — SJDAS Native Design File Format

The `.sjd` format is a JSON-based container for all design data. This is the single source of truth that all modules read and write.

```json
{
  "sjd_version": "1.1",
  "id": "uuid",
  "name": "Kanjivaram Wedding Border v3",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "canvas": {
    "width_px": 4096,
    "height_px": 4096,
    "dpi": 600,
    "hook_count": 2400,
    "weft_count": 1200
  },
  "zones": {
    "body": { "bounds": { "x": 0, "y": 0, "w": 3200, "h": 4096 }, "repeat_x": true, "repeat_y": false },
    "border": { "bounds": { "x": 3200, "y": 0, "w": 400, "h": 4096 }, "repeat_x": false, "repeat_y": true },
    "pallu": { "bounds": { "x": 3600, "y": 0, "w": 496, "h": 4096 }, "repeat_x": false, "repeat_y": false }
  },
  "layers": [
    {
      "id": "uuid",
      "name": "Peacock Motif — Main Body",
      "type": "vector",
      "zone": "body",
      "visible": true,
      "locked": false,
      "data": { "svg_path": "M 100 200 C ...", "x": 120, "y": 340, "scale": 1.0, "rotation": 0 }
    },
    {
      "id": "uuid",
      "name": "Gold Zari — Border",
      "type": "bitmap",
      "zone": "border",
      "visible": true,
      "data": { "s3_key": "designs/uuid/layers/gold_zari.png" }
    }
  ],
  "colour_palette": [
    { "id": "c1", "name": "Deep Crimson", "hex": "#8B0000", "yarn_code": "PANTONE 202 C", "ncs": "S 4550-R", "thread_count_percent": 35 },
    { "id": "c2", "name": "Gold Zari", "hex": "#CFB53B", "yarn_code": "PANTONE 871 C", "thread_count_percent": 20 }
  ],
  "weave_assignments": [
    { "layer_id": "uuid", "weave_type": "satin_8h", "raised": 7, "lowered": 1 },
    { "layer_id": "uuid", "weave_type": "twill_2_2", "raised": 2, "lowered": 2 }
  ],
  "repeat_tile": { "width": 256, "height": 512, "s3_key": "designs/uuid/repeat_tile.png" },
  "metadata": {
    "style": "Kanjivaram",
    "region": "Tamil Nadu",
    "occasion": "Wedding",
    "ai_decoded": true,
    "decode_confidence": 0.91,
    "tags": ["peacock", "gold-zari", "border", "traditional"]
  },
  "loom_config": {
    "target_machine": "udayravi",
    "hook_count": 2400,
    "colour_count": 12,
    "float_max": 8,
    "validated": true,
    "validation_score": 97
  }
}
```

---

## 4. Tech Stack — End to End

### 4.1 Frontend Stack

| Concern | Technology | Version | Notes |
|---|---|---|---|
| Framework | Next.js (App Router) | 14.x | Server components, ISR, streaming |
| Language | TypeScript | 5.x | Strict mode. No `any`. |
| Canvas Engine | Fabric.js | 6.x | Primary design canvas — pixel + vector hybrid |
| Vector Layer | Konva.js | 9.x | High-perf layer compositing on top of Fabric |
| 3D Engine | Three.js | r165 | Fabric simulation, drape preview |
| Animation | Framer Motion | 11.x | Page transitions, micro-interactions, loading |
| State (client) | Zustand | 4.x | Design canvas state, tool state, UI state |
| State (server) | TanStack Query | 5.x | API data fetching, caching, background refresh |
| Styling | Tailwind CSS | 3.x | Utility-first. Custom design tokens via CSS vars. |
| Component Base | shadcn/ui | latest | Radix primitives, fully customised on top |
| Real-Time | Socket.io client | 4.x | Collaborative canvas, live loom telemetry |
| File Upload | react-dropzone | 14.x | Drag-and-drop screenshot/image upload |
| i18n | next-intl | 3.x | English, Tamil, Telugu, Hindi |
| PWA | next-pwa | 5.x | Offline capability, installable |
| Forms | React Hook Form + Zod | latest | Validated forms throughout |
| Charts | Recharts | 2.x | Analytics dashboards |
| PDF (client) | react-pdf | 7.x | Design spec sheet preview |
| Testing (unit) | Jest + RTL | latest | Component and hook tests |
| Testing (E2E) | Playwright | latest | Full user flow tests |

### 4.2 Backend — AI & Design Processing (Python)

| Concern | Technology | Version | Notes |
|---|---|---|---|
| Framework | FastAPI | 0.111+ | Async, auto OpenAPI docs |
| AI Runtime | PyTorch | 2.3+ | All model inference |
| Image Processing | OpenCV | 4.9+ | Contour detection, Hough transforms, preprocessing |
| Segmentation (region) | Segment Anything Model (SAM) v2 | Meta | Isolates saree from background, zones detection |
| Motif Detection | YOLOv8 | Ultralytics | Fine-tuned on Indian textile motif dataset |
| Super Resolution | BSRGAN / Real-ESRGAN | — | Upscale low-res photos before decode |
| Pattern Generation | Stable Diffusion XL | 1.0 | Fine-tuned on textile dataset. ControlNet for sketch input. |
| Style Transfer | ip-adapter | — | Apply reference image style to design |
| Voice Input | OpenAI Whisper | large-v3 | Tamil, Telugu, Hindi, English |
| OCR | EasyOCR + Tesseract | — | Text in design images, label reading |
| Vector Tracing | potrace (Python binding) | — | Bitmap → SVG clean vector outline |
| Bezier Fitting | scipy + custom engine | — | Smooth Bezier curves from contour points |
| Colour Analysis | scikit-learn (KMeans) | — | Palette extraction, colour clustering |
| Colour Matching | colormath | — | Delta-E matching to Pantone/NCS/yarn codes |
| Weave Inference | Custom CNN | — | Infers weave structure from image texture |
| Float Checker | Custom rule engine | — | Validates float length against loom constraints |
| Background Tasks | Celery | 5.x | Async AI job queue |
| Task Broker | Redis | 7.x | Celery broker + result backend |
| HTTP Client | httpx | — | Internal service calls |
| Data Validation | Pydantic v2 | — | Request/response schemas |
| Testing | pytest + pytest-asyncio | — | AI pipeline unit + integration tests |

### 4.3 Backend — Business Logic (Node.js)

| Concern | Technology | Version | Notes |
|---|---|---|---|
| Framework | Hono.js | 4.x | Fast, TypeScript-native, runs on Node + Edge |
| Language | TypeScript | 5.x | Strict mode |
| ORM | Prisma | 5.x | Type-safe PostgreSQL queries |
| Auth | JWT + bcrypt | — | Access (15min) + refresh (30d) tokens, httpOnly cookies |
| OAuth | better-auth | — | Google SSO for enterprise accounts |
| Real-Time | Socket.io server | 4.x | Canvas collaboration, loom telemetry |
| Queue | BullMQ | 4.x | Export jobs, notifications, email |
| Email | Resend | — | Transactional email (simple, generous free tier) |
| SMS | Twilio | — | Order alerts, loom error notifications |
| File Storage | AWS SDK v3 | — | S3 operations |
| PDF Gen | Puppeteer | — | Design spec sheet PDFs |
| Validation | Zod | 3.x | All request schemas |
| Testing | Vitest | — | Unit tests |

### 4.4 Data Layer

| Store | Technology | Use Case |
|---|---|---|
| Primary DB | PostgreSQL 15 (AWS RDS) | All structured data: users, designs, orders, tenants |
| Cache | Redis 7 (ElastiCache) | Sessions, collab state, job queues, rate limiting |
| Object Storage | AWS S3 / MinIO (on-prem) | BMP files, .sjd files, thumbnails, exports, uploads |
| Search | Meilisearch | Design library search: motif names, tags, colours, region |
| Vector Store | pgvector (PostgreSQL ext.) | AI similarity search over design embeddings |
| Time-Series | InfluxDB / TimescaleDB | Loom machine telemetry: RPM, job status, metres |

### 4.5 Infrastructure & Cloud

| Concern | Technology | Notes |
|---|---|---|
| Cloud | AWS ap-south-1 (Mumbai) | Lowest latency for India. Data residency compliance. |
| Containers | Docker + ECS Fargate | Serverless containers. No server management. Solo-friendly. |
| GPU Workers | AWS EC2 G4dn.xlarge | NVIDIA T4 GPU. Auto-scaling group. ~₹2/hour spot instances. |
| CDN | AWS CloudFront | Static assets, thumbnails, design previews |
| IaC | Terraform | All infra as code. Reproducible environments. |
| CI/CD | GitHub Actions | Auto-deploy on push. Full pipeline. Free for solo. |
| Monitoring | Grafana Cloud (free tier) + Sentry | APM, error tracking. Free until scale. |
| Secrets | AWS Secrets Manager | API keys, DB credentials |
| DNS + SSL | Route 53 + ACM | Auto-renewing TLS certificates |
| On-Prem Option | Docker Compose | For factories with no internet. MinIO replaces S3. SQLite option. |
| Dev Environment | Docker Compose (local) | One `docker compose up` to run full stack locally |

### 4.6 Solo Founder — Managed Services to Avoid Building Yourself

These services replace entire engineering teams. Use them:

| What | Service | Monthly Cost Est. |
|---|---|---|
| Payments & Billing | Stripe (subscriptions, invoicing) | 2.9% + ₹2/transaction |
| Email delivery | Resend | Free up to 3,000/month |
| Error tracking | Sentry | Free up to 5K errors/month |
| Monitoring | Grafana Cloud | Free up to 10K metrics |
| Feature flags | Flagsmith (open source, self-host) | Free |
| Customer support | Crisp.chat | Free tier available |
| Auth (if you want faster) | Clerk or Auth.js | Clerk: $25/month |
| Search | Meilisearch Cloud | $30/month (or self-host free) |
| Loom Bridge update delivery | GitHub Releases | Free |

---

## 5. AI Features & Capabilities — Full Specification

### AI Feature 1 — Screenshot & Photo Design Decoder ⭐ CORE DIFFERENTIATOR
*Full pipeline specification in Section 6*

### AI Feature 2 — AI Pattern Generation

**What it does:** Generate new saree/textile designs from text prompts, sketches, or reference images.

**Model:** Stable Diffusion XL 1.0, fine-tuned on SJDAS textile dataset (see Section 7). ControlNet conditioning for structural guidance from user sketches.

**Input modes:**
- Text prompt: `"peacock motif Kanjivaram border, gold zari on deep crimson, traditional South Indian"`
- Reference image upload: generate in the style of the reference
- Rough sketch: draw basic shapes on canvas → AI fills in detailed design
- Existing design: generate N variations with colour, scale, or motif changes

**Output:** High-resolution tileable pattern at minimum 600 DPI, colour-separated into yarn layers, ready for weave assignment.

**Generation parameters exposed to user:**
- Style: Traditional / Contemporary / Fusion / Geometric / Floral
- Region: Kanjivaram / Banarasi / Pochampally / Paithani / Dharmavaram / Custom
- Colour mood: Bridal / Festival / Casual / Pastel / Monochrome
- Complexity: Simple (5–8 colours) / Medium (8–16) / Rich (16–32)
- Repeat type: Half-drop / Full-drop / Mirror / Brick

**Prompt intelligence:** AI auto-enriches the user's prompt with textile-specific terms. `"lotus border"` becomes `"lotus motif Jacquard border repeat, separated colour layers, warp-faced satin weave, high contrast, 600 DPI tileable"` before hitting the model.

### AI Feature 3 — Intelligent Motif Recognition & Library Matching

**What it does:** Upload or paste any design image — AI identifies every motif present.

**Model:** YOLOv8 fine-tuned on Indian textile motif dataset.

**Detects:** Peacock (mayura), Mango/Paisley (kalga/keri), Lotus (kamal), Temple border (gopuram), Chakra, Vine/Creeper (bel), Elephant (hathi), Parrot (tota), Fish (meen), Dancing figure (nataraj), Geometric (diamond, hexagon, chevron), Zari line patterns, Butis (scattered small motifs)

**Output per detected motif:**
- Bounding box on canvas
- Motif name + regional attribution
- Confidence score (0–100%)
- Matched entry in SJDAS Motif Library (if found)
- Similar motifs from library (similarity search via pgvector embeddings)

**Library:** 10,000+ catalogued Indian textile motifs. Each entry has: SVG version, region, style category, historical context, common weave pairings.

### AI Feature 4 — Auto Segmentation (Saree Anatomy)

**What it does:** Detects and separates the standard saree structure automatically.

**Zones detected:**
- `body` (main fabric repeat area, warp direction)
- `border` (kinnam — left and right side borders)
- `pallu` (decorative end piece)
- `endpiece` (narrower end on opposite side)
- `blouse_piece` (if present in the design)

**Model:** Fine-tuned U-Net on annotated saree images.

**After segmentation:** Each zone is an independent, lockable layer. Edit the border colour without touching the body. Swap pallu designs while keeping the body intact. Export zones separately to different loom configurations.

### AI Feature 5 — Weave Structure AI Advisor

**What it does:** Analyses the design and recommends the optimal weave structure for each region.

**Weave types in the library:**
- Plain weave (tabby)
- Twill: 2/2, 3/1, 3/3, herringbone
- Satin: 4H, 5H, 8H (warp-faced and weft-faced)
- Jacquard compound weave
- Dobby patterns
- Custom structures (user-defined binary matrix)

**AI recommendations include:**
- Optimal weave per design region (solid fill → satin, detailed motif → Jacquard, texture → twill)
- Manufacturability score: how easy/expensive to weave on the target loom type
- Float check: flags any weave+design combination that creates floats longer than the configured max
- Yarn usage estimate: metres of each colour yarn required per metre of fabric
- Auto-fix: one click to apply AI's recommended fixes for float violations

### AI Feature 6 — Colour Intelligence

**What it does:** Everything colour — from extraction to yarn matching to trend suggestions.

**Sub-features:**
- **Palette extraction:** K-means clustering extracts dominant colours from any uploaded image
- **Yarn colour matching:** Maps extracted hex values to the nearest physical yarn colour (Pantone NTX Textile, NCS, Indian dye batch codes)
- **Colour reduction for loom:** Automatically reduces palette to loom-feasible count (2–256 colours) while preserving design intent. Uses perceptual colour distance (Delta-E 2000) for best quality.
- **Colour harmony generator:** Given a base colour, suggest complementary, analogous, triadic, split-complementary palettes — shown as yarn swatches
- **Seasonal trend overlay:** Integrates with WGSN/Pantone trend data API to suggest commercially relevant colour stories

### AI Feature 7 — Voice Command Interface

**What it does:** Designer speaks → canvas changes. Multi-lingual.

**Model:** OpenAI Whisper large-v3 (self-hosted on GPU worker)

**Languages:** English, Tamil (தமிழ்), Telugu (తెలుగు), Hindi (हिन्दी)

**Sample commands and what they do:**

| Voice Command | Action |
|---|---|
| "Add a peacock motif to the border" | Detects zone, places nearest peacock motif from library |
| "Change the body colour to deep indigo" | Applies colour change to body zone layer |
| "Generate 3 variations of this pallu" | Triggers variation generation for pallu zone |
| "Reduce to 8 colours for the loom" | Runs colour reduction to 8 colours |
| "Check if this design is loom ready" | Triggers validation pipeline |
| "Export to Udayravi format" | Initiates Udayravi BMP export |
| "Increase the repeat tile by 20 percent" | Scales repeat tile |

**All voice actions are undoable.** Voice commands are transcribed and shown in the command log panel so users can review what was understood.

### AI Feature 8 — Design Quality & Rejection Prediction

**What it does:** Before export, predicts whether the design will cause a loom rejection or quality failure in production.

**Validation checks run:**
1. Hook count: does the design fit within the loom's hook capacity?
2. Colour count: does the palette exceed the loom's supported colour count?
3. Float violations: are any floats longer than the configured maximum?
4. Minimum thread detail: is any motif detail too fine for the current DPI/hook density?
5. Colour registration: are adjacent colour boundaries clean enough to avoid bleeding?
6. Repeat continuity: does the repeat tile join seamlessly without visible seams?
7. Warp tension balance: is the weave structure balanced to avoid fabric distortion?

**Output:**
- Overall Loom Readiness Score: 0–100
- Per-issue severity: Critical (will fail) / Warning (may cause quality issues) / Info (minor)
- Visual overlay on canvas highlighting problem areas
- Auto-fix button for each correctable issue
- Estimated rejection probability: `"Based on this design profile, looms in your cluster reject ~8% of similar designs. This design scores LOW RISK."`

### AI Feature 9 — Conversational AI Design Assistant

**What it does:** A knowledgeable textile AI assistant built into the sidebar.

**Powered by:** Claude API (Anthropic) — the best model for nuanced, context-aware responses about complex domains.

**System prompt context includes:** SJDAS platform knowledge, Indian textile tradition knowledge, the user's current design state (design name, zones, colours, weave assignments, loom config), the user's factory type and cluster.

**Sample interactions:**

> User: "What weave is best for a silk Kanjivaram pallu with heavy zari?"
> AI: "For a Kanjivaram pallu with heavy zari, 8-harness satin (warp-faced) is the traditional choice. The long floats create the characteristic sheen and allow the zari thread to show prominently on the face. Set your raised count to 7 and lowered to 1. Watch your float limit — keep it under 8mm for stability. Want me to apply 8H satin to your pallu zone now?"

> User: "How many hooks do I need for this border design?"
> AI: "Looking at your current border design — it's 400 pixels wide at 600 DPI with 12 distinct colour separations. You'll need approximately 1,400 hooks for the border alone. Your current Udayravi loom config is set to 2,400 total hooks, so you have plenty of headroom."

### AI Feature 10 — 3D Fabric Simulation

**What it does:** Real-time 3D rendering of the designed fabric with physically accurate material behaviour.

**Tech:** Three.js (WebGL) with custom physically-based rendering (PBR) shader. Thread interlacement simulation based on weave structure.

**View modes:**
- **Flat lay:** Design viewed flat, like a scan — good for checking repeat and colour
- **Draped:** Fabric draped over a 3D form — shows how colours interact at folds
- **Saree on mannequin:** Full 9-metre saree simulation wrapped on a 3D mannequin figure
- **AR preview (Phase 2):** Use mobile camera to overlay designed saree on a real person

**Yarn materials available:** Silk (Mulberry, Tussar), Cotton, Polyester, Blended, Zari (gold/silver metallic)

**Lighting presets:** Natural daylight, indoor showroom, wedding venue (warm), stage lighting

### AI Feature 11 — Trend Intelligence Module

**What it does:** Monitors what's selling and trending so your customers' designs are commercially relevant.

**Data sources:**
- Pantone Color Institute seasonal reports
- WGSN trend API (if subscribed)
- Pinterest trend scraping (visual similarity clustering)
- SJDAS platform-wide analytics: which design styles, motifs, and colour combinations lead to highest order completion rates

**Features:**
- "Trending Now" motif and colour panel on dashboard, updated weekly
- "Design Score" for any design: how well it aligns with current market trends
- Seasonal suggestions: "Wedding season (Nov–Feb) is coming — trending: heavy zari, deep red, peacock motifs"
- Factory analytics: your designs vs. platform benchmarks — rejection rate, order volume, design-to-loom time

---

## 6. Screenshot-to-Design Core Feature — Deep Specification

### 6.1 Why This Feature Wins the Market

Every loom factory in India has:
- WhatsApp groups full of blurry reference design photos
- Stacks of old design cards and paper printouts
- Screenshots from Instagram and Pinterest
- Photos taken in rival factories or at trade exhibitions

Right now, a design operator spends 4–8 hours manually re-drawing each of these in legacy CAD software. SJDAS reduces this to 60 seconds. This single feature, demoed to a factory owner, closes the sale.

### 6.2 The Full AI Pipeline — 10 Steps

```
User uploads image
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 1: IMAGE PRE-PROCESSING                                      │
│ Input: Any image (JPG, PNG, HEIC, PDF, WebP)                     │
│ - Auto white balance + exposure correction (OpenCV)              │
│ - Denoising: Non-local means denoising                           │
│ - Super-resolution: BSRGAN upscale to minimum 2000×2000px        │
│ - Perspective correction: detect and dewarp if fabric is skewed  │
│ - Compression artefact removal: JPEG block removal               │
│ Output: Clean, high-resolution normalised image                   │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 2: BACKGROUND REMOVAL & FABRIC ISOLATION                     │
│ Model: SAM v2 (Segment Anything Model — Meta)                    │
│ - Detects and masks out: mannequin/body, hands, background,      │
│   hangers, shadow, table surface, photographer's watermark       │
│ - Extracts clean fabric region only                               │
│ Output: Masked fabric image with transparent background           │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 3: SAREE ANATOMY SEGMENTATION                                │
│ Model: Fine-tuned U-Net on 5,000 annotated saree images          │
│ - Detects and segments: body, border (left/right), pallu,        │
│   endpiece, blouse piece                                         │
│ - Each zone is assigned a bounding polygon                        │
│ Output: Zone map with labelled regions                            │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 4: MOTIF DETECTION                                           │
│ Model: YOLOv8 fine-tuned on Indian textile motif dataset         │
│ - Detects all motif instances with bounding boxes                │
│ - Classifies motif type (peacock, mango, lotus, temple, etc.)    │
│ - Identifies repeating instances — marks as "repeat pattern"     │
│ - Confidence score per detection                                  │
│ Output: List of detected motifs with positions, types, confidence │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 5: CONTOUR TRACING & VECTORISATION                           │
│ Tools: OpenCV (findContours) → potrace → custom Bezier fitter    │
│ - Extracts pixel outline of each detected motif                  │
│ - Applies Douglas-Peucker simplification to reduce noise         │
│ - Fits smooth Bezier curves through contour points               │
│ - Generates clean SVG path data for each motif                    │
│ Output: SVG vector representation of every motif                  │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 6: REPEAT PATTERN ANALYSIS                                   │
│ Tools: NumPy FFT + custom pattern correlation engine             │
│ - Fourier transform identifies spatial frequency of repeats      │
│ - Detects repeat period in warp and weft directions              │
│ - Extracts the minimal repeat tile                               │
│ - Tests for half-drop, full-drop, mirror, brick repeat types     │
│ Output: Repeat tile image + repeat type + period (px and mm)     │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 7: COLOUR EXTRACTION & YARN MATCHING                         │
│ Tools: scikit-learn KMeans + colormath Delta-E matching          │
│ - K-means clustering extracts dominant palette (auto k selection)│
│ - Segments image into per-colour regions (colour flood fill)     │
│ - Maps each colour to nearest yarn code (Pantone NTX, NCS)      │
│ - Creates one thread colour layer per distinct colour            │
│ Output: Colour palette + yarn codes + per-colour layer masks     │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 8: WEAVE STRUCTURE INFERENCE                                  │
│ Model: Custom CNN trained on weave texture images                │
│ - Analyses texture micro-structure in the source image           │
│ - Classifies into: plain, twill, satin, jacquard, dobby          │
│ - Assigns inferred weave as default to each zone                 │
│ Output: Per-zone weave type assignment (fully editable)          │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 9: .SJD DESIGN FILE ASSEMBLY                                 │
│ - Assembles all extracted data into .sjd JSON format             │
│ - Creates canvas layers: vector motifs + colour regions + zones  │
│ - Attaches repeat tile, colour palette, weave assignments        │
│ - Stores all assets to S3                                        │
│ Output: Complete .sjd file — opens directly in canvas editor     │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│ STEP 10: VALIDATION & CONFIDENCE REPORT                           │
│ - Runs loom readiness validation (Section 5, Feature 8)          │
│ - Generates confidence report: per-element detection scores      │
│ - Highlights low-confidence regions on canvas (orange overlay)   │
│ - Flags any loom issues found in the decoded design              │
│ Output: Confidence report PDF + validated .sjd file              │
└───────────────────────────────────────────────────────────────────┘
        │
        ▼
   Canvas Editor opens with decoded design
   Original image shown side-by-side for reference
   Designer can edit, accept, or request re-decode
```

### 6.3 Supported Input Formats

| Format | Notes |
|---|---|
| JPEG / JPG | Most common. SJDAS handles heavy JPEG compression artefacts. |
| PNG | Clean transparency supported. |
| WebP | Modern web format, common in screenshots. |
| HEIC / HEIF | iPhone native format. Auto-converted to PNG before processing. |
| PDF | Scanned design cards, trade catalogues. Page selection UI shown. |
| WhatsApp-compressed images | Super-resolution step specifically handles WhatsApp's 70% JPEG compression. |
| Low-resolution (min 300×300px) | BSRGAN upscaling applied first. |
| Batch upload | Up to 20 images processed simultaneously. Results shown in gallery. |

### 6.4 Performance Targets

| Metric | Target |
|---|---|
| Total decode time (standard 1080p image, GPU) | < 45 seconds |
| Total decode time (4K image, GPU) | < 90 seconds |
| Motif detection accuracy (standard test set) | > 88% mAP@0.5 |
| Colour extraction accuracy (Delta-E vs ground truth) | Delta-E < 5 (perceptually similar) |
| Zone segmentation IoU | > 0.82 |
| Repeat pattern detection accuracy | > 90% |
| False positive motif rate | < 8% |

### 6.5 Edge Cases & Handling

| Edge Case | Handling |
|---|---|
| No clear repeat pattern (unique design) | Marks full image as single tile, no repeat applied |
| Very low contrast image | Enhances contrast (CLAHE) before processing; warns user in confidence report |
| Design on a person (worn saree photo) | SAM removes body/background, processes fabric only; confidence warning shown |
| Mixed design styles (e.g. modern + traditional) | Processes all elements; user manually corrects zone assignments |
| Non-saree textile (dupatta, lehenga, shirt fabric) | Segmentation still works; zone labels auto-adjusted; user can override |
| Image with text / watermarks overlaid | OCR detects and masks text before processing; text extracted separately |
| Heavily crumpled/folded fabric photo | Perspective correction + elastic morphological correction applied; low confidence warning |

---

## 7. AI Training Dataset Strategy

### 7.1 Overview

As a solo founder, building a training dataset is one of your biggest moats. No competitor has a large, labelled Indian textile image dataset. Every image you collect and label is a permanent competitive advantage.

### 7.2 Dataset Sources — What You Already Have + What to Get

#### Source 1: Your Existing Design Images (Immediate)
- Export all existing design files from your current SJDAS desktop app
- These are already structured (BMP files, design metadata)
- Estimated: 500–2,000 images
- **Action:** Write a script to export all existing BMP designs with metadata (hook count, weave type, colour count) as training pairs

#### Source 2: Factory Collection (Months 1–3)
- Visit 5–10 Nellore/Dharmavaram factories you're targeting as customers
- Offer: free 6-month platform access in exchange for design archive access
- What to collect: design BMP files, photos of finished fabrics, design cards
- **Target:** 5,000+ designs from 10 factories = massive head start
- **Label exchange:** factories identify motif names, regions, weave types — they know their designs

#### Source 3: Public Datasets (Immediate)
- **Kaggle — Saree Dataset:** Search "saree dataset", "textile pattern dataset", "Indian fabric"
- **DTD (Describable Textures Dataset):** 5,640 images, 47 texture categories — good for weave inference training
- **FashionNet / DeepFashion:** Contains saree images with some segmentation
- **iMaterialist (Google/Kaggle):** Textile/garment classification dataset
- **IITB Saari Dataset:** Academic Indian textile classification dataset
- **Wikimedia Commons:** Hundreds of high-quality saree images under Creative Commons

#### Source 4: Web Scraping (Months 1–2)
- **Taneira, Nalli, Kanjivaram Silk House, Pothys** product pages — scrape product images with metadata (style name, region, occasion)
- **IndiaMART, TradeIndia** — supplier product listings with fabric photos
- **Pinterest boards** — "Kanjivaram saree", "Banarasi design", "saree border pattern"
- **Instagram** — search textile/loom hashtags (#sareedesign, #kanjivaram, #banarasi, etc.)
- **Legal note:** Use for AI training under fair use/research doctrine. Do not republish raw scraped content.

#### Source 5: Synthetic Data Generation (Months 3–6)
- Once you have initial model running, use it to generate synthetic training data
- Generate 10,000 synthetic saree designs with Stable Diffusion
- Auto-label with the model, manually review 10% sample
- This is a data flywheel: model trains on real data → generates synthetic → synthetic improves model

### 7.3 Labelling Strategy

You cannot label 50,000 images alone. Here is the strategy:

#### Auto-labelling (Free)
- Use pretrained COCO/ImageNet models to auto-label bounding boxes (imperfect but good starting point)
- Use colour histograms to auto-label dominant colours
- Use existing weave classification papers' models as pseudo-labellers

#### Crowd-labelling (Low Cost)
- **Scale AI / Labelbox** — professional annotation. ~$0.05–0.20 per bounding box. For 10,000 images × 5 motifs each = ~₹25,000–100,000
- **Local art students** — hire 2–3 textile design students from ANITS or GITAM (Vizag/Nellore) as part-time annotators. ₹10,000/month each. They understand motif names in Telugu/regional terms.
- **Factory staff** — include a "label this motif" step in the SJDAS onboarding for beta customers. Gamified: earn credit for annotations.

#### Labelling Format
Use COCO JSON format for object detection, VOC XML for segmentation. Use Label Studio (open source, self-hosted) as the labelling tool.

### 7.4 Minimum Dataset Requirements Per Model

| Model | Minimum Training Images | Target |
|---|---|---|
| Motif detection (YOLOv8) | 2,000 labelled images with bounding boxes | 15,000+ |
| Zone segmentation (U-Net) | 500 annotated saree images with zone masks | 5,000+ |
| Weave inference CNN | 1,000 weave texture crops (10 weave types × 100) | 5,000+ |
| Pattern generation (SDXL fine-tune) | 5,000 high-quality design images | 50,000+ |
| Style classification | 500 images per style (10 styles) | 2,000+ per style |

### 7.5 Dataset Version Control

- Store all training data in S3 with versioned prefixes: `s3://sjdas-ml/datasets/v1/`, `v2/`, etc.
- Track dataset versions in DVC (Data Version Control) linked to GitHub repo
- Never overwrite — always append new data to new version
- Keep a held-out test set (10%) that is NEVER used in training — only for evaluation

---

## 8. UI/UX Design Language & Premium Interface

### 8.1 Design Philosophy

SJDAS must feel like three things at once:
1. **A professional tool** — as precise and powerful as Figma or Adobe Illustrator
2. **Indian craft heritage** — warm, rich, rooted in the aesthetic of the textiles it serves
3. **Consumer-grade simplicity** — a factory owner with no design background can use it in 30 minutes

The design language is called **"Silk & Steel"** — the warmth and richness of silk combined with the precision and trust of engineering steel.

### 8.2 Design Tokens

```css
/* Colours */
--color-brand-navy:      #1E3A5F;  /* Primary — trust, precision */
--color-brand-crimson:   #C0392B;  /* Action — CTA buttons, alerts */
--color-brand-gold:      #9A7B20;  /* Heritage — decorative, celebration */
--color-brand-jade:      #1A6B3C;  /* Success states */
--color-surface-base:    #F7F9FD;  /* App background */
--color-surface-raised:  #FFFFFF;  /* Cards, panels */
--color-surface-overlay: #EAF0FB;  /* Hover, selected states */
--color-border-subtle:   #D5DCE8;  /* Dividers, input borders */
--color-text-primary:    #1A1A2E;  /* Body text */
--color-text-secondary:  #64748B;  /* Labels, metadata */
--color-text-disabled:   #94A3B8;  /* Disabled states */

/* Typography */
--font-sans:   'Inter', system-ui, sans-serif;     /* UI text */
--font-mono:   'IBM Plex Mono', monospace;          /* Codes, export data */
--font-devanagari: 'Noto Sans', sans-serif;         /* Hindi */
--font-tamil:  'Noto Sans Tamil', sans-serif;       /* Tamil */
--font-telugu: 'Noto Sans Telugu', sans-serif;      /* Telugu */

/* Type Scale */
--text-xs:  11px;   /* Metadata, badges */
--text-sm:  13px;   /* Labels, captions */
--text-base: 15px;  /* Body text */
--text-lg:  17px;   /* Section headers */
--text-xl:  21px;   /* Panel titles */
--text-2xl: 27px;   /* Page titles */
--text-3xl: 34px;   /* Hero headings */

/* Spacing */
--space-1: 4px;   --space-2: 8px;   --space-3: 12px;
--space-4: 16px;  --space-5: 20px;  --space-6: 24px;
--space-8: 32px;  --space-10: 40px; --space-12: 48px;
--space-16: 64px; --space-20: 80px;

/* Border Radius */
--radius-sm:  4px;   /* Inputs, tags */
--radius-md:  8px;   /* Cards, buttons */
--radius-lg:  12px;  /* Modals, drawers */
--radius-xl:  20px;  /* Chips, badges */
--radius-full: 9999px; /* Pills, avatars */

/* Shadows */
--shadow-sm:  0 1px 3px rgba(30,58,95,0.08);      /* Interactive elements */
--shadow-md:  0 4px 12px rgba(30,58,95,0.10);     /* Cards */
--shadow-lg:  0 8px 24px rgba(30,58,95,0.14);     /* Modals */
--shadow-xl:  0 16px 48px rgba(30,58,95,0.18);    /* Drawers, floating panels */

/* Animation */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* Playful spring */
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);      /* Smooth transitions */
--duration-fast:   120ms;
--duration-normal: 240ms;
--duration-slow:   400ms;
```

### 8.3 Animation System

| Element | Animation | Details |
|---|---|---|
| Page transitions | Shared element transitions | Framer Motion layoutId. Design card expands to canvas. |
| App loading | Saree-weave skeleton | Animated thread lines weaving across skeleton cards. |
| AI processing overlay | Neural pulse on canvas | Blue pulsing rings emanating from upload zone while AI runs. |
| Progress steps | Staggered reveal | Each decode step (Pre-process → Detect → Trace → …) reveals with 80ms stagger. |
| Canvas tool switch | Spring scale | Tool icons spring-scale (1.0 → 1.15 → 1.0) on select. |
| Colour swatch select | Elastic bounce | Swatch scales up with spring easing, shows yarn code tooltip. |
| Notification toast | Slide + fade | Slides in from bottom-right, progress bar auto-dismiss. |
| Export success | Silk ripple | Concentric elliptical ripple (fabric wave) from export button. |
| Loom status — active | Subtle pulse ring | Green pulse ring around active loom card. |
| Collaborative cursor | Interpolated follow | Other users' cursors follow path with 60ms lag for smoothness. |
| 3D preview load | Fabric unroll | 3D mesh unrolls from top-left corner on first load. |
| Modal open | Scale + blur backdrop | Modal scales from 0.95 → 1.0 with background blur-in. |
| Drag-and-drop zone | Dashed border inflate | Dashed border expands + colour shifts on drag-over. |

### 8.4 Screen-by-Screen Layout Specification

#### Screen 1 — Dashboard (Home)

```
┌────────────────────────────────────────────────────────────────┐
│ [SJDAS logo]    [Workspace: Nellore Factory ▼]  [🔔] [Avatar] │  ← Top Nav
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         📸  Drop a design here to decode it              │ │  ← Hero decode zone
│  │     Or paste a screenshot (Ctrl+V works too!)            │ │    Animated dashed border
│  │            [Browse Files]  [Use Camera]                  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  RECENT DESIGNS                              [+ New Design]   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ [thumb]  │  │ [thumb]  │  │ [thumb]  │  │ [thumb]  │      │  ← Design cards grid
│  │ Wedding  │  │ Buti     │  │ Festival │  │ Temple   │      │
│  │ Border   │  │ Repeat   │  │ Pallu    │  │ Border   │      │
│  │ 2h ago   │  │ Yesterday│  │ 3d ago   │  │ 1w ago   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│                                                                │
│  ┌─────────────────────────────────┐  ┌──────────────────┐   │
│  │  🏭 PRODUCTION QUEUE (3 active) │  │ 📈 TREND PULSE   │   │  ← Split bottom
│  │  › Wedding Border → Loom #3     │  │ Trending: Peacock│   │
│  │    ████████░░░░ 68% — 4h left   │  │ Colour: #8B0000  │   │
│  │  › Temple Pallu → Loom #7       │  │ Region: Kanchi   │   │
│  │    ██░░░░░░░░░░ 12% — est 18h   │  │ [View Full Report│   │
│  └─────────────────────────────────┘  └──────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

#### Screen 2 — Design Canvas (Core Workspace)

```
┌──────────────────────────────────────────────────────────────────────┐
│ ← Dashboard  │  Wedding Border v3.sjd  │  🤝 Live (2 users)  │  [Export] │  ← Top bar
├──┬──────────────────────────────────────────────────────────┬────────┤
│  │ Body  │ Border  │ Pallu  │ Endpiece               [+zone]│        │  ← Zone tabs
│T │────────────────────────────────────────────────────────  │ PROPS  │
│O │                                                          │ PANEL  │
│O │                  C A N V A S                             │        │
│L │                                                          │ Layer: │
│B │         [ZOOM: 80%]  [GRID: ON]  [REPEAT: ON]           │ Gold   │
│A │                                                          │ Zari   │
│R │                                                          │ ──────│
│  │                                                          │ Weave: │
│▸ │                                                          │ Satin  │
│  │                                                          │ 8H ▾  │
│  │                                                          │ ──────│
│  │                                                          │ Colour │
│  │                                                          │ [████] │
│  │                                                          │ ──────│
│  │                                                          │ [AI ▸] │
├──┴──────────────────────────────────────────────────────────┴────────┤
│ [████][████][████][████][████]   Undo 12  │  600×1200px  │ Zoom 80% │  ← Colour tray + status
└──────────────────────────────────────────────────────────────────────┘
                                                              🎤 AI button (floating, bottom-right)
```

#### Screen 3 — Screenshot Decode Flow

```
Phase 1: Upload
┌────────────────────────────────────────────┐
│                                            │
│     Drag your design here                  │
│         — or —                            │
│     [Browse]  [Paste]  [Camera]            │
│                                            │
│  ✓ Works with blurry photos               │
│  ✓ WhatsApp screenshots welcome            │
│  ✓ PDF design cards supported             │
└────────────────────────────────────────────┘

Phase 2: AI Processing (animated step reveal, 45 sec)
┌────────────────────────────────────────────┐
│  Analysing your design...                  │
│                                            │
│  ✅ Pre-processing image         (3s)      │
│  ✅ Removing background           (5s)     │
│  ✅ Detecting saree zones         (8s)     │
│  🔄 Identifying motifs...        (→)       │
│  ⬜ Tracing design elements               │
│  ⬜ Extracting colours                    │
│  ⬜ Assigning weave structure             │
│  ⬜ Validating for loom                   │
│                                            │
│  [Live preview thumbnail animating...]     │
└────────────────────────────────────────────┘

Phase 3: Result
┌──────────────────────┬─────────────────────┐
│  Original Image       │  Decoded Design     │
│  [photo]              │  [canvas preview]   │
│                       │                     │
│                       │  Confidence: 91%    │
│                       │  Motifs found: 8    │
│                       │  Colours: 14        │
│                       │  Weave: Satin 8H    │
├──────────────────────┴─────────────────────┤
│  [Accept & Open in Editor]  [Refine]  [Try Again] │
└────────────────────────────────────────────────┘
```

#### Screen 4 — Loom Export

```
┌─────────────────────────────────────────────────┐
│  Export Design: Wedding Border v3               │
│  ─────────────────────────────────────────────  │
│  Target Machine:  [Udayravi 2400 Hook    ▾]     │
│  Format:          [Udayravi Native (.udr) ▾]    │
│  Hook Count:      [2400          ] hooks        │
│  Colour Depth:    [14 colours    ] (max 16)     │
│  Resolution:      [600 DPI       ]              │
│  ─────────────────────────────────────────────  │
│  VALIDATION RESULTS              Score: 97/100  │
│  ✅ Hook count: OK (2,200 of 2,400 used)        │
│  ✅ Colour count: OK (14 of 16 max)             │
│  ✅ All floats within limit (max: 8)            │
│  ⚠️  3 motifs have very fine detail (< 0.3mm)  │
│      [Auto-fix these]                           │
│  ─────────────────────────────────────────────  │
│  PREVIEW                                        │
│  [BMP preview thumbnail — 2400×1200]            │
│  ─────────────────────────────────────────────  │
│  [⬇ Download File]  [📡 Push to Loom #3]  [PDF Spec] │
└─────────────────────────────────────────────────┘
```

### 8.5 Component Library — Key Custom Components

| Component | Description |
|---|---|
| `<DesignCanvas>` | Core Fabric.js canvas wrapper. Zone layers, tools, real-time sync. |
| `<ZoneTab>` | Tabbed zone switcher with zone-specific colour coding |
| `<WeaveSelector>` | Visual weave structure picker — shows binary matrix preview |
| `<ColourSwatch>` | Yarn colour swatch with Pantone code tooltip, click-to-apply |
| `<MotifCard>` | Draggable motif card from library with SVG preview |
| `<LoomStatusCard>` | Live loom telemetry card with animated progress, RPM, error state |
| `<AIProgressStepper>` | Animated step-by-step AI pipeline progress |
| `<ConfidenceHeatmap>` | Canvas overlay showing AI confidence per region |
| `<ColourPalettePanel>` | Extracted palette with yarn matching, Delta-E scores |
| `<ThreadCounter>` | Live hook/colour count gauge with loom limit indicator |
| `<VoiceCommandButton>` | Floating mic button with waveform animation when active |
| `<CollaboratorCursor>` | Animated named cursor for collaborative editing |
| `<ExportConfigPanel>` | Loom target selection + export format configuration |
| `<ValidationScoreBadge>` | Animated 0-100 score ring with colour coding |
| `<TrendPulseWidget>` | Dashboard widget with trending motif/colour cards |

---

## 9. Module Breakdown — Web Application

### Module 1 — Auth & Tenant Management

**Routes:** `/login`, `/register`, `/invite`, `/settings/workspace`

**Features:**
- Email + password registration with email verification
- Google OAuth SSO (enterprise tier)
- Multi-tenant: each factory/company is a separate workspace (tenant)
- RBAC roles: `OWNER` / `ADMIN` / `DESIGNER` / `VIEWER` / `LOOM_OPERATOR`
- Invite team members by email with role assignment
- 2FA (TOTP — Google Authenticator compatible)
- Audit log: all login, design, export, and machine push events
- Session management: see all active sessions, revoke remotely

### Module 2 — Dashboard

**Routes:** `/dashboard`

**Features:**
- Recent designs grid with thumbnail, name, last modified, status
- Paste screenshot anywhere on page (global paste handler) → triggers decode flow
- Production queue widget: active loom jobs with progress bars
- AI Trend Pulse: weekly trending motifs and colours
- Quick stats: designs this month, looms active, orders completed, time saved vs. manual
- Global search: search all designs, motifs, orders by name/tag/colour (Meilisearch)

### Module 3 — Screenshot Decode Module

**Routes:** `/decode` (full-page flow), integrated into dashboard as drag-drop zone

**Features:**
- File upload (drag-drop, click-to-browse, paste, camera)
- Real-time pipeline progress (animated step-by-step)
- Side-by-side result view (original vs decoded)
- Confidence overlay toggle
- Batch decode: process up to 20 images at once, grid results view
- Decode history: all previous decode jobs with input image and output design

### Module 4 — Canvas Editor

**Routes:** `/design/:id`

**Features:**
- Fabric.js canvas with Konva compositing layer
- Zone tabs: Body / Border / Pallu / Endpiece — each lockable and independently editable
- Tool palette: Select, Pan, Draw (pencil, brush), Shapes (rect, ellipse, line, Bezier), Fill, Eyedropper, Magic Wand, Erase, Clone Stamp, Text
- Layers panel: show/hide/lock/reorder layers, rename, delete
- Properties panel: context-sensitive — shows weave assignment, colour, transform, opacity for selected layer
- Undo/redo: 100-step command stack
- Grid + snap: configurable grid with snap-to-grid
- Repeat preview: toggle to see the design tiled in repeat pattern
- Ruler: pixels, millimetres, and hook-count units
- Canvas zoom: 10%–3200%, smooth pinch-zoom on touch devices
- Keyboard shortcuts: standard Photoshop-style shortcuts (`V` select, `B` brush, `E` erase, `Ctrl+Z` undo, etc.)

### Module 5 — AI Generation Module

**Routes:** Integrated into Canvas Editor as right sidebar panel

**Features:**
- Text-to-pattern: prompt field with style/region/complexity parameters
- Sketch-to-pattern: draw on canvas → AI generates detailed design from sketch
- Reference-to-pattern: upload any image → AI generates in that style
- Variation generator: select any zone or layer → generate N variations
- Style transfer: apply visual style of reference image to existing design
- Generation history: browse all AI-generated designs in session
- Prompt library: saved successful prompts with preview

### Module 6 — Motif Library

**Routes:** `/library/motifs`

**Features:**
- Grid browse: 10,000+ motifs with thumbnail, name, region, style
- Search: text search + filter by region, style category, colour, complexity
- Drag-to-canvas: drag any motif directly onto the design canvas
- Motif detail: SVG preview, historical context, regional attribution, common uses, weave pairings
- Personal library: upload and save your own custom motifs
- Team library: shared motifs within your workspace
- Marketplace (Phase 3): buy/sell premium motif packs

### Module 7 — Weave Manager

**Routes:** `/library/weaves`, panel in Canvas Editor

**Features:**
- Visual weave library: all standard structures shown as binary matrix + fabric preview
- Custom weave editor: define your own weave by clicking the matrix
- Float checker: real-time float violation detection as you edit
- Yarn usage calculator: enter fabric dimensions → get yarn consumption per colour in metres
- Weave assignment: assign any weave to any layer with one click
- Weave simulation: see how the weave looks on the current design in 2D

### Module 8 — Colour Studio

**Routes:** Panel in Canvas Editor + `/library/colours`

**Features:**
- Palette extraction from any uploaded image
- Yarn colour matching: Delta-E matching to Pantone NTX, NCS, and Indian dye codes
- Colour reduction: auto-reduce palette to N colours while preserving design intent
- Harmony generator: given base colour → suggest complementary palettes as yarn swatches
- Colour library: save favourite palettes for reuse across designs
- Trend colours: weekly trending colours from Pantone/WGSN integrated

### Module 9 — 3D Preview Module

**Routes:** Modal/panel in Canvas Editor

**Features:**
- Real-time Three.js PBR rendering from design data
- View modes: Flat lay, Draped, Saree on mannequin
- Material selector: Silk / Cotton / Polyester / Zari / Blended
- Lighting presets: Daylight / Showroom / Wedding venue / Stage
- Export 3D preview as video (GIF or MP4) — for client presentations
- AR preview via mobile (Phase 2): WebXR API on mobile browser

### Module 10 — Export Engine

**Routes:** Modal in Canvas Editor

**Features:**
- Format selector with all supported formats (see Section 10)
- Machine-specific configuration (hook count, colour depth per machine)
- Validation run before every export — must pass minimum score
- BMP preview before export
- Download file or push directly to registered loom machine
- Export history: all previous exports with download links (90-day retention)
- Design spec sheet PDF: auto-generated with thumbnail, colours, weave specs, hook count, notes

### Module 11 — Loom Machine Module

**Routes:** `/looms`

**Features:**
- Machine registry: add/edit/delete loom machines, configure type and connection
- SJDAS Bridge download: link to download the Bridge agent for the factory PC
- Real-time status: online/offline indicator, current job, RPM, % complete
- Job push: select design + format → push directly to machine
- Telemetry history: RPM over time, error log, job history per machine
- Alert configuration: SMS/push alert on loom error, job complete, low yarn warning

### Module 12 — Production Management

**Routes:** `/production`

**Features:**
- Order creation: client name, design, loom assignment, deadline, notes, priority
- Kanban board: Design → Approved → Queued → Weaving → QC → Shipped
- Drag-and-drop order management
- Loom assignment: assign pending orders to available looms
- Production analytics: average design-to-loom time, rejection rate, output metres/day
- Rejection tracker: log rejections with reason codes, link to design for correction

### Module 13 — Design Library

**Routes:** `/library`

**Features:**
- All designs: grid/list view with filter by status, zone, date, tag, style
- Version history: every save creates a version — browse and restore any version
- Design tagging: manual tags + AI auto-tags (style, region, occasion, motifs detected)
- Folder organisation: user-defined folders
- Design sharing: share design link with external party (view-only, time-limited)
- Duplicate design: copy any design as starting point for new iteration
- Design comparison: side-by-side compare two versions

### Module 14 — Collaboration

**Routes:** Embedded in Canvas Editor

**Features:**
- Real-time multi-user canvas: see all collaborators' cursors and edits live
- Conflict resolution: operational transforms (OT) — last-write-wins with undo capability
- Presence indicators: avatar stack in top bar shows who is viewing/editing
- Comment threads: pin comment to canvas location — tag team members, reply, resolve
- Approval workflow: designer submits design → owner approves/rejects with comments
- Change notifications: email/push when collaborator edits or comments on your design

### Module 15 — Analytics

**Routes:** `/analytics`

**Features:**
- Usage: designs created per week, AI generations, exports, decode jobs
- Production: output metres, loom utilisation %, rejection rate trend
- Design performance: which designs/motifs/styles lead to successful orders
- Time saved: estimated hours saved vs. manual design workflow (shown as ₹ value)
- Trend alignment score: how well your design output matches current market trends

### Module 16 — Settings & Admin

**Routes:** `/settings`

**Features:**
- Workspace: name, logo, address, GST number
- Users: invite, remove, change roles
- Billing: plan, payment method, invoice history (Stripe Customer Portal)
- Loom config: global loom defaults (max hooks, max colours, float limit)
- Integrations: SJDAS Bridge link, webhook configuration
- Language: switch UI language (EN / Tamil / Telugu / Hindi)
- API Keys: generate API keys for external integration (Enterprise tier)

---

## 10. Udayravi & Power Loom Integration — Deep Specification

### 10.1 Udayravi Creations — Context

Udayravi Creations is a local Nellore-based Jacquard machine manufacturer and service provider. Their machines are the most common Jacquard controllers in the Nellore/Andhra Pradesh cluster. The existing SJDAS codebase already has BMP export logic targeting Udayravi machines — this section specifies how to formalise, expand, and deepen this integration.

### 10.2 Udayravi File Format Specification

Based on analysis of existing SJDAS loom_exporter.py and Udayravi machine documentation:

```
UDAYRAVI NATIVE FORMAT (.udr) — SPECIFICATION

File Header (64 bytes):
  Bytes 0–3:   Magic number: 0x55445259 ("UDRY")
  Bytes 4–5:   Format version: 0x0101 (v1.1)
  Bytes 6–7:   Hook count (little-endian uint16): e.g., 0x0960 = 2400
  Bytes 8–9:   Weft repeat count (little-endian uint16)
  Bytes 10–11: Colour count (uint16, max 16 for standard, 256 for extended)
  Bytes 12–13: DPI (uint16): typically 600
  Bytes 14–15: Weave type code (uint16)
  Bytes 16–47: Colour table (16 × 2 bytes: yarn colour index per colour slot)
  Bytes 48–63: Reserved / padding (0x00)

Body:
  Bitmap data in row-major order
  Each row = hook_count bits, packed into bytes (MSB first)
  1 = raised (warp thread lifted), 0 = lowered
  Total rows = weft_repeat_count

Extended Colour Mode (flag byte 15 = 0x01):
  Colour table expanded to 256 entries × 3 bytes (RGB) = 768 bytes
  Used when colour_count > 16
```

**SJDAS generates this format by:**
1. Taking the validated .sjd design file
2. Rendering all layers flat at target DPI
3. Applying colour reduction to target colour_count
4. Converting each pixel to the nearest colour slot index
5. Packing bits according to weave assignment per colour slot
6. Writing header + packed bit rows to .udr file

### 10.3 SJDAS Bridge Agent — Full Specification

**What it is:** A lightweight desktop application that runs on a Windows/Linux PC in the factory. It bridges the SJDAS cloud platform with the Udayravi (and other) loom machines on the local factory network.

**Tech stack:** Electron.js (cross-platform desktop) + Node.js backend. Single-file installer. ~50MB download. Requires no technical knowledge to install.

**Installation flow:**
1. Factory owner downloads SJDAS Bridge from `/settings/looms → Download Bridge`
2. Runs installer on factory Windows PC (double-click .exe)
3. During setup wizard: enters their SJDAS workspace API key (shown in settings)
4. Bridge registers with SJDAS cloud and shows device ID
5. Factory owner goes to SJDAS web app → adds loom machines → selects this Bridge as the connection point

**Machine connection methods (in priority order for Udayravi):**

| Method | When to Use | How |
|---|---|---|
| **File Drop (Primary)** | Udayravi controller has a "watch folder" on the PC | Bridge writes .udr file to configured folder path. Simplest and most reliable. |
| **USB Serial** | Older Udayravi units with serial interface | Bridge opens COM port, sends file via serial protocol (9600–115200 baud) |
| **TCP/IP LAN** | Newer Udayravi units with Ethernet port | Bridge sends file via TCP socket to machine IP:port |
| **USB HID** | Udayravi USB dongle interface | Bridge communicates via USB HID protocol |

**Bridge → Cloud communication:**
- Connects to SJDAS cloud via WebSocket over HTTPS (port 443 — works through any firewall)
- Receives job push: `{ jobId, designFile: base64, targetMachine, format }`
- Sends telemetry: `{ machineId, status, rpm, jobId, percentComplete, errors }`
- Telemetry polling interval: every 5 seconds while job active, every 60 seconds idle
- Offline resilience: if cloud connection drops, queues jobs locally in SQLite, syncs when reconnected

**Bridge security:**
- All cloud communication over TLS 1.3
- Bridge authenticates with workspace API key (stored in OS keychain, not plaintext file)
- Machine files are encrypted in transit (AES-256-GCM)
- Bridge can be remotely disabled from SJDAS web app

### 10.4 Supported Export Formats — Full List

| Format | Extension | Use Case | Priority |
|---|---|---|---|
| Udayravi Native | `.udr` | Udayravi Jacquard machines (Nellore cluster) | **P0 — Phase 1** |
| Standard Jacquard BMP | `.bmp` | Any Jacquard controller — universal | **P0 — Phase 1** |
| Staubli JC6 | `.jc6` | Staubli Jacquard heads (common in Kanchipuram, Surat) | P1 — Phase 2 |
| Bonas | `.bnd` | Bonas-Verdol controllers (Varanasi, Surat) | P1 — Phase 2 |
| Grosse | `.wif` + binary | Grosse Jacquard (South India) | P1 — Phase 2 |
| Mechanical Punch Card | `.pcd` | Older mechanical Jacquard looms | P2 — Phase 3 |
| Electronic Dobby | `.edb` | Dobby loom heads | P2 — Phase 3 |
| WIF (Weaving Information Format) | `.wif` | Open standard — compatible with many tools | P1 — Phase 2 |
| PNG (design export) | `.png` | High-resolution design image for presentations | **P0 — Phase 1** |
| SVG (design export) | `.svg` | Scalable vector design for further editing | P1 — Phase 2 |
| Colour Separation PDF | `.pdf` | Spot colour layers for manual production | P1 — Phase 2 |
| Design Spec Sheet PDF | `.pdf` | Production document with all specs | **P0 — Phase 1** |

---

## 11. Monetisation & B2B Licensing Model

### 11.1 Pricing Tiers

| Tier | Price | Users | Designs | AI Decodes | Looms | Support |
|---|---|---|---|---|---|---|
| **STARTER** | ₹4,999/month | 3 | 100/month | 20/month | 1 machine | Email 48h |
| **PROFESSIONAL** | ₹14,999/month | 10 | Unlimited | 100/month | 5 machines | Email 24h + Chat |
| **CLUSTER** | ₹39,999/month | Unlimited | Unlimited | 500/month | Unlimited | Priority + Phone |
| **ENTERPRISE** | Custom (₹75,000+) | Unlimited | Unlimited | Unlimited + custom model training | Unlimited + API | Dedicated + SLA + Onboarding |

**Annual discount:** 2 months free (16% discount) for annual prepay.

**Free Trial:** 14 days, full Professional features, no credit card required.

### 11.2 Add-On Revenue

| Add-On | Price | Description |
|---|---|---|
| Extra AI Decodes | ₹50/decode | Above plan limit |
| Extra AI Generations | ₹10/generation | Above plan limit |
| Motif Library Pro | ₹2,999/month | Access to premium regional motif packs (per region: Banarasi, Kanjivaram, Pochampally, etc.) |
| SJDAS Bridge Hardware Unit | ₹12,000 one-time | Pre-configured Raspberry Pi 4 with SJDAS Bridge pre-installed. Plug & play for non-technical factories. |
| Onboarding Package | ₹25,000 one-time | 2-day in-person factory onboarding + staff training (Andhra Pradesh) |
| Custom Motif Training | ₹50,000 one-time | Train AI on factory's own design archive. Improves decode accuracy for their specific style. |

### 11.3 Motif Marketplace (Phase 3)

- Designers and regional artisans upload curated motif packs
- Priced ₹500–5,000 per pack
- SJDAS takes 30% commission, creator gets 70%
- Build a catalogue of authentic regional packs: Banarasi Brocade Pack, Kanjivaram Temple Pack, Pochampally Ikat Pack, etc.

### 11.4 Go-to-Market — Solo Founder Strategy

**Month 1–3: Nellore Anchor Customers (Your Home Advantage)**
- Personally visit 20 power loom factories in Nellore and Dharmavaram
- Offer: 3-month free Professional access in exchange for: (a) feedback sessions, (b) design archive for training data, (c) testimonial/case study
- Target: 5 paying customers by Month 3 at ₹14,999/month = ₹75,000 MRR

**Month 4–6: Cluster Expansion + Word of Mouth**
- Kanchipuram (Tamil Nadu) — 500+ Jacquard silk factories. Partner with Kanchipuram Silk Weavers' Co-operative Society.
- Dharmavaram (AP) — wedding silk capital. Partner with local textile association.
- Use customer case studies (time saved, rejections reduced) as sales material
- WhatsApp group marketing: loom owners share referral links in factory WhatsApp groups
- Referral programme: ₹5,000 credit per referred paying customer

**Month 7–12: National Clusters**
- Varanasi (Banarasi silk), Surat (synthetic Jacquard), Bhiwandi (Maharashtra)
- Hire 1 part-time sales person in Varanasi and Surat once revenue supports it
- Apply for DPIIT Startup India recognition (tax benefits + credibility)
- Ministry of Textiles SAMARTH scheme: apply for textile technology grant

**Channel Partners:**
- Local CAD training institutes (NedGraphics resellers): offer 20% commission to refer clients
- Textile machinery dealers in Nellore/Dharmavaram: they already have relationships with all loom owners
- SIT (Silk & Industrial Textiles) regional associations: speak at association events

### 11.5 Revenue Projections (Conservative)

| Milestone | Timeline | MRR |
|---|---|---|
| 5 paying customers (Nellore) | Month 3 | ₹75,000 |
| 20 paying customers | Month 6 | ₹3,00,000 |
| 50 paying customers | Month 9 | ₹7,50,000 |
| 100 paying customers | Month 12 | ₹15,00,000 |
| 250 paying customers | Month 18 | ₹37,50,000 |

At ₹15,00,000 MRR (Month 12), you are at ₹1.8 crore ARR — Series A territory.

---

## 12. Database Schema & Data Architecture

### 12.1 PostgreSQL Schema (Prisma SDL)

```prisma
// Tenants (one per factory/company)
model Tenant {
  id              String   @id @default(cuid())
  name            String
  slug            String   @unique
  planTier        PlanTier @default(STARTER)
  maxUsers        Int      @default(3)
  maxDecodes      Int      @default(20)     // per month
  maxGenerations  Int      @default(50)
  loomConnections Int      @default(1)
  createdAt       DateTime @default(now())
  billingStatus   BillingStatus @default(ACTIVE)
  stripeCustomerId String? @unique
  users           User[]
  designs         Design[]
  orders          Order[]
  looms           LoomMachine[]
  subscription    Subscription?
}

// Users
model User {
  id                String   @id @default(cuid())
  tenantId          String
  tenant            Tenant   @relation(fields: [tenantId], references: [id])
  email             String   @unique
  name              String
  passwordHash      String?
  role              UserRole @default(DESIGNER)
  languagePref      Language @default(EN)
  avatarUrl         String?
  lastLoginAt       DateTime?
  twoFactorEnabled  Boolean  @default(false)
  createdAt         DateTime @default(now())
  @@index([tenantId])
}

// Designs
model Design {
  id            String        @id @default(cuid())
  tenantId      String
  tenant        Tenant        @relation(fields: [tenantId], references: [id])
  ownerId       String
  name          String
  description   String?
  thumbnailKey  String?       // S3 key
  fileKey       String        // S3 key for .sjd file
  status        DesignStatus  @default(DRAFT)
  tags          String[]
  style         String?       // "Kanjivaram", "Banarasi", etc.
  region        String?
  aiDecoded     Boolean       @default(false)
  decodeConf    Float?        // 0.0 - 1.0
  createdAt     DateTime      @default(now())
  updatedAt     DateTime      @updatedAt
  versions      DesignVersion[]
  orders        Order[]
  exports       ExportJob[]
  @@index([tenantId])
  @@index([ownerId])
}

// Design versions (immutable snapshot on each save)
model DesignVersion {
  id            String   @id @default(cuid())
  designId      String
  design        Design   @relation(fields: [designId], references: [id])
  versionNumber Int
  fileKey       String   // S3 key for this version's .sjd file
  createdById   String
  changeSummary String?
  createdAt     DateTime @default(now())
  @@unique([designId, versionNumber])
}

// Loom Machines
model LoomMachine {
  id              String          @id @default(cuid())
  tenantId        String
  tenant          Tenant          @relation(fields: [tenantId], references: [id])
  name            String
  machineType     MachineType     @default(UDAYRAVI)
  connectionMethod ConnectionMethod @default(FILE_DROP)
  bridgeAgentId   String?         // ID of registered Bridge agent
  ipAddress       String?
  port            Int?
  comPort         String?         // For USB serial
  watchFolderPath String?         // For file drop
  hookCount       Int             @default(2400)
  maxColours      Int             @default(16)
  maxFloat        Int             @default(8)
  status          MachineStatus   @default(OFFLINE)
  lastSeenAt      DateTime?
  createdAt       DateTime        @default(now())
  loomJobs        LoomJob[]
  @@index([tenantId])
}

// Export Jobs
model ExportJob {
  id            String      @id @default(cuid())
  designId      String
  design        Design      @relation(fields: [designId], references: [id])
  tenantId      String
  format        ExportFormat
  config        Json         // machine-specific config
  status        JobStatus    @default(PENDING)
  outputKey     String?      // S3 key of generated file
  validationScore Int?
  validationReport Json?
  createdAt     DateTime     @default(now())
  completedAt   DateTime?
  errorMessage  String?
  loomJobs      LoomJob[]
}

// Loom Jobs (push to machine)
model LoomJob {
  id              String     @id @default(cuid())
  loomId          String
  loom            LoomMachine @relation(fields: [loomId], references: [id])
  exportJobId     String
  exportJob       ExportJob  @relation(fields: [exportJobId], references: [id])
  status          JobStatus  @default(QUEUED)
  pushedAt        DateTime?
  startedAt       DateTime?
  completedAt     DateTime?
  metresCompleted Float?
  errorLog        String?
}

// AI Decode Jobs
model DecodeJob {
  id              String    @id @default(cuid())
  tenantId        String
  inputKey        String    // S3 key of uploaded image
  status          JobStatus @default(PENDING)
  resultDesignId  String?   // Design created from decode
  confidenceReport Json?
  pipelineLog     Json?     // Step-by-step timing + results
  createdAt       DateTime  @default(now())
  completedAt     DateTime?
  errorMessage    String?
}

// Orders
model Order {
  id            String      @id @default(cuid())
  tenantId      String
  tenant        Tenant      @relation(fields: [tenantId], references: [id])
  designId      String
  design        Design      @relation(fields: [designId], references: [id])
  loomId        String?
  customerName  String
  notes         String?
  priority      Priority    @default(NORMAL)
  status        OrderStatus @default(DESIGN_PENDING)
  deadline      DateTime?
  createdAt     DateTime    @default(now())
  updatedAt     DateTime    @updatedAt
}

// Enums
enum PlanTier     { STARTER PROFESSIONAL CLUSTER ENTERPRISE }
enum UserRole     { OWNER ADMIN DESIGNER VIEWER LOOM_OPERATOR }
enum Language     { EN TA TE HI }
enum DesignStatus { DRAFT IN_PROGRESS APPROVED ARCHIVED }
enum MachineType  { UDAYRAVI STAUBLI BONAS GROSSE GENERIC_BMP }
enum ConnectionMethod { FILE_DROP USB_SERIAL TCP_IP USB_HID MQTT }
enum MachineStatus { ONLINE OFFLINE BUSY ERROR }
enum ExportFormat { UDR BMP STAUBLI_JC6 BONAS WIF PNG SVG PDF_COLOUR_SEP PDF_SPEC }
enum JobStatus    { PENDING PROCESSING COMPLETED FAILED CANCELLED }
enum OrderStatus  { DESIGN_PENDING APPROVED QUEUED WEAVING QC SHIPPED REJECTED }
enum Priority     { LOW NORMAL HIGH URGENT }
enum BillingStatus { ACTIVE PAST_DUE CANCELLED }
```

### 12.2 Redis Key Structure

```
# Session tokens
session:{userId} → JSON user session data, TTL 15min

# Collaboration canvas state
collab:canvas:{designId} → JSON canvas state (latest snapshot)
collab:cursors:{designId} → Hash of userId → {x, y, name, colour}

# AI job status (for polling)
job:status:{jobId} → JSON {status, progress, step, result}

# Rate limiting
ratelimit:api:{tenantId}:{endpoint} → Counter, TTL 1min
ratelimit:decode:{tenantId} → Counter per month, TTL to month end

# Feature flags
flags:{tenantId} → JSON feature flag overrides

# Loom telemetry (latest)
loom:telemetry:{machineId} → JSON {status, rpm, jobId, pct, lastSeen}
```

### 12.3 S3 Bucket Structure

```
s3://sjdas-prod/
├── uploads/
│   └── {tenantId}/
│       └── {timestamp}-{uuid}.{ext}          ← raw user uploads (images for decode)
├── designs/
│   └── {tenantId}/
│       └── {designId}/
│           ├── current.sjd                    ← current design file
│           ├── thumbnail.webp                 ← 400×400 thumbnail
│           ├── versions/
│           │   └── v{n}.sjd                   ← version snapshots
│           ├── layers/
│           │   └── {layerId}.png              ← individual layer bitmaps
│           └── repeat_tile.png                ← extracted repeat tile
├── exports/
│   └── {tenantId}/
│       └── {exportJobId}/
│           ├── design.{format}                ← the loom file
│           └── spec_sheet.pdf                 ← design spec PDF
├── motifs/
│   ├── system/
│   │   └── {motifId}/
│   │       ├── motif.svg                      ← vector motif
│   │       └── thumb.webp                     ← preview thumbnail
│   └── {tenantId}/
│       └── custom motifs
└── ml/
    └── datasets/
        └── v{n}/
            ├── images/
            ├── labels/
            └── metadata.json
```

---

## 13. API Architecture

### 13.1 REST Endpoints — Python Design Service (FastAPI)

```
POST   /api/v1/decode                    Upload image, start decode job
GET    /api/v1/decode/{jobId}            Poll decode job status + result
POST   /api/v1/decode/batch             Upload multiple images (up to 20)

POST   /api/v1/ai/generate              Text/sketch-to-pattern generation
POST   /api/v1/ai/variations            Generate N variations of a design
POST   /api/v1/ai/analyse               Analyse design (motifs, quality, weave rec)
POST   /api/v1/ai/style-transfer        Apply style from reference image
POST   /api/v1/ai/voice                 Process voice command (audio upload)

POST   /api/v1/export                   Trigger export job (design → loom file)
GET    /api/v1/export/{jobId}           Poll export job + download URL

GET    /api/v1/motifs                   Search motif library
GET    /api/v1/motifs/{id}              Get motif detail + SVG
POST   /api/v1/motifs                   Upload custom motif (tenant)

GET    /api/v1/weaves                   List weave structures
POST   /api/v1/weaves/check-floats      Check float violations for weave+design
POST   /api/v1/weaves/yarn-calc         Calculate yarn usage
```

### 13.2 REST Endpoints — Node.js Business Logic Service (Hono.js)

```
# Auth
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
POST   /api/v1/auth/invite/{token}      Accept workspace invite
GET    /api/v1/auth/me

# Designs
GET    /api/v1/designs                  List (paginated, filterable)
POST   /api/v1/designs                  Create new design
GET    /api/v1/designs/{id}            Get design + metadata
PATCH  /api/v1/designs/{id}            Update name/tags/status
DELETE /api/v1/designs/{id}
GET    /api/v1/designs/{id}/versions   List versions
GET    /api/v1/designs/{id}/versions/{v} Get specific version

# Looms
GET    /api/v1/looms                    List registered machines
POST   /api/v1/looms                    Register new machine
PATCH  /api/v1/looms/{id}
DELETE /api/v1/looms/{id}
POST   /api/v1/looms/{id}/push         Push export job to machine
GET    /api/v1/looms/{id}/telemetry    Latest telemetry snapshot
GET    /api/v1/looms/{id}/history      Job + telemetry history

# Orders
GET    /api/v1/orders
POST   /api/v1/orders
PATCH  /api/v1/orders/{id}
DELETE /api/v1/orders/{id}

# Workspace / Admin
GET    /api/v1/workspace               Get tenant settings
PATCH  /api/v1/workspace
POST   /api/v1/workspace/invite        Invite user by email
GET    /api/v1/workspace/users         List workspace users
PATCH  /api/v1/workspace/users/{id}   Change role
DELETE /api/v1/workspace/users/{id}   Remove user

# Analytics
GET    /api/v1/analytics/overview      Dashboard stats
GET    /api/v1/analytics/designs       Design performance
GET    /api/v1/analytics/production    Production metrics
GET    /api/v1/analytics/looms         Loom efficiency
```

### 13.3 WebSocket Events (Socket.io)

```javascript
// Canvas collaboration (room: `canvas:${designId}`)
"canvas:join"             // User joins design session
"canvas:leave"            // User leaves design session
"canvas:operation"        // Canvas mutation (add/move/edit layer)
"canvas:cursor"           // Cursor position update
"canvas:undo"             // Undo operation broadcast
"canvas:selection"        // Selection change broadcast

// AI progress (room: `job:${jobId}`)
"ai:progress"             // { step, progress: 0-100, message }
"ai:complete"             // { resultDesignId, confidence }
"ai:error"                // { message }

// Loom telemetry (room: `loom:${machineId}`)
"loom:status"             // { status, rpm, jobId, pctComplete }
"loom:error"              // { code, message }
"loom:complete"           // { jobId, metresCompleted }

// Global notifications (room: `user:${userId}`)
"notification:new"        // { type, message, actionUrl }
"export:ready"            // { exportJobId, downloadUrl }
"approval:request"        // { designId, fromUser }
```

---

## 14. DevOps, CI/CD & Infrastructure

### 14.1 Local Development Setup (Docker Compose)

```yaml
# docker-compose.dev.yml
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: sjdas_dev
      POSTGRES_USER: sjdas
      POSTGRES_PASSWORD: dev_password
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  meilisearch:
    image: getmeili/meilisearch:v1.7
    ports: ["7700:7700"]
    environment:
      MEILI_MASTER_KEY: dev_master_key

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin

  web:
    build: ./web
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://sjdas:dev_password@postgres:5432/sjdas_dev
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: http://minio:9000
    depends_on: [postgres, redis, minio]
    volumes: ["./web:/app"]

  api:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://sjdas:dev_password@postgres:5432/sjdas_dev
      REDIS_URL: redis://redis:6379
    depends_on: [postgres, redis]
    volumes: ["./backend:/app"]

  worker:
    build: ./backend
    command: celery -A app.worker worker --loglevel=info
    depends_on: [redis, api]
    volumes: ["./backend:/app"]
    # Note: for AI features locally, needs GPU or will use CPU (slow)
```

**One command to start everything locally:**
```bash
docker compose -f docker-compose.dev.yml up
```

### 14.2 GitHub Actions CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test Frontend
        run: |
          cd web && npm ci
          npm run type-check
          npm run lint
          npm run test
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements-dev.txt
          mypy app/ --ignore-missing-imports
          ruff check app/
          pytest tests/ -v --cov=app --cov-fail-under=75

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1

      - name: Build and push Docker images to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker build -t $ECR_REGISTRY/sjdas-web:$GITHUB_SHA ./web
          docker build -t $ECR_REGISTRY/sjdas-api:$GITHUB_SHA ./backend
          docker push $ECR_REGISTRY/sjdas-web:$GITHUB_SHA
          docker push $ECR_REGISTRY/sjdas-api:$GITHUB_SHA

      - name: Deploy to ECS (staging)
        run: |
          aws ecs update-service --cluster sjdas-staging \
            --service sjdas-web --force-new-deployment
          aws ecs update-service --cluster sjdas-staging \
            --service sjdas-api --force-new-deployment

      - name: Run E2E tests on staging
        run: |
          cd web && npx playwright test --config=playwright.staging.config.ts

      - name: Deploy to production (manual approval required)
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ secrets.GITHUB_TOKEN }}
          approvers: BalajiKoushik01
```

### 14.3 Solo Founder Infrastructure Cost Estimate (Monthly)

| Service | Tier | Monthly Cost (USD) | Monthly Cost (INR) |
|---|---|---|---|
| AWS ECS Fargate (web + api) | 2 tasks × 0.5 vCPU + 1GB | ~$25 | ~₹2,000 |
| AWS RDS PostgreSQL | db.t3.medium (Multi-AZ off) | ~$30 | ~₹2,500 |
| AWS ElastiCache Redis | cache.t3.micro | ~$15 | ~₹1,250 |
| AWS S3 + CloudFront | 100GB storage + 50GB transfer | ~$15 | ~₹1,250 |
| EC2 GPU (G4dn.xlarge spot) | ~8 hrs/day × 30 days | ~$40 | ~₹3,300 |
| AWS Secrets Manager | — | ~$5 | ~₹400 |
| Grafana Cloud + Sentry | Free tiers | $0 | ₹0 |
| Resend (email) | Free tier | $0 | ₹0 |
| Meilisearch Cloud (search) | Starter | ~$30 | ~₹2,500 |
| Domain + SSL | Route 53 | ~$5 | ~₹400 |
| **Total Infrastructure** | | **~$165/month** | **~₹13,600/month** |

Your first 5 customers at ₹14,999/month = ₹74,995 MRR — infrastructure cost is <20% of revenue from customer 1.

---

## 15. Security & Compliance

### 15.1 Security Architecture

**Multi-tenant isolation:**
- PostgreSQL Row-Level Security (RLS): every table with `tenantId` has a policy that restricts queries to the current tenant's rows
- S3 object keys always prefixed with `{tenantId}/` — server enforces this, never trusts client paths
- Redis keys always prefixed with `{tenantId}:` for tenant-namespaced data

**Authentication:**
- JWT access tokens: 15-minute expiry, RS256 signed
- Refresh tokens: 30-day expiry, stored as httpOnly cookie, rotated on each use
- 2FA: TOTP (RFC 6238) — QR code setup, backup codes provided
- All passwords: bcrypt with cost factor 12

**API security:**
- Rate limiting: Kong Gateway — 100 req/min per tenant on standard endpoints, 10 req/min on AI/decode
- Input validation: Zod (Node.js) and Pydantic v2 (Python) — all inputs validated before processing
- File upload security: magic byte validation (not just extension checking), max 50MB per file, virus scan (ClamAV) on all uploads
- SQL injection: impossible via Prisma ORM parameterised queries
- XSS: React's JSX auto-escaping + strict CSP headers

**Data protection:**
- RDS encrypted at rest (AWS KMS)
- S3 buckets: server-side encryption (SSE-S3 minimum, SSE-KMS for sensitive data)
- All inter-service communication over TLS 1.3
- Audit log: every design create/edit/export/delete, every loom push, every login — immutable append-only log in PostgreSQL

### 15.2 India DPDP Act Compliance

The Digital Personal Data Protection Act 2023 applies to SJDAS as it processes personal data of Indian users.

- Data localisation: all data stored in AWS ap-south-1 (Mumbai) ✓
- Consent: explicit consent checkbox at registration with clear privacy policy link
- Purpose limitation: data collected only for stated purpose (platform operation)
- Data principal rights: users can request data export or account deletion — implemented in Settings → Privacy
- Data retention: delete inactive accounts after 2 years of no activity (configurable)
- Breach notification: Sentry alerts + 72-hour notification procedure documented

### 15.3 Security Checklist Before Each Production Deploy

- [ ] All secrets in AWS Secrets Manager (no hardcoded keys)
- [ ] `npm audit` / `pip audit` — no high/critical CVEs unaddressed
- [ ] OWASP Top 10 scan (run ZAP against staging)
- [ ] All S3 buckets: public access blocked, bucket policy verified
- [ ] RDS: not publicly accessible, security group only allows ECS tasks
- [ ] HTTPS enforced everywhere — HTTP redirects to HTTPS
- [ ] CSP, HSTS, X-Frame-Options headers set

---

## 16. Solo Founder Build Roadmap — Week by Week

### Guiding Principles for Solo Build

1. **Ship working software to real users as fast as possible.** A beta customer using the product weekly is worth 100 features.
2. **AI-first on the core feature (decode), polish later.** Get the decode pipeline working end-to-end, even if the UI is rough.
3. **Use managed services for everything non-core.** Your competitive advantage is the AI and the domain knowledge — not your auth system.
4. **Each phase ends with something demo-able to a factory owner.**
5. **Avoid premature optimisation.** Single ECS task is fine for 50 customers. Optimise when you have the problem.

### Phase 0 — Foundation (Weeks 1–3)

**Goal:** Full-stack scaffold running locally and on staging. Login works.

| Week | What to Build | Output |
|---|---|---|
| Week 1 | Next.js 14 scaffold with Tailwind + design tokens. Prisma schema + PostgreSQL. Docker Compose local dev. GitHub repo + CI lint/test. | Can run `docker compose up` and see a styled home page |
| Week 2 | Auth module: register, login, JWT, refresh tokens, multi-tenant creation. Basic dashboard layout (no data yet). S3 bucket + MinIO local. | Can register, log in, see empty dashboard |
| Week 3 | GitHub Actions CI/CD → ECS staging deploy. Staging domain live (e.g. staging.sjdas.in). Error tracking (Sentry). Monitoring (Grafana Cloud). | Every push to main auto-deploys to staging. Real URL works. |

### Phase 1 — Core MVP: Decode + Canvas + Export (Weeks 4–12)

**Goal:** A factory owner can upload a photo, see a decoded design, edit it, and export a BMP/UDR file.

| Week | What to Build | Output |
|---|---|---|
| Week 4 | FastAPI backend scaffold. Celery + Redis job queue. S3 upload endpoint. Placeholder decode endpoint that returns mock result. | Can upload image, see "processing…" status, get mock result |
| Week 5 | Image pre-processing pipeline: BSRGAN super-res, OpenCV normalisation, background removal (SAM v2 via HuggingFace Inference API first — don't run your own GPU yet). | Step 1–2 of decode pipeline working |
| Week 6 | Zone segmentation (U-Net inference) + motif detection (YOLOv8, use pretrained COCO model as placeholder until fine-tuned). | Steps 3–4 working with pretrained models |
| Week 7 | Contour tracing + Bezier vectorisation (potrace + scipy). Colour extraction (KMeans). .sjd file assembly. | Steps 5–7 working. .sjd file generated. |
| Week 8 | Canvas Editor: Fabric.js canvas loads .sjd file. Zone tabs. Layers panel. Basic select/move tools. Undo/redo. | Decoded design opens in canvas. Can move things around. |
| Week 9 | Canvas Editor: drawing tools (brush, shapes, fill). Properties panel (weave selector, colour picker). Repeat preview. | Full editing capability in canvas |
| Week 10 | Export Engine: BMP export. Udayravi .udr export. Float checker. Validation score. Export modal UI. Design Spec Sheet PDF. | Can export a design to BMP and .udr. Validation runs. |
| Week 11 | Design Library: list, thumbnail generation, version save, search (Meilisearch). Dashboard with real data. | Dashboard shows real designs. Library works. |
| Week 12 | Polish MVP: loading states, error states, confidence report display, decode history. Performance check (canvas 60fps). | **BETA LAUNCH READY** |

**End of Phase 1:** Show this to 5 Nellore factory owners. Get 3 using it weekly.

### Phase 2 — AI Power Features (Weeks 13–22)

**Goal:** AI generation, voice commands, collaboration, 3D preview, loom machine API.

| Week | What to Build | Output |
|---|---|---|
| Week 13 | Fine-tune YOLOv8 on collected textile dataset. Improve decode accuracy from ~60% to ~85%. | Decode quality jumps significantly |
| Week 14 | AI Pattern Generation: SDXL inference endpoint. Prompt UI in canvas sidebar. Style/region/complexity params. | Can generate designs from text prompts |
| Week 15 | AI Pattern Generation: ControlNet sketch input (draw on canvas → AI fills). Variation generator. | Sketch-to-design working |
| Week 16 | Colour Intelligence: yarn matching (Pantone NTX Delta-E). Colour harmony generator. Colour reduction with Delta-E optimisation. | Colour panel with yarn codes and harmony suggestions |
| Week 17 | Voice Commands: Whisper inference endpoint. Voice command parser (intent + entity extraction). Integration with canvas actions. English + Telugu first. | Say "change border colour to gold" → it happens |
| Week 18 | SJDAS Bridge Agent: Electron.js desktop app. File drop integration (Udayravi watch folder). WebSocket tunnel to cloud. | File exported from web → appears in Udayravi watch folder automatically |
| Week 19 | Real-time Collaboration: Socket.io server. Canvas OT (operational transforms). Presence cursors. Comment threads. | Two people editing same design simultaneously |
| Week 20 | 3D Fabric Preview: Three.js PBR shader. Flat/draped/mannequin modes. Material selector. | Can preview designed fabric in 3D |
| Week 21 | Production Management: Order model. Kanban board UI. Loom assignment. Production analytics. | Full order-to-loom pipeline visible |
| Week 22 | Multi-lingual UI: Tamil + Hindi translations. Language switcher. Whisper Tamil/Hindi voice commands. | App fully usable in Tamil and Hindi |

**End of Phase 2:** 20+ paying customers. MRR ₹3,00,000+. Raise pre-seed if desired.

### Phase 3 — Scale & Enterprise (Weeks 23–36)

**Goal:** Full feature parity with (and beyond) all competitors. Enterprise readiness. National expansion.

| Weeks | What to Build |
|---|---|
| 23–24 | Motif Library: catalogue 10,000 motifs. Region packs. Drag-to-canvas. Personal + team library. |
| 25–26 | Staubli JC6 + Bonas export formats. WIF export. Expand to Kanchipuram + Varanasi clusters. |
| 27–28 | Rejection Prediction AI: train on factory rejection data. Predictive analytics dashboard. |
| 29–30 | AI Design Assistant Chatbot (Claude API integration). Context-aware textile knowledge. |
| 31–32 | Trend Intelligence Module: Pantone API + scraping pipeline. Trend score per design. |
| 33–34 | Motif Marketplace: upload, pricing, purchase flow, Stripe Connect for creator payouts. |
| 35–36 | Enterprise features: custom model training pipeline, white-label option, API keys, SSO, SLA infra. |

### Phase 4 — Mobile & Global (Months 10–15)

- React Native mobile app (iOS + Android) — design approval, loom monitoring, decode from phone camera
- AR preview using WebXR on mobile
- Bangladesh, Vietnam, Indonesia market entry (Bengali, Bahasa localisation)
- API ecosystem — let third-party tools integrate with SJDAS

---

## 17. KPIs & Success Metrics

### 17.1 Product KPIs

| Metric | Phase 1 Target | Phase 2 Target | Phase 3 Target |
|---|---|---|---|
| Screenshot Decode Accuracy (mAP@0.5) | > 70% (pretrained models) | > 88% (fine-tuned) | > 93% (fine-tuned + more data) |
| Decode Time (standard 1080p image) | < 90 seconds | < 60 seconds | < 30 seconds |
| Canvas Performance | 30 fps | 60 fps | 60 fps + smooth collab |
| Export Success Rate | > 95% | > 99% | > 99.5% |
| AI Generation Acceptance Rate | N/A | > 70% | > 80% |
| Loom Push Success Rate | > 95% | > 99% | > 99.5% |
| Uptime | 99% | 99.5% | 99.9% |

### 17.2 Business KPIs

| Metric | Month 3 | Month 6 | Month 9 | Month 12 |
|---|---|---|---|---|
| Paying workspaces | 5 | 20 | 50 | 100 |
| MRR | ₹75,000 | ₹3,00,000 | ₹7,50,000 | ₹15,00,000 |
| Decode jobs/month | 200 | 1,000 | 3,000 | 5,000 |
| Designs exported/month | 100 | 500 | 1,500 | 2,500 |
| NPS score | > 50 | > 60 | > 65 | > 70 |
| Customer churn rate | < 10% | < 8% | < 6% | < 5% |
| Design-to-loom time reduction | > 50% | > 65% | > 70% | > 75% |

### 17.3 The One Metric That Matters Most

> **Designs successfully exported to loom per active workspace per week.**

This is the core value metric. If a factory is exporting designs to their loom, SJDAS is working. If this number is growing, you are winning. Every product, AI, and UX decision should be judged by whether it increases this number.

---

## 18. Appendix — File Formats, Motif Taxonomy & Yarn Standards

### 18.1 Indian Saree Anatomy Reference

```
                        SAREE LAYOUT (9 metres total)
┌──────────────────────────────────────────────────────────────┐
│ ENDPIECE │        BODY (main fabric — ~7.5m)       │  PALLU  │
│ (25cm)   │                                          │ (80cm)  │
│          │  [body repeat tile tiles across here]    │         │
│          │                                          │         │
├──────────┼──────────────────────────────────────────┼─────────┤
│ BORDER   │           BORDER (kinnam)                │ BORDER  │
│ 5-20cm   │        runs full length of saree         │         │
└──────────┴──────────────────────────────────────────┴─────────┘
     ↑
  blouse piece (optional, ~0.8m, often separate design)
```

**Zone characteristics for SJDAS:**
- **Body:** tiled repeat pattern — only the minimal repeat tile needs to be designed
- **Border:** linear repeat — tiles in the weft (width) direction only
- **Pallu:** unique non-repeating design — the most complex and premium section
- **Endpiece:** simpler version of pallu on the other end

### 18.2 Indian Textile Motif Taxonomy

```
ROOT: Indian Textile Motifs
├── Floral
│   ├── Lotus (kamal) — sacred, very common in all regions
│   ├── Marigold (genda) — auspicious, Varanasi specialty
│   ├── Rose (gulab) — Mughal influence, Lucknowi
│   ├── Jasmine (chameli) — South Indian border motif
│   └── Flower vine (phool bel) — creeper/scroll with flowers
├── Animal & Bird
│   ├── Peacock (mayura/mor) — national bird, dominant in Kanjivaram, Banarasi
│   ├── Parrot (tota/kili) — auspicious, common in border motifs
│   ├── Swan (hans) — associated with purity, Odia and Assamese textiles
│   ├── Elephant (hathi/gaj) — South Indian temple borders
│   ├── Horse (ghoda) — Rajasthani influence
│   └── Fish (meen/matsya) — Bengal (Jamdani), Assam (Mekhela Chador)
├── Geometric
│   ├── Diamond (heera) — Pochampally ikat specialty
│   ├── Chevron / Zigzag — Patola (Gujarat)
│   ├── Hexagonal lattice — Kota Doria
│   ├── Square grid (chaukhana) — basic geometric background
│   └── Triangle border (trikona) — South Indian temple borders
├── Nature
│   ├── Mango / Paisley (kalga/keri/aam) — most common Indian motif ever
│   ├── Leaf scroll (patti bel) — running border vine
│   ├── Tree of Life (kalpa vriksha) — temple sarees
│   ├── Sun (surya) — Odia, Assamese motifs
│   └── Moon (chandra) — Chanderi, Maheshwari motifs
├── Architectural
│   ├── Temple gopuram border — Kanjivaram signature
│   ├── Arch (mehrab) — Mughal influence, Banarasi
│   ├── Lattice window (jali) — Lucknowi, Chanderi
│   └── Palace pillars (stambha) — heavy silk sarees
├── Abstract / Symbolic
│   ├── Butis (scattered small motifs) — dots, seeds, stars distributed across body
│   ├── Chakra (wheel/circle) — sacred, many variations
│   ├── Swastika (good luck symbol) — traditional, context-sensitive
│   ├── Kalash (pot) — auspicious, used in borders
│   └── Zari line patterns — pure geometric gold/silver stripe patterns
└── Regional Specialties
    ├── Pochampally ikat geometric (Telangana)
    ├── Uppada jamdani floral (Andhra Pradesh — your region!)
    ├── Dharmavaram silk temple motifs (Andhra Pradesh)
    ├── Venkatagiri jamdani (Andhra Pradesh)
    ├── Kanjivaram temple/peacock (Tamil Nadu)
    └── Banarasi Mughal brocade (Uttar Pradesh)
```

### 18.3 Standard Yarn Colour Code Systems

| System | Used In | Notes |
|---|---|---|
| Pantone NTX (Textile) | International, premium mills | Industry standard for cotton/silk yarn colours. 2,310 colours. |
| NCS (Natural Colour System) | European suppliers | Used by Staubli-compatible mills. |
| RAL | Industrial textiles | Less common in Indian saree industry |
| Indian Dye Batch Codes | Domestic Indian mills | Not standardised — SJDAS will build a mapping from common supplier codes |
| Munsell | Academic / research | Used in academic textile colour research |

**SJDAS approach:** Store all colours as hex (device-independent) + Delta-E matched Pantone NTX code. Allow factory to add their own yarn supplier codes and map to Pantone. This creates a factory-specific yarn library that improves with use.

### 18.4 Standard Weave Notation Reference

| Weave Type | Notation | Raised:Lowered | Float Length | Typical Use |
|---|---|---|---|---|
| Plain (tabby) | 1/1 | 1:1 | 1 | Background, simple fill |
| 2/2 twill | 2/2 | 2:2 | 2 | Texture, diagonal pattern |
| 3/1 twill | 3/1 | 3:1 | 3 | Satin-twill hybrid |
| 4H satin | 4 HS | 3:1 | 4 | Medium sheen, body fill |
| 5H satin | 5 HS | 4:1 | 5 | Good sheen, dress sarees |
| 8H satin | 8 HS | 7:1 | 8 | Maximum sheen — Kanjivaram pallu |
| Jacquard compound | JC | Variable | Variable | Complex motifs, multi-colour |
| Dobby | DOB | Per shaft sequence | Variable | Geometric patterns, borders |

### 18.5 Environment Variables Reference

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/sjdas

# Redis
REDIS_URL=redis://host:6379

# AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-south-1
S3_BUCKET_NAME=sjdas-prod

# AI Services
ANTHROPIC_API_KEY=           # For AI assistant (Claude API)
OPENAI_API_KEY=              # Optional: Whisper API (or self-host)
HUGGINGFACE_API_KEY=         # For HF Inference API (SAM v2, etc.)

# Auth
JWT_SECRET=                  # RS256 private key (base64)
JWT_PUBLIC_KEY=              # RS256 public key (base64)

# Payments
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=      # Frontend env

# Email
RESEND_API_KEY=

# SMS
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Search
MEILISEARCH_HOST=
MEILISEARCH_MASTER_KEY=

# Monitoring
SENTRY_DSN=
SENTRY_ENVIRONMENT=production

# Feature flags
FLAGSMITH_API_KEY=

# App
NEXT_PUBLIC_APP_URL=https://app.sjdas.in
NEXT_PUBLIC_API_URL=https://api.sjdas.in
APP_ENV=production
```

---

## Document Control

| Field | Value |
|---|---|
| Document Title | SJDAS Product Bible v1.1 — Solo Founder Edition |
| Version | 1.1 |
| Date | March 2026 |
| Author | Balaji Koushik |
| Status | ACTIVE — Living Document |
| Target Stack | Nellore cluster (Udayravi machines), Solo founder build |
| Next Review | June 2026 |
| Classification | CONFIDENTIAL — Internal Use Only |

> **This is a living document.** Update it at every major decision point — new features, architecture changes, competitive moves, pivot decisions. All engineering, design, and business decisions should trace back to this document. Treat it as the single source of truth for everything SJDAS.

---

*Built with purpose for the Indian textile industry. Every power loom factory in India deserves world-class software.*
