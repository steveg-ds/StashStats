"""QueueMixin - Handles Ravelry API queue endpoints."""
from stashies.client.base import BaseRavelryClient


class QueueMixin(BaseRavelryClient):
    """
    QueueMixin implements queue management endpoints for the Ravelry API.
    """

    def get_queue(self):
        """
        Get the user's queue list.
        """
        response = self.get_request("queue/list.json")
        if not response:
            return None
        return response

    def add_to_queue(self, data):
        """
        Add a pattern to the queue.
        """
        response = self.post_request("queue/add.json", json_data=data)
        return response

    def remove_from_queue(self, item_id: int):
        """
        Remove a pattern from the queue by its ID.
        """
        response = self.delete_request(f"queue/{item_id}.json")
        return response is not None