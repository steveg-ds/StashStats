from typing import Any, Dict, List, Tuple, Union

import dash_bootstrap_components as dbc
from dash import dcc, html

from .base import Base
from .components import BaseComponent, Header, Search, SearchResults
from .model import Model


class AppController(Base):
    def __init__(self, header_id: str, search_id: str, result_id: str):
        self.MODEL: 'Model' = Model()
        self.HEADER: 'Header' = Header(container_id=header_id)
        self.SEARCH: 'Search' = Search(container_id=search_id)
        self.SEARCH_RESULTS: 'SearchResults' = SearchResults(container_id=result_id)

    def create_initial_layout(self) -> List[dbc.Container]:
        return [
            self.HEADER.container,
            self.SEARCH.container,
            self.SEARCH_RESULTS.container,
            dbc.Container(dcc.Store(id='memory-output')),
        ]

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
    ):
        # TODO: if query is empty, it should return a popup error modal thing of some sort.
        # TODO: I should add yarn description stuff to the cards so they can take up more space
        yarns = self.MODEL.search_yarn(query=query, sort=sort)

        if yarns is not None:
            self.LOGGER.debug(f"Query: {query}, # of Yarns Found: {len(yarns)}")
            accordion_items: List[dbc.AccordionItem] = [
                dbc.AccordionItem(yarn.create_card_display(), title=yarn.name)
                for yarn in yarns
            ]
            return dbc.Col(dbc.Accordion(accordion_items), width=6)
        else:
            self.LOGGER.error('Query: {query}, No Results Found')
