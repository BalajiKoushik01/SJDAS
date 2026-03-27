"""
Advanced Hardware Exporter for Jacquard Looms.
Generates specialized formats (JC5, WIF, DAT, DXF) from the master matrix.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import numpy as np
import cv2
import os
from backend.routers.auth import verify_token
from backend.services.float_checker import check_floats
from backend.services.jc5_service import JC5Encoder

router = APIRouter(
    prefix="/export-advanced",
    tags=["Export Advanced"],
    responses={404: {"description": "Not found"}},
)

# Initialize production encoders
jc5_encoder = JC5Encoder(hooks=600)  # Default, can be overridden by loom config

@router.post("/jc5")
async def export_jc5(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """Export to Staubli JC5 format after validating floats."""
    file_bytes = np.frombuffer(await file.read(), np.uint8)
    image_matrix = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    
    if image_matrix is None:
        raise HTTPException(status_code=400, detail="Invalid matrix uploaded")
        
    _, binary_matrix = cv2.threshold(image_matrix, 127, 1, cv2.THRESH_BINARY)
    float_report = check_floats(binary_matrix, max_float=15)
    
    if float_report["status"] == "FAIL":
        raise HTTPException(status_code=422, detail="Float violations prevented JC5 export.")

    out_file = "production.jc5"
    jc5_encoder.encode(binary_matrix, out_file)
    
    return FileResponse(out_file, media_type="application/octet-stream", filename=out_file)

@router.post("/wif")
async def export_wif(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """Export to WIF (Weaving Information File)."""
    # Placeholder for WIF Generation (which is plain text INI style)
    out_file = "production.wif"
    with open(out_file, 'w') as f:
        f.write("[WIF]\nVersion=1.1\n[WEAVE]\n")
    return FileResponse(out_file, media_type="text/plain", filename=out_file)
