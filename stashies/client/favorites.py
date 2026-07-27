"""FavoritesMixin - Handles Ravelry API favorites endpoints."""
from typing import Optional, Dict, List, Any
from .base import BaseRavelryClient


class FavoritesMixin(BaseRavelryClient):
    """
    FavoritesMixin implements favorites management endpoints for the Ravelry API.
    """

    def get_favorites(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the user's favorites list.
        """
        response = self.get_request("favorites/list.json")
        if response is not None:
            return response.get("favorites")
        return None

    def add_favorite(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a pattern to favorites.
        """
        response = self.post_request("favorites/add.json", json_data=data)
        if response is not None:
            return response.get("favorite")
        return None

    def remove_favorite(self, item_id: int) -> bool:
        """
        Remove a pattern from favorites by its ID.
        """
        response = self.delete_request(f"favorites/{item_id}.json")
        return response is not None