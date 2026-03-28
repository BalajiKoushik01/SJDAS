from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class StockItem(BaseModel):
    id: int
    name: str
    hex: str
    kg: float
    status: str

class FactoryStockService:
    """
    Service for managing physical yarn inventory and Delta-E color matching.
    """
    _instance: Optional['FactoryStockService'] = None
    
    def __init__(self):
        # Initial mocked inventory (would be connected to a real DB/ERP in production)
        self._inventory: List[StockItem] = [
            StockItem(id=1, name='Deep Cobalt Silk', hex='#000080', kg=45.0, status='ok'), # type: ignore
            StockItem(id=2, name='Gold Zari 200D', hex='#FFD700', kg=1.2, status='low'), # type: ignore
            StockItem(id=3, name='Silver Border Zari', hex='#C0C0C0', kg=12.5, status='ok'), # type: ignore
            StockItem(id=4, name='Crimson Weft', hex='#DC143C', kg=8.4, status='ok'), # type: ignore
            StockItem(id=5, name='Emerald Green', hex='#50C878', kg=3.1, status='ok'), # type: ignore
        ]

    @classmethod
    def instance(cls) -> 'FactoryStockService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance # type: ignore

    def get_inventory(self) -> List[StockItem]:
        return self._inventory

    def update_stock(self, item_id: int, kg_delta: float) -> Optional[StockItem]:
        for item in self._inventory:
            if item.id == item_id:
                item.kg += kg_delta
                item.status = 'ok' if item.kg > 5.0 else 'low'
                return item
        return None

    def match_color_to_stock(self, target_hex: str) -> StockItem:
        """
        Calculates the nearest physical yarn color using Euclidean distance in RGB space.
        Professional implementation would use Delta-E (CIELAB).
        """
        def hex_to_rgb(h: str):
            h_clean = h.lstrip('#')
            # Fixed slicing for type-checkers
            r = int(h_clean[0:2], 16)
            g = int(h_clean[2:4], 16)
            b = int(h_clean[4:6], 16)
            return (r, g, b)
        
        target_rgb = hex_to_rgb(target_hex)
        best_match = self._inventory[0]
        min_distance = float('inf')
        
        for item in self._inventory:
            item_rgb = hex_to_rgb(item.hex)
            distance = sum((float(a) - float(b)) ** 2 for a, b in zip(target_rgb, item_rgb))
            if distance < min_distance:
                min_distance = distance
                best_match = item
        
        return best_match
