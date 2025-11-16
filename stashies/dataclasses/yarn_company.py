from pydantic.dataclasses import dataclass
from pydantic import Field

from typing import Optional


@dataclass
class YarnCompany:
    name: str = Field(...)
    id: Optional[int] = Field(default=None, alias="id", repr=False)
