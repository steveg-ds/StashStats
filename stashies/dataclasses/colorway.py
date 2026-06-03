"""Pydantic dataclass for a Ravelry yarn colorway."""
from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass
class Colorway:
    """
    Represents a single colorway variant of a Ravelry yarn.

    - Properties:
        - id (int): Ravelry colorway ID.
        - name (str): Colorway display name.
        - projects (int): Number of Ravelry projects using this colorway.
        - stashes (int): Number of Ravelry stashes containing this colorway.
    """

    id: int = Field(...)
    '''Ravelry colorway ID.'''

    name: str = Field(...)
    '''Colorway display name.'''

    projects: int = Field(..., alias='projects_count')
    '''Number of Ravelry projects using this colorway.'''

    stashes: int = Field(..., alias='stashes_count')
    '''Number of Ravelry stashes containing this colorway.'''
