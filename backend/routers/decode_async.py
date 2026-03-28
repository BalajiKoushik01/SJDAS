"""
SJDAS v2 — Decode Async Router
Accepts image upload, enqueues Celery decode pipeline task, returns task_id.
WebSocket progress is served via /ws/progress/{task_id} in main.py.
"""
import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from backend.routers.auth import User, verify_token
from backend.services.contracts import normalize_decode_result

router = APIRouter()


@router.post("/decode-async")
async def decode_async(
    file: UploadFile = File(...),
    hook_count: int = Form(600),
    ends_ppi: int = Form(80),
    color_count: int = Form(6),
    style_override: Optional[str] = Form(None),
    current_user: User = Depends(verify_token),
):
    """
    SJDAS v2 Screenshot → Loom Pipeline (Async).

    Accepts any saree image (PNG/JPG/WEBP/PDF), validates it,
    saves to temp storage, and enqueues the 6-step Celery decode task.

    Returns a task_id to poll via WebSocket /ws/progress/{task_id}.
    """
    if not file.content_type or not file.content_type.startswith(("image/", "application/pdf")):
        raise HTTPException(status_code=400, detail="File must be an image or PDF.")

    # Cap file size at 50MB
    MAX_SIZE = 50 * 1024 * 1024
    image_bytes = await file.read()
    if len(image_bytes) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")

    # Save to temp dir
    task_id = str(uuid.uuid4())
    temp_dir = "temp_decode"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{task_id}_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    # Enqueue Celery task
    try:
        from backend.tasks import run_decode_pipeline
        task = run_decode_pipeline.delay({
            "task_id": task_id,
            "image_path": temp_path,
            "hook_count": hook_count,
            "ends_ppi": ends_ppi,
            "color_count": color_count,
            "style_override": style_override,
        })
        return JSONResponse({
            "status": "queued", 
            "task_id": task.id,
            "internal_ref": task_id
        })
    except ImportError:
        # Fallback for environments without Celery installed
        return JSONResponse({
            "status": "error",
            "message": "Celery worker not installed. Asynchronous processing unavailable.",
            "task_id": task_id
        }, status_code=501)
    except Exception as e:
        # Celery is installed but broker might be down
        return JSONResponse({
            "status": "error",
            "message": f"Pipeline Broker Error: {str(e)}",
            "task_id": task_id
        }, status_code=503)


@router.get("/decode-async/{task_id}")
async def get_decode_result(task_id: str, current_user: User = Depends(verify_token)):
    """Poll decode result by task_id (alternative to WebSocket)."""
    try:
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        if result.state == "SUCCESS":
            normalized = normalize_decode_result(result.result if isinstance(result.result, dict) else {})
            return {"status": "success", "result": normalized.model_dump()}
        elif result.state == "FAILURE":
            return {"status": "error", "message": str(result.info)}
        else:
            return {"status": "pending", "state": result.state}
    except Exception:
        return {"status": "unknown", "task_id": task_id}
