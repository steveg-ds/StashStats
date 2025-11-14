from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import List, Union, Dict, Any

from .yarn_company import YarnCompany
from .yarn_fiber import YarnFiber

@dataclass
class Yarn:

    discontinued: bool = Field(...)

    grams: int = Field(...)

    yarn_id: int = Field(alias="id", repr=False)

    machine_washable: Union[bool, None] = Field(...)

    yarn_name: str = Field(alias="name")

    rating_average: float = Field(...)
    rating_count: int = Field(...)
    rating_total: int = Field(...)
    grams: int = Field(...)

    yardage: int = Field(...)
    yarn_company: "YarnCompany" = Field(...)

    yarn_fibers: List["YarnFiber"] = Field(...)

    yarn_attributes: Union[List[Dict[str, Any]], List[str]] = Field(...)

    def __post_init__(self):
        if self.machine_washable is None:
            self.machine_washable = False
            
        if isinstance(self.yarn_attributes, list):
            self.yarn_attributes = [attr["description"] for attr in self.yarn_attributes]