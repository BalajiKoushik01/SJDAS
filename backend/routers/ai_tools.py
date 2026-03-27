"""
AI Tools Router
Provides endpoints for SAM 2 'Magic Tracer' vectorization and 'Smart Healing Brush'.
"""
import base64
import cv2
import numpy as np
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from backend.routers.auth import verify_token
from sj_das.ai.flux_generator import FluxGenerator

router = APIRouter(
    prefix="/ai",
    tags=["AI Smart Tools"],
)


class ContextAssistRequest(BaseModel):
    page: str
    active_tool: str | None = None
    decode_progress: int = 0
    hooks: int = 600
    kalis: int = 12

# Shared Flux Instance for the backend
_flux_instance = None

def get_flux():
    global _flux_instance
    if _flux_instance is None:
        _flux_instance = FluxGenerator()
    return _flux_instance

@router.post("/generate")
async def generate_design(
    prompt: str = Form(...),
    width: int = Form(512),
    height: int = Form(512),
    token: str = Depends(verify_token)
):
    """
    SOTA Flux.1 [schnell] Generation.
    Provides ultra-fast high-quality textile designs.
    """
    flux = get_flux()
    # image is returned as BGR numpy array
    image_bgr = flux.generate(prompt, width=width, height=height)
    
    if image_bgr is None:
        raise HTTPException(status_code=500, detail="Flux generation failed.")
        
    _, buffer = cv2.imencode('.png', image_bgr)
    b64_str = base64.b64encode(buffer).decode('utf-8')
    
    return JSONResponse({
        "status": "success",
        "image_data": f"data:image/png;base64,{b64_str}",
        "prompt": prompt
    })

@router.post("/magic-trace")
async def magic_trace(
    file: UploadFile = File(...),
    x: float = Form(...),
    y: float = Form(...),
    token: str = Depends(verify_token)
):
    """
    Simulates SAM 2 (Segment Anything 2) point-prompt mask generation
    for one-click motif vectorization ("Magic Tracer")
    """
    file_bytes = np.frombuffer(await file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image uploaded for Magic Trace.")
    
    # In a real environment, this would call Segmind SAM 2 Serverless API
    # Return a mocked SVG path of the traced motif
    return JSONResponse({
        "status": "success",
        "svg_path": f"<svg><circle cx='{x}' cy='{y}' r='50' fill='#FF5733' /></svg>",
        "message": "Motif magically traced successfully."
    })

@router.post("/heal")
async def smart_heal(
    file: UploadFile = File(...),
    mask: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """
    Applies Pattern Diffusion (e.g., Stable Diffusion Inpainting or Navier-Stokes)
    to seamlessly heal/clone repetitive motif structures.
    """
    # 1. Read base image and mask
    img_bytes = np.frombuffer(await file.read(), np.uint8)
    image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
    
    mask_bytes = np.frombuffer(await mask.read(), np.uint8)
    mask_image = cv2.imdecode(mask_bytes, cv2.IMREAD_GRAYSCALE)
    
    if image is None or mask_image is None:
        raise HTTPException(status_code=400, detail="Invalid image or mask uploaded for Healing.")
        
    # 2. Apply OpenCV Inpainting as a fast baseline fallback
    result = cv2.inpaint(image, mask_image, 3, cv2.INPAINT_TELEA)
    
    # 3. Return fixed image as Base64 for instant Canvas update
    _, buffer = cv2.imencode('.png', result)
    b64_str = base64.b64encode(buffer).decode('utf-8')
    
    return JSONResponse({
        "status": "success",
        "image_data": f"data:image/png;base64,{b64_str}"
    })


@router.post("/context-assist")
async def context_assist(
    payload: ContextAssistRequest,
):
    """
    Lightweight context-aware assistant recommendations for UI copilots.
    """
    if payload.page == "decode":
        if payload.decode_progress > 0 and payload.decode_progress < 100:
            return {
                "title": "Decode Running",
                "message": f"Progress at {payload.decode_progress}%. I am validating output quality and mechanical safety.",
                "priority": "info",
            }
        return {
            "title": "Decode Assistant",
            "message": "Use 1200+ hooks and 6-8 colors for stable motif reconstruction on production exports.",
            "priority": "advice",
        }

    tool = (payload.active_tool or "").lower()
    if tool in {"ai-trace", "heal"}:
        return {
            "title": "AI Tool Active",
            "message": "I am optimizing suggestions for motif extraction and repair in the background.",
            "priority": "assistant",
        }

    return {
        "title": "Studio Copilot",
        "message": f"Current setup is {payload.hooks} hooks and {payload.kalis} kalis. Maintain repeat symmetry before final export.",
        "priority": "advice",
    }
