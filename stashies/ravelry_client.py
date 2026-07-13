"""Ravelry API client wrapper inheriting endpoints modules."""
from .client.base import BaseRavelryClient
from .client.yarn import YarnMixin
from .client.pattern import PatternMixin
from .client.stash import StashMixin

class RavelryClient(BaseRavelryClient, YarnMixin, PatternMixin, StashMixin):
    """
    RavelryClient combining base connection details and endpoint mixins.
    """
    pass
