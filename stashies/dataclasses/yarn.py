from typing import Any, ClassVar, Dict, List, Optional, Set, Union

from pydantic import AliasChoices, BaseModel, Field, ValidationInfo, field_validator

from ..utils.model_config import MODEL_CONFIG
from .yarn_photos import YarnPhotos


class Yarn(BaseModel):
    """
    Pydantic model representing a Ravelry yarn product.

    - Properties:
        - id (int): Ravelry numeric yarn ID.
        - name (str): Yarn product name.
        - discontinued (bool | None): True if yarn is no longer produced.
        - grams (int | None): Skein weight in grams.
        - yardage (int | None): Skein length in yards.
        - company (str): Manufacturer name, resolved from multiple API aliases.
        - machine_washable (bool | None): Safe for machine washing.
        - colorways (list[str] | None): Sorted deduplicated colorway names.
        - photos (YarnPhotos): Photo URLs in multiple sizes.
    """
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
    '''Sorted, deduplicated list of colorway names; populated from colorways detail endpoint.'''

    photos: List[YarnPhotos] = Field(
        default_factory=list,
        validation_alias=AliasChoices('photos', 'first_photo'),
    )
    '''Container for yarn photo URLs with multiple size variants.
    '''

    @field_validator('colorways', mode='before')
    def set_colorway_list(
        cls, v: Optional[List[Dict[str, Any]]]
    ) -> Union[List[str], None]:
        """
        Normalise colorway list from API — deduplicate and sort by name.
        - Input
            - v: Raw list of colorway dicts with a 'name' key, or None.
        - output: Sorted list of unique colorway name strings, or None.
        """
        if v is not None:
            return sorted(set([colorway['name'] for colorway in v]))
        return v

    @field_validator('photos', mode='before')
    def convert_photo_list(
        cls, v: Union[List[Dict[str, Any]], Dict[str, Any], None]
    ) -> List[YarnPhotos]:
        """
        Normalise photo data from API into a list of YarnPhotos instances.
        - Input
            - v: List of photo dicts, single photo dict, or None.
        - output: List of YarnPhotos instances.
        """
        if not v:
            return []
        if isinstance(v, list):
            return [YarnPhotos(**photo) for photo in v]
        if isinstance(v, dict):
            return [YarnPhotos(**v)]
        return []

    @field_validator('company', mode='before')
    def get_company_name(cls, v: Union[Dict[str, Any], str]) -> str:
        """
        Resolve company name from a nested dict or plain string.
        - Input
            - v: Dict with a 'name' key, or a bare string.
        - output: Company name string.
        """
        if isinstance(v, dict):
            return v.get('name', '')
        return v