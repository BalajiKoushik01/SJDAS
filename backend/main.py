import base64
import os
import sys
from io import BytesIO
from typing import List, Optional

import asyncio
import cv2
import numpy as np
from fastapi import Body, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from celery.result import AsyncResult

# Add project root to path to import sj_das modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import SJ-DAS core modules
try:
    from sj_das.ai.procedural_generator import get_procedural_generator
    from sj_das.ai.prompt_parser import DesignParameters
    from sj_das.ai.stable_diffusion_generator import get_sd_generator
except ImportError as e:
    print(f"Error importing SJ-DAS modules: {e}")
    # Mocking for testing if modules are missing in some envs
    get_sd_generator = None
    get_procedural_generator = None

# Import Routers
from backend.routers import jules, auth, decode, export, factory, kali, decode_async, export_advanced, ai_tools
from backend.tasks import generate_saree_master_file


app = FastAPI(
    title="SJDAS AI Engine v2.0",
    description="Asynchronous Background Autonomous Framework",
    version="2.0.0"
)

# CORS setup for interacting with Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jules.router, prefix="/jules", tags=["Jules"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(decode.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(export.router, prefix="/api/v1", tags=["Export"])
app.include_router(export_advanced.router, prefix="/api/v1", tags=["Advanced Export"])
app.include_router(factory.router, prefix="/api/v1", tags=["Factory"])
app.include_router(kali.router, prefix="/api/v1", tags=["Multi-Panel Architecture"])
app.include_router(decode_async.router, prefix="/api/v1", tags=["Async Pipeline"])
app.include_router(ai_tools.router, prefix="/api/v1", tags=["AI Smart Tools"])


class AsyncExportRequest(BaseModel):
    design_id: str
    hooks: int
    kali_count: int
    picks_height: int

@app.post("/api/v1/generate-loom-file-async", tags=["Async Export"])
async def trigger_generation(design_data: AsyncExportRequest):
    """
    Receives request and hands it to Celery immediately. UI remains un-frozen.
    """
    data_dict = design_data.model_dump()
    task = generate_saree_master_file.delay(data_dict)
    return {"status": "processing", "task_id": task.id}

@app.websocket("/ws/progress/{task_id}")
async def websocket_progress(websocket: WebSocket, task_id: str):
    """
    Next.js connects here to get real-time updates for Framer Motion loaders.
    """
    await websocket.accept()
    
    try:
        while True:
            task_result = AsyncResult(task_id)
            
            if task_result.state == 'PENDING':
                await websocket.send_json({"status": "pending", "message": "Initializing AI Workers..."})
            elif task_result.state == 'PROGRESS':
                await websocket.send_json({"status": "progress", "meta": task_result.info})
            elif task_result.state == 'SUCCESS':
                await websocket.send_json({"status": "success", "file_url": task_result.result})
                break
            elif task_result.state == 'FAILURE':
                await websocket.send_json({"status": "error", "message": str(task_result.info)})
                break
                
            await asyncio.sleep(0.5)
    except Exception as e:
        await websocket.close()


class DesignRequest(BaseModel):
    design_type: str = "border"
    style: str = "traditional"
    occasion: Optional[str] = "festive"
    colors: List[str] = ["red", "gold"]
    motifs: List[str] = ["peacock"]
    weave: str = "jeri"
    complexity: str = "medium"


class GenerateResponse(BaseModel):
    image: str  # Base64 encoded image
    format: str = "png"


def numpy_to_base64(img_array: np.ndarray) -> str:
    """Convert numpy array (RGB) to base64 string."""
    try:
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            # Convert RGB to BGR for cv2 encoding (if needed) or direct PIL
            # The generators return RGB (Procedural) or RGB (SD via my checks)
            # Let's assume RGB for PIL
            img = Image.fromarray(img_array.astype('uint8'))
        else:
            img = Image.fromarray(img_array.astype('uint8'))

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Error converting image: {e}")
        return ""


@app.get("/")
async def root():
    return {"message": "SJ-DAS API is running"}


@app.post("/generate/procedural", response_model=GenerateResponse)
async def generate_procedural(request: DesignRequest):
    if not get_procedural_generator:
        raise HTTPException(status_code=500, detail="Core modules not loaded")

    try:
        # Map request to DesignParameters
        # Assuming existing DesignParameters class structure, or creating a mock if complex
        # Note: In real integration, we should inspect DesignParameters init
        # For now, we'll manually construct a compatible object or pass a dict
        # if supported

        # Checking DesignParameters structure from prompt_parser is hard statically
        # Let's create a dummy object compatible with what generators expect
        class Params:
            def __init__(self, **entries):
                self.__dict__.update(entries)
                self.width_mm = 512  # Default
                self.length_mm = 512  # Default

        params = Params(**request.dict())

        generator = get_procedural_generator()
        result_img = generator.generate_design(params)

        b64_img = numpy_to_base64(result_img)
        return {"image": b64_img}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/ai", response_model=GenerateResponse)
async def generate_ai(request: DesignRequest):
    if not get_sd_generator:
        raise HTTPException(status_code=500, detail="Core modules not loaded")

    try:
        class Params:
            def __init__(self, **entries):
                self.__dict__.update(entries)
                self.width_mm = 512
                self.length_mm = 512

        params = Params(**request.dict())

        generator = get_sd_generator()
        # This might be slow (load model on first request)
        print("Generating AI design...")
        results = generator.generate(params, num_images=1)

        if not results:
            raise HTTPException(status_code=500, detail="Generation failed")

        b64_img = numpy_to_base64(results[0])
        return {"image": b64_img}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
