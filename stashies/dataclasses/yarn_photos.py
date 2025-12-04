from pydantic import Field, HttpUrl
from pydantic.dataclasses import dataclass


@dataclass
class YarnPhotos:

    medium: HttpUrl = Field(
        default=HttpUrl("https://placehold.co/600x400?text=No+Image+:("),
        alias="medium_url",
    )
    '''URL for medium photo'''

    thumbnail: HttpUrl = Field(
        default=HttpUrl("https://placehold.co/600x400?text=No+Image+:("),
        alias="thumbnail_url",
    )
    '''URL for thumbnail photo'''

    small: HttpUrl = Field(
        default=HttpUrl("https://placehold.co/600x400?text=No+Image+:("),
        alias="small_url",
    )
    '''URL for small photo'''

    square: HttpUrl = Field(
        default=HttpUrl("https://placehold.co/600x400?text=No+Image+:("),
        alias="square_url",
    )
    '''URL for square photo'''
