"""FavoritesMixin - Handles Ravelry API favorites endpoints."""
from typing import Any, Dict, List, Optional
from stashies.client.base import BaseRavelryClient


class FavoritesMixin(BaseRavelryClient):
    """
    FavoritesMixin implements favorites management endpoints for the Ravelry API.
    """

    def get_favorites(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the user's favorites list.
        """
        res = self.get_request("favorites/list.json")
        if res is not None:
            return res.get("favorites")
        return None

    def add_favorite(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a pattern to favorites.
        """
        res = self.post_request("favorites/add.json", json_data=data)
        if res is not None:
            return res.get("favorite") or res.get("queue_item")
        return None

    def remove_favorite(self, item_id: int) -> bool:
        """
        Remove a pattern from favorites by its ID.
        """
        res = self.delete_request(f"favorites/{item_id}.json")
        return res is not None