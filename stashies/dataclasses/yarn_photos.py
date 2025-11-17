from pydantic import Field, BaseModel, field_validator, HttpUrl
from typing import Optional


class YarnPhotos(BaseModel):

    yarn_id: int = Field(init=False, repr=False)

    medium: Optional[HttpUrl] = Field(default=None, alias="medium_url")
    '''URL for medium photo'''

    thumbnail: Optional[HttpUrl] = Field(default=None, alias="thumbnail_url")
    '''URL for thumbnail photo'''

    small: Optional[HttpUrl] = Field(default=None, alias="small_url")
    '''URL for small photo'''

    square: Optional[HttpUrl] = Field(default=None, alias="square_url")
    '''URL for square photo'''

