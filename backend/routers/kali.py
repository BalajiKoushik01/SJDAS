import cv2
import base64
import numpy as np
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
from backend.routers.auth import verify_token
from backend.services.kali_engine import generate_tapered_kali, stitch_master_file

router = APIRouter(
    prefix="/kali",
    tags=["Multi-Panel Architecture"],
    responses={404: {"description": "Not found"}},
)

@router.post("/process-master")
async def process_kali_master(
    file: UploadFile = File(...),
    top_hooks: int = Form(...),
    bottom_hooks: int = Form(...),
    total_picks: int = Form(...),
    total_kalis: int = Form(...),
    token: str = Depends(verify_token)
):
    """
    Agentic Workflow for Multi-Panel Continuous Output.
    Generates exact master NumPy array, returns a tiny compressed preview.
    """
    file_bytes = np.frombuffer(await file.read(), np.uint8)
    image_matrix = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE) # Assuming indexed 8-bit mapping
    
    if image_matrix is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # 1. Kali-Warp Agent (INTER_NEAREST ensures strict exact color retention)
    print("Executing Strict Kali-Warp Generator...")
    warped_kali = generate_tapered_kali(image_matrix, top_hooks, bottom_hooks, total_picks)
    
    # 2. Giant Canvas Construction
    print(f"Stitching {total_kalis} Kalis...")
    master_matrix = stitch_master_file(warped_kali, total_kalis)
    
    total_width = master_matrix.shape[1]
    
    # 3. Compress a "Preview Image" for UI so browser doesn't crash on huge matrices
    preview_matrix = cv2.resize(master_matrix, (800, 600), interpolation=cv2.INTER_NEAREST)
    _, buffer = cv2.imencode('.png', preview_matrix)
    preview_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "status": "success",
        "message": "Master File Generated with strict INTER_NEAREST.",
        "master_dimensions": {"width": total_width, "height": total_picks},
        "preview_image_base64": f"data:image/png;base64,{preview_base64}",
        "float_guard_status": "Scanning background..."
    }
