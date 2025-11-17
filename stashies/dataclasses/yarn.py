from pydantic import Field, BaseModel, field_validator, ValidationInfo

from typing import Optional, Dict, Any

from .yarn_photos import YarnPhotos


class Yarn(BaseModel):
    id: int = Field(alias="id", repr=False)
    '''Yarn ID'''

    name: str = Field(alias="name")
    '''Yarn name'''

    discontinued: Optional[bool] = Field(...)
    '''Indicates if yarn has been discontinued'''

    grams: Optional[int] = Field(...)
    '''grams of one skein of yarn'''

    yardage: Optional[int] = Field(...)
    '''yardage of one skein of yarn'''

    yarn_company: str = Field(..., alias="yarn_company_name")
    '''company name of yarn'''

    machine_washable: Optional[bool] = Field(...)
    '''Indicates if yarn is machine washable'''

    photos: Optional['YarnPhotos'] = Field(..., alias='first_photo')
    '''stores instance of the `YarnPhotos` dataclass. 
        Contains URLS for square, medium, thumbnail, and small photo sizes
    '''

    @field_validator('photos', mode='before')
    def set_yarn_id(cls, v: Dict[str, Any], info: ValidationInfo) -> Any:
        if v is not None:
            v['yarn_id'] = info.data['id']

        return v
