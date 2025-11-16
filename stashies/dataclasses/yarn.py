from pydantic import Field, BaseModel, field_validator
from typing import Optional, Union

from .yarn_company import YarnCompany


class Yarn(BaseModel):
    yarn_id: int = Field(alias="id", repr=False)
    yarn_name: str = Field(alias="name")

    discontinued: Optional[bool] = Field(...)

    grams: Optional[int] = Field(default=None)

    yardage: Optional[int] = Field(default=None)

    yarn_company: Optional['YarnCompany'] = Field(
        default=None, alias="yarn_company_name"
    )

    machine_washable: Optional[bool] = Field(default=None)

    rating_average: Optional[float] = Field(default=None)

    rating_count: Optional[int] = Field(default=None)

    rating_total: Optional[int] = Field(default=None)

    @field_validator('yarn_company', mode='before')
    def process_company_name(cls, v: Union['YarnCompany', str]) -> 'YarnCompany':
        if isinstance(v, str):
            v = YarnCompany(name=v)
        return v
