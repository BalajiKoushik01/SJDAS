import os
import tempfile
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.routers.auth import User, verify_token
from backend.services.decode_service import run_full_pipeline, DecodeParams

router = APIRouter(prefix="/api/v1")

class DecodeResponse(BaseModel):
    job_id: str
    status: str
    message: str
    result: Optional[dict] = None

@router.post("/decode", response_model=DecodeResponse)
async def upload_for_decode(
    file: UploadFile = File(...),
    hook_count: int = Form(600),
    ends_ppi: int = Form(80),
    color_count: int = Form(6),
    style_override: Optional[str] = Form(None),
    current_user: User = Depends(verify_token)
):
    """
    SJDAS v2.0 Agentic Loop Pipeline (Synchronous Wrapper)
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Save to temp file for the service
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        params = DecodeParams(
            image_path=temp_path,
            hook_count=hook_count,
            ends_ppi=ends_ppi,
            color_count=color_count,
            style_override=style_override
        )
        
        # In this 'synchronous' version, we run the pipeline immediately.
        # Note: This might timeout for very large images, hence decode_async exists.
        result = run_full_pipeline(params)
        
        return {
            "job_id": f"job_{uuid.uuid4().hex[:8]}",
            "status": "completed",
            "message": "Decode successful",
            "result": vars(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/decode/{job_id}")
async def get_decode_status(job_id: str, current_user: User = Depends(verify_token)):
    # Since this router is synchronous, we don't have a status DB yet.
    # We return a generic check (legacy path).
    return {
        "job_id": job_id,
        "status": "active",
        "message": "Status polling is recommended via the /tasks endpoint."
    }
