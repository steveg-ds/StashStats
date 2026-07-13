"""Pattern endpoints mixin."""
from typing import Any, Dict, Optional, List

class PatternMixin:
    """Mixin for Ravelry Pattern API endpoints."""
    
    def search_patterns(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search patterns."""
        res = self.get_request("patterns/search.json", params={"query": query})
        if res is not None:
            return res.get("patterns")
        return None

    def get_pattern(self, pattern_id: int) -> Optional[Dict[str, Any]]:
        """Get pattern details."""
        res = self.get_request(f"patterns/{pattern_id}.json")
        if res is not None:
            return res.get("pattern")
        return None
