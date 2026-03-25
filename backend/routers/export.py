import os
import cv2
import numpy as np
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.routers.auth import verify_token
from backend.services.bmp_compiler import export_to_indexed_bmp

router = APIRouter(
    prefix="/api/v1/export",
    tags=["Export"],
    responses={404: {"description": "Not found"}},
)

class ExportResponse(BaseModel):
    jobId: str
    status: str
    url: str

from backend.services.float_checker import check_floats

# ... (inside router)

@router.post("/generate-loom-file")
async def generate_loom_file(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """
    Receives the giant UI matrix from frontend (or reads the shadow canvas), 
    and mathematically exports to the strict 8-bit indexed BMP format.
    Runs proactive Float Checking before export.
    """
    # 1. Read the uploaded raw array
    file_bytes = np.frombuffer(await file.read(), np.uint8)
    image_matrix = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE) # The UI must send an 8-bit single-channel image
    
    if image_matrix is None:
        raise HTTPException(status_code=400, detail="Invalid matrix uploaded for export")
        
    # 2. Strict Machine Header Palette (Simulated grab from Factory API)
    # 0 = Ground, 1 = Butta, 2 = Extra Zari
    factory_inventory_palette = [
        (0, 0, 128),     # Navy
        (255, 215, 0),   # Gold
        (192, 192, 192)  # Silver
    ]
    
    # 3. Float Validation
    # We convert grayscale to binary (0, 1) to test warp/weft floats
    _, binary_matrix = cv2.threshold(image_matrix, 127, 1, cv2.THRESH_BINARY)
    float_report = check_floats(binary_matrix, max_float=15)
    
    if float_report["status"] == "FAIL":
        # Reject export if critical floats exist
        raise HTTPException(
            status_code=422, 
            detail={
                "message": "Export failed due to float violations.",
                "report": float_report
            }
        )
    
    # 4. Export to Indexed BMP
    output_filename = "saree_production_file.bmp"
    export_to_indexed_bmp(
        master_matrix=image_matrix, 
        stock_colors=factory_inventory_palette,
        output_filename=output_filename
    )
    
    # In a real system, upload to S3 or serve securely. Here we return the file locally.
    return FileResponse(
        path=output_filename, 
        media_type="image/bmp", 
        filename=output_filename
    )

@router.get("/status/{jobId}")
async def get_export_status(jobId: str, token: str = Depends(verify_token)):
    return {
        "jobId": jobId,
        "status": "completed",
        "url": "/mock/download/link.bmp"
    }
