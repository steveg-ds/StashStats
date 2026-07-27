"""Ravelry API client facade."""
from .base import BaseRavelryClient
from .yarn import YarnMixin
from .pattern import PatternMixin
from .stash import StashMixin
from .queue import QueueMixin
from .favorites import FavoritesMixin
from .color_families import ColorFamiliesMixin
from .yarn_weights import YarnWeightsMixin


class RavelryClient(
    BaseRavelryClient,
    YarnMixin,
    PatternMixin,
    StashMixin,
    QueueMixin,
    FavoritesMixin,
    ColorFamiliesMixin,
    YarnWeightsMixin
):
    """
    Facade for Ravelry API client combining all mixin endpoints.
    
    Usage:
        client = RavelryClient(api_username='user', api_key='key')
        yarns = client.search_yarn('wool')
        queue = client.get_queue()
        favorites = client.get_favorites()
    """
    pass