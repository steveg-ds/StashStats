from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class StashSyncState(BaseModel):
    """Pydantic V2 model enforcing type validation for stash sync tracking state."""
    stash_id: str
    is_dirty: bool = False
    last_synced_at: Optional[datetime] = None
    sync_error: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
