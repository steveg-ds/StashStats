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
from stashies.app_controller import AppController
from dotenv import load_dotenv

load_dotenv()

LOGGER = create_logger(logger_name='AppLogger')

app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.SANDSTONE],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)

CONTROLLER = AppController(
    header_id="app-header",
    search_id="app-search",
    result_id="app-results"
)

app.layout = dbc.Container(children=CONTROLLER.create_initial_layout())


@callback(
    Output("app-results", "children"),
    Input("search-button", "n_clicks"),
    State("search-query", "value"),
    State("search-sort", "value"),
    State("search-category", "value"),
)
def handle_search(n_clicks, query, sort, category):
    if not query:
        raise PreventUpdate
    
    # We pass 'sort' to the controller, the user's Search component uses 'best_match' which may need mapping
    # but the API might accept it or ignore it. For now just pass it along.
    return CONTROLLER.search_yarn(query=query, sort=sort)


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
