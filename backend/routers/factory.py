from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from backend.routers.auth import User, verify_token
from backend.services.factory_stock_service import FactoryStockService

router = APIRouter(
    prefix="/factory",
    tags=["Factory Integration"],
    responses={404: {"description": "Not found"}},
)

class StockMatchRequest(BaseModel):
    design_colors: List[str]  # e.g., ["#FFD700", "#000080"]
    factory_id: str           # e.g., "LOC_SULLURPETA_01"
    threshold: str = "delta-e-2000"

@router.get("/inventory")
async def get_inventory(current_user: User = Depends(verify_token)):
    """Fetch current physical yarn stock levels."""
    service = FactoryStockService.instance()
    return {"items": service.get_inventory()}

# Logic is now moved to FactoryStockService

@router.post("/match-stock")
async def match_stock(request: StockMatchRequest, current_user: User = Depends(verify_token)):
    """
    Automated Color Indexer: 
    Maps design colors to exact physical factory thread inventory.
    """
    service = FactoryStockService.instance()
    matched_results = []
    
    for req_color in request.design_colors:
        best_match = service.match_color_to_stock(req_color)
        
        # Calculate distance for status (reusing internal logic or assuming status is already set)
        matched_results.append({
            "requested_color": req_color,
            "matched_thread": f"T_{best_match.id}",
            "thread_name": best_match.name,
            "status": f"Stock {best_match.status.capitalize()}",
            "hex": best_match.hex
        })
        
    return {
        "factory_id": request.factory_id,
        "algorithm": request.threshold,
        "matches": matched_results
    }
