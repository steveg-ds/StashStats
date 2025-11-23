from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass
class Colorway:
    id: int = Field(...)

    name: str = Field(...)

    projects: int = Field(..., alias='projects_count')

    stashes: int = Field(..., alias='stashes_count')
