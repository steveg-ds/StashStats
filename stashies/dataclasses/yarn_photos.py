"""Pydantic dataclass for Ravelry yarn photo URLs at multiple sizes."""
from pydantic import Field, HttpUrl
from pydantic.dataclasses import dataclass


@dataclass
class YarnPhotos:
    """
    Holds photo URLs for a yarn in multiple size variants.
    Falls back to a placeholder image URL when no photo is available.

    - Properties:
        - medium (HttpUrl): Medium-size photo URL.
        - thumbnail (HttpUrl): Thumbnail photo URL.
        - small (HttpUrl): Small photo URL.
        - square (HttpUrl): Square-cropped photo URL.
    """

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
