import dash_bootstrap_components as dbc
from dash import html
from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import List, ClassVar, Dict, Literal, Any

from .base_component import BaseComponent


@dataclass
class Search(BaseComponent):
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
                    width=self.default_width,
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
                    width=self.default_width,
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
                    width=self.default_width,
                ),
                dbc.Col(
                    dbc.Button("Submit", id=button_id, color="primary"),
                    width=self.default_width,
                ),
                html.Hr(style={"margin": "20px 0"}),
                dbc.Modal(  # TODO: make this its own component
                    [
                        dbc.ModalHeader(children=None, id='yarn-modal-header'),
                        dbc.ModalBody(children=None, id='yarn-modal-body'),
                        dbc.ModalFooter(
                            [
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Close",
                                            id="yarn-modal-close-btn",
                                            className="ms-auto",
                                            n_clicks=0,
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "confirm",
                                            id="yarn-modal-action-btn",
                                            className="ms-auto",
                                            n_clicks=0,
                                        )
                                    ]
                                ),
                            ]
                        ),
                    ],
                    id="yarn-modal",
                    centered=True,
                    is_open=False,
                    autofocus=True,
                    backdrop=True,
                ),
            ]
        )

    def __post_init__(self, *args: Any, **kwargs: Any):
        super().__post_init__(*args, **kwargs)  # call __post__init__ from parent class
