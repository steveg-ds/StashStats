from typing import Any, ClassVar, Dict, List, Optional, Set, Union

from pydantic import AliasChoices, BaseModel, Field, ValidationInfo, field_validator

from ..utils.model_config import MODEL_CONFIG
from .yarn_photos import YarnPhotos


class Yarn(BaseModel):
    ''''''
    model_config = MODEL_CONFIG

    id: int = Field(alias="id")
    '''API Yarn ID'''

    name: str = Field(alias="name")
    '''Name of the yarn product'''

    discontinued: Optional[bool] = Field(...)
    '''Indicates if the yarn has been discontinued by the manufacturer'''

    grams: Optional[int] = Field(...)
    '''Weight of one complete skein/hank in grams'''

    yardage: Optional[int] = Field(...)
    '''Length of yarn contained in one skein/hank, measured in yards'''

    company: str = Field(
        ...,
        validation_alias=AliasChoices(
            "yarn_company_name", "company_name", "company", 'yarn_company'
        ),
    )
    '''Name of the company that manufactures/distributes the yarn'''

    machine_washable: Optional[bool] = Field(...)
    '''Indicates if the yarn can be safely washed in a washing machine'''

    colorways: Optional[List[str]] = Field(default=None, init=False)

    photos: 'YarnPhotos' = Field(
        default_factory=YarnPhotos,
        validation_alias=AliasChoices('first_photo', 'photos'),
    )
    '''Container for yarn photo URLs with multiple size variants.
    '''

    @field_validator('colorways', mode='before')
    def set_colorway_list(
        cls, v: Optional[List[Dict[str, Any]]]
    ) -> Union[List[str], None]:
        if v is not None:
            return list(set(sorted([colorway['name'] for colorway in v])))
        return v

    @field_validator('photos', mode='before')
    def convert_photo_list(
        cls, v: Union[List[Dict[str, Any]], Dict[str, Any]]
    ) -> 'YarnPhotos':
        if isinstance(v, list):
            from random import choice

            v = choice(v)
        return YarnPhotos(**v)

    @field_validator('company', mode='before')
    def get_company_name(cls, v: Union[Dict[str, Any], str]) -> str:
        if isinstance(v, dict):
            return v['name']
        return v