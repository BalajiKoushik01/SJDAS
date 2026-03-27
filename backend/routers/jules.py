from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import subprocess
import sys
import os
from backend.routers.auth import User, require_roles

router = APIRouter()

class MaintenanceRequest(BaseModel):
    fix: bool = False
    upgrade: bool = False
    security: bool = False
    types: bool = False

class MaintenanceResponse(BaseModel):
    status: str
    output: str
    issues_found: int = 0
    issues_fixed: int = 0

@router.post("/run", response_model=MaintenanceResponse)
async def run_maintenance(
    request: MaintenanceRequest,
    current_user: User = Depends(require_roles(["admin"])),
):
    """Run Jules Maintenance Agent via API."""
    try:
        if os.getenv("ENABLE_JULES_MAINTENANCE_API", "false").lower() != "true":
            raise HTTPException(
                status_code=403,
                detail="Jules maintenance API is disabled. Set ENABLE_JULES_MAINTENANCE_API=true to enable.",
            )
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        script_path = os.path.join(project_root, 'tools', 'jules_maintenance.py')
        
        args = [sys.executable, script_path]
        if request.fix:
            args.append("--fix")
        if request.upgrade:
            args.append("--upgrade")
        if request.security:
            args.append("--security")
        if request.types:
            args.append("--types")
            
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout + "\n" + result.stderr,
            "issues_found": result.stdout.count("[NOTE]") + result.stdout.count("[WARNING]") + result.stdout.count("[ERROR]"),
            "issues_fixed": result.stdout.count("✨ Fixed")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
