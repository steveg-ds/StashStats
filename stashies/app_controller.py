from pydantic.dataclasses import dataclass
from pydantic import Field
from dash import html
import dash_bootstrap_components as dbc
from .base import Base

from typing import Dict, Any, List, Union

from .model import Model
from .components import Header, Search, SearchResults


from .utils import MODEL_CONFIG


@dataclass(config=MODEL_CONFIG)
class AppController(Base):
    MODEL: 'Model' = Field(default_factory=Model)
    HEADER: 'Header' = Field(default_factory=Header)
    SEARCH: 'Search' = Field(default_factory=Search)
    SEARCH_RESULTS: 'SearchResults' = Field(default_factory=SearchResults)

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
    ):
        yarns = self.MODEL.search_yarn(query=query, sort=sort)

        if yarns is not None:
            self.LOGGER.debug(f"Query: {query}, # of Yarns Found: {len(yarns)}")
            accordion_items: List[dbc.AccordionItem] = [
                self.SEARCH_RESULTS.create_search_result(
                    id=yarn.id,
                    name=yarn.name,
                    label_data=yarn.model_dump(
                        include={'discontinued', 'grams', 'yardage'}
                    ),
                    photo=yarn.photos.thumbnail,
                )
                for yarn in yarns
            ]
            return dbc.Accordion(
                accordion_items,
            )
        else:
            self.LOGGER.error('Query: {query}, No Results Found')

    def __post_init__(self):
        pass
