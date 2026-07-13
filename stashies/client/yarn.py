"""Ravelry API client for yarn endpoints."""
from typing import List, Optional

class YarnMixin:
    """
    Ravelry API client wrapper specifically for Yarn endpoints.
    """

    def search_yarn(self, query: str, sort: str = "best") -> Optional[List[dict]]:
        """
        GET request to yarns/search.json.
        Return list of yarn dictionaries from the response's yarns key.
        """
        params = {"query": query, "sort": sort}
        result = self.get_request(endpoint="yarns/search.json", params=params)
        if result and isinstance(result, dict):
            return result.get("yarns")
        return None

    def get_yarn(self, yarn_id: int) -> Optional[dict]:
        """
        GET request to yarns/{yarn_id}.json.
        Return the yarn dictionary from yarn key.
        """
        result = self.get_request(endpoint=f"yarns/{yarn_id}.json")
        if result and isinstance(result, dict):
            return result.get("yarn")
        return None
