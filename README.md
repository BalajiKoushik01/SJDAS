# SJDAS v2.0: Autonomous Textile Jacquard Studio
**The Ultimate Power Loom Editor: PyQt6 Desktop Core + Cloud AI Extensions**

SJ-DAS is an enterprise-grade Textile Design Studio built to bridge the gap between human creativity and rigid mechanical loom constraints. By combining a blazing-fast local PyQt6 desktop architecture with asynchronous cloud AI workers, SJDAS outputs 100% production-ready 8-bit Indexed Color BMPs and JC5 machine files directly to industrial Jacquard looms.

---

## 👨‍💻 Author & Contact
**Balaji Koushik**
Email: [balajikoushik01@gmail.com](mailto:balajikoushik01@gmail.com)
GitHub: [BalajiKoushik01](https://github.com/BalajiKoushik01)

---

## 🏗️ Architecture Stack: The Hybrid Approach

### 1. The Core Desktop Engine (v1.0 + v2.0 Upgrades)
- **Framework:** PyQt6 & QFluentWidgets for a professional, standalone Windows/macOS desktop application.
- **Design Patterns:** Factory Pattern (UI Components), Command Pattern (Undo/Redo), Observer Pattern.
- **Math Engine:** OpenCV (Non-Linear Trapezoidal Kali Warping strictly using `cv2.INTER_NEAREST`).
- **Compilation:** Pillow `P` mode (0-compression 8-bit Strict Palette hardware exporting to bypass Windows CE loom limits).

### 2. The Asynchronous Cloud Labor (FastAPI + Celery)
To prevent freezing the desktop UI during massive 12,000x8000px matrix calculations, heavy lifting is piped to an asynchronous cloud stack:
- **API Engine:** FastAPI
- **Background Workers:** Celery + Redis
- **Live Sync:** WebSockets (`/ws/progress/{task_id}`) streaming 0ms UI progress back to the client.

### 3. The B2B Web Portal (Next.js 15)
An enterprise web-dashboard (`web/`) built with React (Fabric.js), Zustand, and Tailwind CSS. Offers "Midnight Industrial" access to cloud sync, AI tracing (SAM 2), and remote factory management.

### 4. Database & Auth (Multi-Tenant Scale)
- **Platform:** Supabase (PostgreSQL)
- **Security:** Strict Row Level Security (RLS) guaranteeing exact `factory_id` tenant isolation.

---

## ✨ Features & Upgrades

### 🎨 Professional Editor Tools
- Selection (Lasso, Magic Wand), Drawing (Brush, Clone Stamp), Auto-Seamless Repeat.
- **Smart Recolor & Factory Stock API:** Calculates CIEDE2000 Delta-E distance between a design's colors and the factory's physical thread inventory (stored in Supabase). 

### 🧠 MiniMax M2.1 AI Integration
Advanced LLM optimized for intelligent design assistance.
- Intelligent Design Analysis (motif types, color harmony, weave structures).
- Conversational AI Assistant (natural language querying for design feasibility).

### 📐 The Kali-Warp Processing Engine (Multi-Panel Output)
Mathematically stretches and tapers motifs (using OpenCV) to construct Multi-Panel (Kali) designs, smoothly stitching up to 12 Kalis into a single giant NumPy array seamlessly.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Windows 10/11 (primary)
- 8GB RAM minimum, 16GB recommended
- Redis Server (for FastAPI background workers)

### 1. Desktop Application Setup

```bash
git clone https://github.com/BalajiKoushik01/SJDAS.git
cd SJDAS

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Launch application (CORRECT ENTRY POINT)
python launcher.py
```

### 2. FastAPI Background Workers Setup
```bash
cd backend
pip install -r requirements.txt

# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Web Server
uvicorn main:app --reload --port 8000

# Terminal 3: Start Celery
celery -A tasks worker --loglevel=info
```

### 3. Next.js Web Portal Setup
```bash
cd web
npm install
npm run dev
```

---

## 🧪 Testing & Code Quality

```bash
# Run all tests with coverage
pytest tests/ -v --cov=sj_das --cov-report=html

# Type checking & Linting
mypy sj_das/utils sj_das/core
ruff check sj_das/ --fix
```
*Current Coverage: 100% on `geometry_utils`, `commands`, and core utilities.*

---

## 🏭 Loom Integration

### Supported Formats
- **BMP Export**: Industry-standard Jacquard format (8-bit indexed, 0-compression)
- **Hook Configuration**: 1000-4000+ hooks supported
- **Color Depth**: 2-256 colors (loom-dependent)

---

**Built with ❤️ for the textile industry**
