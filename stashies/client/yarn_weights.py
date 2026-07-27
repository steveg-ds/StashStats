"""Yarn Weights client mixin for Ravelry API endpoints."""
from typing import Any, Dict, Optional, List
from .base import BaseRavelryClient


class YarnWeightsMixin(BaseRavelryClient):
    """Mixin for Ravelry Yarn Weights API endpoints."""
    
    def get_yarn_weights(self) -> Optional[List[Dict[str, Any]]]:
        """Get all yarn weights from Ravelry API."""
        res = self.get_request("yarns/yarn_weights.json")
        if res is not None:
            return res.get("yarn_weights")
        return None