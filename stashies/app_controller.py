from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from .base import Base

from typing import Dict, Any, List, Union, Tuple

from .model import Model
from .components import Header, Search, SearchResults, BaseComponent


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

    def populate_yarn_modal(self, yarn_id: str):
        yarn = self.MODEL.get_full_yarn(yarn_id=yarn_id)

        if yarn is not None:
            self.LOGGER.debug(f"Yarn: {yarn.name}")

            return [
                True,
                dbc.Container(  # Yarn modal header
                    dbc.Label(f"Add '{yarn.name}' to stash?"),
                    className="d-flex justify-content-center align-items-center",
                    style={"height": "100%", "width": "100%"},
                ),
                yarn.create_yarn_modal_body(),
                yarn.model_dump(),
            ]
