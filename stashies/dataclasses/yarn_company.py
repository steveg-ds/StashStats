from pydantic.dataclasses import dataclass
from pydantic import Field

@dataclass
class YarnCompany:
    id: int = Field(alias="id", repr=False)
    name: str = Field(...)
    
