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
        # Return a tabs layout switching between Search and Stash Analytics
        return [
            self.HEADER.container,
            dbc.Container(
                [
                    dcc.Tabs(
                        id="app-tabs",
                        value="tab-search",
                        children=[
                            dcc.Tab(
                                label="Yarn Search",
                                value="tab-search",
                                children=[
                                    html.Div(style={"height": "20px"}),
                                    self.SEARCH.container,
                                    self.SEARCH_RESULTS.container,
                                ],
                                style={"backgroundColor": "#222", "color": "#fff"},
                                selected_style={"backgroundColor": "#333", "color": "#00bc8c"}
                            ),
                            dcc.Tab(
                                label="Stash Analytics",
                                value="tab-analytics",
                                children=[
                                    html.Div(style={"height": "20px"}),
                                    dbc.Container(id="analytics-tab-content")
                                ],
                                style={"backgroundColor": "#222", "color": "#fff"},
                                selected_style={"backgroundColor": "#333", "color": "#00bc8c"}
                            )
                        ]
                    ),
                    dcc.Store(id='memory-output')
                ]
            )
        ]


    def search_yarn(
        self,
        query: str,
        sort: str = "best",
    ):
        yarns = self.MODEL.search_yarn(query=query, sort=sort)

        if yarns is not None:
            self.LOGGER.debug(f"Query: {query}, # of Yarns Found: {len(yarns)}")
            
            accordion_items: List[dbc.AccordionItem] = []
            for y in yarns:
                # Fetch full details including colorways/images
                full_yarn = self.MODEL.get_full_yarn(y.id)
                if not full_yarn:
                    full_yarn = y
                
                # Get the appropriate photo URL
                photo_url = full_yarn.photos.medium
                
                item = self.SEARCH_RESULTS.create_search_result(
                    id=full_yarn.id,
                    name=full_yarn.name,
                    company=full_yarn.company,
                    grams=full_yarn.grams,
                    yardage=full_yarn.yardage,
                    discontinued=full_yarn.discontinued,
                    machine_washable=full_yarn.machine_washable,
                    colorways=full_yarn.colorways,
                    photo=photo_url,
                )
                accordion_items.append(item)
                
            return dbc.Col(dbc.Accordion(accordion_items), width=6)
        else:
            self.LOGGER.error(f'Query: {query}, No Results Found')
            return html.Div("No results found.")

