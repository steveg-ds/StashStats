from pydantic import BaseModel, Field
from typing import Optional

class PackPost(BaseModel):
    skeins: Optional[float] = Field(default=None)

class StashPost(BaseModel):
    yarn_id: int
    colorway_name: Optional[str] = Field(default=None)
    dye_lot: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    pack: Optional[PackPost] = Field(default=None)
    stash_status_id: int = Field(default=1)  # 1 = active
