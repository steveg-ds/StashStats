"""Favorites client mixin for Ravelry API endpoints."""
from typing import Any, Dict, Optional, List
from .base import BaseRavelryClient


class FavoritesMixin(BaseRavelryClient):
    """Mixin for Ravelry Favorites API endpoints."""
    
    def get_favorites(self) -> Optional[List[Dict[str, Any]]]:
        """Get user favorites from Ravelry API."""
        res = self.get_request("favorites/list.json")
        if res is not None:
            return res.get("favorites")
        return None
    
    def add_favorite(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add item to favorites."""
        res = self.post_request("favorites/add.json", json_data=item)
        if res is not None:
            return res.get("favorite")
        return None
    
    def remove_favorite(self, item_id: int) -> bool:
        """Remove item from favorites by ID."""
        res = self.delete_request(f"favorites/{item_id}.json")
        return res is not None