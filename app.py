from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import (
    Dash,
    Input,
    Output,
    State,
    callback,
    callback_context,
    dcc,
    html,
    no_update,
)
from dash.exceptions import PreventUpdate

from stashies.utils import create_logger

LOGGER = create_logger(logger_name='AppLogger')

app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.SANDSTONE],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)

HEADER: dbc.Container = dbc.Container(
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

SEARCHBAR: dbc.Container = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(dbc.Label('Tell me your wishes'), width=2),
                dbc.Col(dbc.Input(id='search-text'), width=4),
                dbc.Col(dbc.Button(id='submit-btn'), width=6),
            ],
            align='center',
        )
    ],
)


SEARCH_RESULTS: dbc.Container = dbc.Container(
    children=None, id='search-results-container'
)

app.layout = dbc.Container(children=[HEADER, SEARCHBAR, SEARCH_RESULTS])


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
