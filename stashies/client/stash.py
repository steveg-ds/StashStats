"""User Stash endpoints mixin."""
from typing import Any, Dict, Optional, List

class StashMixin:
    """Mixin for Ravelry Stash API endpoints."""
    
    def get_stash_list(self, username: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch all stash entries for user."""
        raise NotImplementedError

    def create_stash(self, username: str, stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new stash entry."""
        raise NotImplementedError

    def update_stash(self, username: str, stash_id: int, stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing stash entry."""
        raise NotImplementedError

    def delete_stash(self, username: str, stash_id: int, stash_type: str = "yarn") -> bool:
        """Delete a stash entry."""
        raise NotImplementedError
