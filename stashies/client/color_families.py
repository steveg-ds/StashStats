"""Color Families client mixin for Ravelry API endpoints."""
from typing import Any, Dict, Optional, List
from .base import BaseRavelryClient


class ColorFamiliesMixin(BaseRavelryClient):
    """Mixin for Ravelry Color Families API endpoints."""
    
    def get_color_families(self) -> Optional[List[Dict[str, Any]]]:
        """Get all color families from Ravelry API."""
        res = self.get_request("yarns/color_families.json")
        if res is not None:
            return res.get("color_families")
        return None