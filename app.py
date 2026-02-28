from typing import Dict, List

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Dash, html

from stashies.utils import create_logger

LOGGER = create_logger(logger_name='AppLogger')

SEARCH_CATEGORIES: List[Dict[str, str]] = [
    {'label': 'Yarns', 'value': 'yarns'},
    {'label': 'Yarn Companies', 'value': 'yarn_companies'},
    {'label': 'Personal Stash', 'value': 'personal_stash'},
    {'label': 'Projects', 'value': 'projects'},
    {'label': 'Patterns', 'value': 'patterns'},
]

SORT_CATEGORIES: List[Dict[str, str]] = [
    {'label': 'Best Match', 'value': 'best_match'},
    {'label': 'Highest Rating', 'value': 'highest_rating'},
    {'label': 'Most Projects', 'value': 'most_projects'},
]

DEFAULT_SEARCH: str = "yarns"


DEFAULT_SORT: str = "best_match"

app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)

HEADER: dmc.Container = dmc.Container(
    [
        dbc.Row(
            [
                html.Img(
                    src="../static/Images/logo_color.png",
                    style=dict(width="60%", height="125px"),
                ),
                html.Hr(style={"margin": "10px 0"}),
            ],
            className="justify-content-center align-items-center",
        )
    ],
    # fluid=True,
)

SEARCHBAR: dmc.Container = dmc.Container(
    children=dbc.Row(
        [
            dbc.Col(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Category"),
                            dbc.Select(
                                id='category-search-input',
                                options=SEARCH_CATEGORIES,
                                value=DEFAULT_SEARCH,
                                placeholder="Select Category",
                            ),
                        ]
                    ),
                ],
            ),
            dbc.Col(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Search"),
                            dbc.Input(
                                placeholder="Flux Capacitor",
                                id='text-search-input',
                            ),
                        ]
                    ),
                ],
            ),
            dbc.Col(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Sort"),
                            dbc.Select(
                                id='sort-search-input',
                                options=SORT_CATEGORIES,
                                value=DEFAULT_SORT,
                                placeholder="Select Sort",
                            ),
                        ]
                    ),
                ],
            ),
            dbc.Col(
                dbc.Button("Submit", id='submit-search-button', color="primary"),
            ),
            html.Hr(style={"margin": "20px 0"}),
        ]
    )
)

app.layout = dmc.MantineProvider(forceColorScheme='dark', children=[HEADER, SEARCHBAR])


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
