"""Pattern endpoints mixin."""
from typing import Any, Dict, Optional, List

class PatternMixin:
    """Mixin for Ravelry Pattern API endpoints."""
    
    def search_patterns(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search patterns."""
        raise NotImplementedError

    def get_pattern(self, pattern_id: int) -> Optional[Dict[str, Any]]:
        """Get pattern details."""
        raise NotImplementedError
