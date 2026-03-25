from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.routers.auth import get_current_user, User

router = APIRouter()

class ExportRequest(BaseModel):
    designId: str
    format: str
    hook_count: int

class ExportResponse(BaseModel):
    jobId: str
    status: str

@router.post("/export", response_model=ExportResponse)
async def start_export(
    request: ExportRequest, 
    current_user: User = Depends(get_current_user)
):
    return {
        "jobId": f"mock-export-{request.designId}",
        "status": "pending"
    }

@router.get("/export/{jobId}")
async def get_export_status(jobId: str, current_user: User = Depends(get_current_user)):
    return {
        "jobId": jobId,
        "status": "completed",
        "downloadUrl": f"https://mock-s3-bucket/exports/{jobId}/design.bmp"
    }
