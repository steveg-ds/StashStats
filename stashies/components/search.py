import dash_bootstrap_components as dbc

from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import List, ClassVar, Dict


from ..utils import MODEL_CONFIG


@dataclass(config=MODEL_CONFIG)
class Search:
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

    container_id: str = Field(default='search-bar')
    layout: dbc.Container = Field(init=False)

    default_width: str = Field(default='auto')

    def create_layout(self) -> dbc.Container:
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Category"),
                                        dbc.Select(
                                            id='search-category',
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
                                            id="search-query",
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
                                            id='search-sort',
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
                            dbc.Button("Submit", id="search-button", color="primary"),
                            width=self.default_width,
                        ),
                    ]
                ),
            ],
            id=self.container_id,
            fluid=True,
            className="w-60 mx-auto d-flex justify-content-center",
        )

    def __post_init__(self):
        self.layout = self.create_layout()
