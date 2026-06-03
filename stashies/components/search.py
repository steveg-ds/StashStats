"""Dash component for the yarn search bar with category, query, and sort controls."""
from typing import Any, ClassVar, Dict, List, Literal

import dash_bootstrap_components as dbc
from dash import html
from pydantic import Field
from pydantic.dataclasses import dataclass

from .base_component import BaseComponent


@dataclass
class Search(BaseComponent):
    """
    Renders the search bar with category selector, query input, sort selector, and submit button.

    - Properties:
        - SEARCH_CATEGORIES (ClassVar[list]): Available search category options.
        - SORT_CATEGORIES (ClassVar[list]): Available sort order options.
        - DEFAULT_SEARCH (ClassVar[str]): Default selected search category.
        - DEFAULT_SORT (ClassVar[str]): Default selected sort order.
    - Methods:
        - create_init_layout: Build and return the search bar row.
        - __post_init__: Calls parent post-init to build container.
    """

    SEARCH_CATEGORIES: ClassVar[List[Dict[str, str]]] = [
        {'label': 'Yarns', 'value': 'yarns'},
        {'label': 'Yarn Companies', 'value': 'yarn_companies'},
        {'label': 'Personal Stash', 'value': 'personal_stash'},
        {'label': 'Projects', 'value': 'projects'},
        {'label': 'Patterns', 'value': 'patterns'},
    ]

    SORT_CATEGORIES: ClassVar[List[Dict[str, str]]] = [
        {'label': 'Best Match', 'value': 'best_match'},
        {'label': 'Highest Rating', 'value': 'highest_rating'},
        {'label': 'Most Projects', 'value': 'most_projects'},
    ]

    DEFAULT_SEARCH: ClassVar[str] = "yarns"

    DEFAULT_SORT: ClassVar[str] = "best_match"

    def create_init_layout(
        self,
        category_id: str = 'search-category',
        query_id: str = 'search-query',
        sort_id: str = 'search-sort',
        button_id: str = 'search-button',
    ) -> dbc.Row:
        """
        Build the search bar layout row with all controls.
        - Input
            - category_id (str): Dash ID for category selector. Defaults to 'search-category'.
            - query_id (str): Dash ID for query input. Defaults to 'search-query'.
            - sort_id (str): Dash ID for sort selector. Defaults to 'search-sort'.
            - button_id (str): Dash ID for submit button. Defaults to 'search-button'.
        - output: dbc.Row containing all search controls.
        """
        ids = {"category": category_id, "query": query_id, "sort": sort_id}
        self.component_ids.update(ids)

        return dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Category"),
                                dbc.Select(
                                    id=category_id,
                                    options=self.SEARCH_CATEGORIES,
                                    value=self.DEFAULT_SEARCH,
                                    placeholder="Select Category",
                                ),
                            ]
                        ),
                    ],
                    xs=12,
                    sm="auto",
                    className="mb-2 mb-sm-0",
                ),
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Search"),
                                dbc.Input(
                                    placeholder="Flux Capacitor",
                                    id=query_id,
                                ),
                            ]
                        ),
                    ],
                    xs=12,
                    sm="auto",
                    className="mb-2 mb-sm-0",
                ),
                dbc.Col(
                    [
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Sort"),
                                dbc.Select(
                                    id=sort_id,
                                    options=self.SORT_CATEGORIES,
                                    value=self.DEFAULT_SORT,
                                    placeholder="Select Sort",
                                ),
                            ]
                        ),
                    ],
                    xs=12,
                    sm="auto",
                    className="mb-2 mb-sm-0",
                ),
                dbc.Col(
                    dbc.Button("Submit", id=button_id, color="primary", className="w-100 w-sm-auto"),
                    xs=12,
                    sm="auto",
                ),
                html.Hr(style={"margin": "20px 0"}),
            ]
        )

    def __post_init__(self, *args: Any, **kwargs: Any):
        """Calls parent __post_init__ to build the search container."""
        super().__post_init__(*args, **kwargs)  # call __post__init__ from parent class
