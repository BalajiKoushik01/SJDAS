from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from backend.routers.auth import get_current_user, User

router = APIRouter()

class DecodeResponse(BaseModel):
    jobId: str
    status: str
    message: str

@router.post("/decode", response_model=DecodeResponse)
async def upload_for_decode(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user)
):
    # Mock decode start
    return {
        "jobId": "mock-decode-job-123",
        "status": "processing",
        "message": f"Decode job started for {file.filename} by user {current_user.username}"
    }

@router.get("/decode/{jobId}")
async def get_decode_status(jobId: str, current_user: User = Depends(get_current_user)):
    return {
        "jobId": jobId,
        "status": "completed",
        "resultDesignId": "mock-design-456"
    }
