"""Ravelry API client for stash endpoints."""
from typing import Optional, List, Dict, Any
class StashMixin:
    """
    Ravelry API Client subclass for Stash-related requests.
    """

    def get_stash_list(self, username: str) -> Optional[List[Dict[str, Any]]]:
        """
        GET request to people/{username}/stash/unified/list.json with page size 100
        and aggregates all pages.
        """
        all_items = []
        page = 1
        while True:
            result = self.get_request(
                endpoint=f"people/{username}/stash/unified/list.json",
                params={"page_size": 100, "page": page}
            )
            if result is None:
                if page == 1:
                    return None
                break
            
            unified = result.get("unified_stash", [])
            if not unified:
                break
            
            all_items.extend(unified)
            if len(unified) < 100:
                break
            page += 1
        return all_items

    def create_stash(self, username: str, stash_data: dict) -> Optional[dict]:
        """
        POST request to people/{username}/stash/create.json with stash data.
        """
        return self.post_request(
            endpoint=f"people/{username}/stash/create.json",
            json_data=stash_data
        )

    def update_stash(self, username: str, stash_id: int, stash_data: dict) -> Optional[dict]:
        """
        PUT request to people/{username}/stash/{stash_id}.json with stash data.
        """
        return self.put_request(
            endpoint=f"people/{username}/stash/{stash_id}.json",
            json_data=stash_data
        )

    def delete_stash(self, username: str, stash_id: int, stash_type: str = "yarn") -> bool:
        """
        DELETE request to people/{username}/stash/{stash_id}.json.
        Returns True on success, False on failure.
        """
        result = self.delete_request(
            endpoint=f"people/{username}/stash/{stash_id}.json",
            params={"stash_type": stash_type}
        )
        return result is not None
