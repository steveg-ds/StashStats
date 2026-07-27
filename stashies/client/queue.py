"""Queue client mixin for Ravelry API endpoints."""
from typing import Any, Dict, Optional, List
from .base import BaseRavelryClient


class QueueMixin(BaseRavelryClient):
    """Mixin for Ravelry Queue API endpoints."""
    
    def get_queue(self) -> Optional[List[Dict[str, Any]]]:
        """Get queue items from Ravelry API."""
        res = self.get_request("queue/list.json")
        if res is not None:
            return res.get("queue")
        return None
    
    def add_to_queue(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add item to queue."""
        res = self.post_request("queue/add.json", json_data=item)
        if res is not None:
            return res.get("queue_item")
        return None
    
    def remove_from_queue(self, item_id: int) -> bool:
        """Remove item from queue by ID."""
        res = self.delete_request(f"queue/{item_id}.json")
        return res is not None