"""Ravelry API client wrapper inheriting endpoints modules."""
from .client.base import BaseRavelryClient
from .client.yarn import YarnMixin
from .client.pattern import PatternMixin
from .client.stash import StashMixin
from .client.queue import QueueMixin
from .client.favorites import FavoritesMixin
from .client.color_families import ColorFamiliesMixin
from .client.yarn_weights import YarnWeightsMixin


class RavelryClient(
    YarnMixin,
    PatternMixin,
    StashMixin,
    QueueMixin,
    FavoritesMixin,
    ColorFamiliesMixin,
    YarnWeightsMixin,
    BaseRavelryClient
):
    """
    RavelryClient combining base connection details and endpoint mixins.
    """
    pass
