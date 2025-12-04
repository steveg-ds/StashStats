from pydantic import Field, BaseModel, field_validator, ValidationInfo


from typing import Optional, Dict, Any, List, Union, ClassVar, Set

from .yarn_photos import YarnPhotos
from ..utils.model_config import MODEL_CONFIG


class Yarn(BaseModel):
    model_config = MODEL_CONFIG

    result_params: ClassVar[Set[str]] = Field(
        default={'discontinued', 'grams', 'yardage'}, init=False, repr=False
    )

    id: int = Field(alias="id")
    '''Unique identifier for the yarn (not included in string representation)'''

    name: str = Field(alias="name")
    '''Commercial name of the yarn product'''

    discontinued: Optional[bool] = Field(...)
    '''Indicates if the yarn has been discontinued by the manufacturer'''

    grams: Optional[int] = Field(...)
    '''Weight of one complete skein/hank in grams'''

    yardage: Optional[int] = Field(...)
    '''Length of yarn contained in one skein/hank, measured in yards'''

    company: str = Field(..., alias="yarn_company_name")
    '''Name of the company that manufactures/distributes the yarn'''

    machine_washable: Optional[bool] = Field(...)
    '''Indicates if the yarn can be safely washed in a washing machine'''

    colorways: Optional[List[str]] = Field(default=None, init=False)

    photos: 'YarnPhotos' = Field(default_factory=YarnPhotos, alias='first_photo')
    '''Container for yarn photo URLs with multiple size variants.
    '''

    @field_validator('colorways', mode='before')
    def set_colorway_list(
        cls, v: Optional[List[Dict[str, Any]]]
    ) -> Union[List[str], None]:
        if v is not None:
            return [colorway['name'] for colorway in v]
        return v
