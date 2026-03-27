# SJDAS Deployment Guide (Commercial)

This document provides instructions for deploying the SJDAS ecosystem in a production environment.

## 1. Desktop Application (Windows)

The desktop application is the primary tool for designers.

### Build Executable
Run the provided build script to generate a standalone `.exe`:
```bash
python build_desktop.py
```
The output will be located in `dist/SJDAS_Enterprise.exe`.

### Configuration
Users must create a `.env` file in the same directory as the `.exe` (or in the source root) based on `.env.example`.
Key variable: `SJDAS_API_URL` (points to your FastAPI backend).

---

## 2. Cloud Portal (Next.js)

The web portal for project management and AI background tasks.

### Vercel Deployment (Recommended)
1. Import the `web/` directory to Vercel.
2. Set Environment Variables:
   - `NEXT_PUBLIC_API_URL`: URL of your FastAPI backend.
   - `NEXTAUTH_SECRET`: Random string for authentication.
3. Deploy.

### Manual / Ported Deployment
1. Navigate to `/web`.
2. Run `npm install`.
3. Build the production bundle: `npm run build`.
4. Start the server: `npm start`.

---

## 3. Backend Services (FastAPI + Celery)

The heavy-lifting engine for AI and Loom Export.

### Production Setup (Docker Recommended)
1. Use the committed `backend/Dockerfile` and root `docker-compose.yml`.
2. Requirements:
   - **PostgreSQL**: For user data and design metadata.
   - **Redis**: For Celery task queue and WebSocket brokering.
   - **NVIDIA GPU**: Recommended for AI modules (Screenshot Decode, Vision).

### Launching
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Container Launching
```bash
docker compose up --build
```

### Required Production Security Variables
- `APP_ENV=production`
- `JWT_SECRET_KEY=<strong secret>`
- `ALLOW_LEGACY_TOKEN=false`
- `ALLOWED_ORIGINS=https://your-web-domain`
- `ENABLE_JULES_MAINTENANCE_API=false`

---

## 4. Troubleshooting
- **SSL Errors**: Ensure `verify=True` is active in `CloudService` (enforced in v2.1).
- **GPU Issues**: Verify CUDA installation for local AI processing.
- **WebSocket Timeout**: Check Redis connectivity and proxy headers (Nginx/Cloudflare).
