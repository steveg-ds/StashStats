"""Pydantic dataclass for a Ravelry yarn company."""
from pydantic.dataclasses import dataclass
from pydantic import Field

from typing import Optional


@dataclass
class YarnCompany:
    """
    Represents a yarn manufacturer or distributor on Ravelry.

    - Properties:
        - name (str): Company display name.
        - id (int | None): Ravelry company ID.
    """

    name: str = Field(...)
    '''Company display name.'''

    id: Optional[int] = Field(default=None, alias="id", repr=False)
    '''Ravelry company ID.'''
