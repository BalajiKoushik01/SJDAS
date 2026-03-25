from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from backend.routers.auth import verify_token

router = APIRouter(
    prefix="/api/v1/factory",
    tags=["Factory Integration"],
    responses={404: {"description": "Not found"}},
)

class StockMatchRequest(BaseModel):
    design_colors: List[str]  # e.g., ["#FFD700", "#000080"]
    factory_id: str           # e.g., "LOC_SULLURPETA_01"
    threshold: str = "delta-e-2000"

# Mock Database of Factory Threads
FACTORY_DB = {
    "LOC_SULLURPETA_01": [
        {"thread_id": "T_GOLD_01", "name": "Gold Zari", "hex": "#FFDF00"},
        {"thread_id": "T_NAVY_01", "name": "Navy Silk", "hex": "#000080"},
        {"thread_id": "T_RED_01", "name": "Crimson Silk", "hex": "#DC143C"}
    ]
}

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert HEX color to RGB tuple."""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) # type: ignore

def color_distance_squared(c1: str, c2: str) -> int:
    """Simplified Euclidean distance fallback for color matching."""
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return (r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2

@router.post("/match-stock")
async def match_stock(request: StockMatchRequest, token: str = Depends(verify_token)):
    """
    Automated Color Indexer: 
    Maps design colors to exact physical factory thread inventory.
    """
    factory_inventory = FACTORY_DB.get(request.factory_id)
    
    if not factory_inventory:
         raise HTTPException(status_code=404, detail="Factory inventory not found.")
    
    matched_results = []
    
    # 1. Loop through requested image colors
    for req_color in request.design_colors:
        best_match = factory_inventory[0]
        min_dist = float('inf')
        
        # 2. Find closest thread in physical stock (Approximating CIEDE2000 with Euclidean for now)
        for thread in factory_inventory:
            dist = color_distance_squared(req_color, thread["hex"])
            if dist < min_dist:
                min_dist = dist
                best_match = thread
                
        # 3. Assess threshold
        status = "Stock Validated" if min_dist < 5000 else "Warning: Distant Match"
        
        matched_results.append({
            "requested_color": req_color,
            "matched_thread": best_match["thread_id"],
            "thread_name": best_match["name"],
            "status": status,
            "delta_distance": min_dist
        })
        
    return {
        "factory_id": request.factory_id,
        "algorithm": request.threshold,
        "matches": matched_results
    }
