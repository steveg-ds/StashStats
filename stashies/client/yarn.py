"""Yarn endpoints mixin."""
from typing import Any, Dict, Optional, List

class YarnMixin:
    """Mixin for Ravelry Yarn API endpoints."""
    
    def search_yarn(self, query: str, sort: str = "best") -> Optional[List[Dict[str, Any]]]:
        """Search yarns."""
        raise NotImplementedError

    def get_yarn(self, yarn_id: int) -> Optional[Dict[str, Any]]:
        """Get yarn details."""
        raise NotImplementedError
