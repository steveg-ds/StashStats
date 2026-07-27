"""QueueMixin - Handles Ravelry API queue endpoints."""
from typing import Any, Dict, List, Optional
from .base import BaseRavelryClient


class QueueMixin(BaseRavelryClient):
    """
    QueueMixin implements queue management endpoints for the Ravelry API.
    """

    def get_queue(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get the user's queue list.
        """
        res = self.get_request("queue/list.json")
        if res is not None:
            return res.get("queue") or res.get("queued_projects")
        return None

    def add_to_queue(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a pattern to the queue.
        """
        res = self.post_request("queue/add.json", json_data=data)
        if res is not None:
            return res.get("queue_item")
        return None

    def remove_from_queue(self, item_id: int) -> bool:
        """
        Remove a pattern from the queue by its ID.
        """
        res = self.delete_request(f"queue/{item_id}.json")
        return res is not None