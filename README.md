# SJDAS v2.0: Autonomous Textile Jacquard Studio
**The "Zero-Labor" B2B SaaS for Modern Power Looms**

SJDAS v2.0 is an enterprise-grade, cloud-native Textile Design Studio built to bridge the gap between human creativity and rigid mechanical loom constraints. By leveraging AI (SAM 2, Hugging Face Real-ESRGAN, K-Means Quantization) and mathematical matrix generation (OpenCV, Supabase), SJDAS autonomously outputs 100% production-ready 8-bit Indexed Color BMPs and JC5 machine files directly to industrial Jacquard looms.

---

## 👨‍💻 Author & Contact
**Balaji Koushik**
Email: [balajikoushik01@gmail.com](mailto:balajikoushik01@gmail.com)
GitHub: [BalajiKoushik01](https://github.com/BalajiKoushik01)

---

## 🏗️ Architecture Stack

### Frontend (The Midnight Industrial Studio)
- **Framework:** Next.js 15 (App Router)
- **Editor:** Fabric.js (Strict `useRef` isolation for massive 12,000x8000px canvases)
- **State Management:** Zustand (for non-blocking UI interactions)
- **Styling & UI:** Tailwind CSS v4, shadcn/ui
- **Animations:** Framer Motion (Liquid UI transitions and WebSockets progress streaming)

### Backend (The Autonomous Workers)
- **API Engine:** FastAPI (Python)
- **Async Pipeline:** Celery + Redis (Handling massive NumPy matrix computations off the main thread)
- **Live Sync:** WebSockets (`/ws/progress/{task_id}`) for 0ms UI progress updates
- **Math Engine:** OpenCV (Non-Linear Trapezoidal Kali Warping via `cv2.INTER_NEAREST`)
- **Compilation:** Pillow `P` mode (Zero-compression 8-bit Strict Palette hardware exporting)

### Database & Auth (Multi-Tenant Scale)
- **Platform:** Supabase (PostgreSQL)
- **Security:** Strict Row Level Security (RLS) policies guaranteeing exact `factory_id` tenant isolation
- **Feature Set:** `loom_profiles` (Hardware Constraints) and `thread_inventory` (Physical stock counts)
- **Storage:** Private Supabase Buckets mapped to `factory_id` for proprietary Zero-Scrape IP protection.

---

## ⚙️ Core Modules & Capabilities

### 1. The Kali-Warp Processing Engine (Multi-Panel Output)
SJDAS mathematically stretches and tapers motifs (using OpenCV `getPerspectiveTransform` and `INTER_NEAREST`) to construct **Multi-Panel (Kali)** designs. The backend smoothly stitches up to 12 Kalis into a single giant NumPy array seamlessly.

### 2. Factory Stock API (CIEDE2000 Delta-E Matching)
The system calculates the Euclidean distance between a design's colors and the factory's physical thread inventory stored in Supabase. It features an interactive "Traffic Light" UI (`FactoryStockSidebar.tsx`) that alerts designers if they draw with colors representing threads that are out of stock.

### 3. Asynchronous "Shadow Canvas" (Float Guardian)
The React UI stays silky smooth because heavy math (SAM 2 AI Tracing, Hugging Face Denoising) runs via Celery Background Workers. 

### 4. Zero-Aliasing Machine Export
Directly exports 8-bit Indexed Color `saree_production_file.bmp` files with strict 768-integer pallet headers, completely compliant with Stäubli and Bonas loom interfaces.

---

## 🚀 Setup & Installation

### 1. Requirements
- Node.js 18+
- Python 3.10+
- Redis Server (Native or Docker)
- Supabase Project

### 2. Next.js Frontend Initialization
```bash
cd web
npm install
npm run dev
```

### 3. FastAPI Backend Initialization
```bash
cd backend
pip install -r requirements.txt

# Terminal 1: Start Redis (if Unix/Docker)
redis-server

# Terminal 2: Start FastAPI Web Server
uvicorn main:app --reload --port 8000

# Terminal 3: Start Celery Background Workers
celery -A tasks worker --loglevel=info
```

### 4. Database Setup
Apply the `backend/db/001_rls_migration.sql` to your Supabase project's SQL Editor to establish all tables, auth functions, and RLS policies.

---

*Engineered for performance, designed for creativity. SJDAS v2.0.*
