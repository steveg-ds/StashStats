"""Pydantic models for constructing Ravelry stash POST/PUT request payloads."""
from pydantic import BaseModel, Field
from typing import Optional

class PackPost(BaseModel):
    """
    Optional pack details nested inside a stash creation payload.

    - Properties:
        - skeins (float | None): Number of skeins to record.
    """
    skeins: Optional[float] = Field(default=None)

class StashPost(BaseModel):
    """
    Payload model for creating or updating a Ravelry stash entry.

    - Properties:
        - yarn_id (int): Ravelry yarn ID to stash.
        - colorway_name (str | None): Colorway name string.
        - dye_lot (str | None): Dye lot identifier.
        - location (str | None): Physical storage location.
        - notes (str | None): Free-text notes.
        - pack (PackPost | None): Optional pack quantity details.
        - stash_status_id (int): Ravelry status code; 1 = active.
    """
    yarn_id: int
    colorway_name: Optional[str] = Field(default=None)
    dye_lot: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    pack: Optional[PackPost] = Field(default=None)
    stash_status_id: int = Field(default=1)  # 1 = active
    '''Ravelry stash status code. 1 = active, 2 = held, 3 = stash-away.'''
