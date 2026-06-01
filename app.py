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
    MATCH,
    ALL,
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
    external_stylesheets=[dbc.themes.DARKLY],
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


@callback(
    Output({"type": "stash-status-msg", "index": MATCH}, "children"),
    Input({"type": "stash-submit-btn", "index": MATCH}, "n_clicks"),
    State({"type": "stash-skeins", "index": MATCH}, "value"),
    State({"type": "stash-colorway", "index": MATCH}, "value"),
    State({"type": "stash-dyelot", "index": MATCH}, "value"),
    State({"type": "stash-location", "index": MATCH}, "value"),
    State({"type": "stash-notes", "index": MATCH}, "value"),
    State({"type": "stash-submit-btn", "index": MATCH}, "id"),
)
def handle_add_to_stash(n_clicks, skeins, colorway, dyelot, location, notes, button_id):
    if n_clicks is None or not n_clicks:
        raise PreventUpdate

    yarn_id = button_id["index"]
    
    # Structure data payload matching Stash (POST) schema requirements
    stash_payload = {
        "yarn_id": int(yarn_id),
        "stash_status_id": 1
    }
    if colorway:
        stash_payload["colorway_name"] = colorway
    if dyelot:
        stash_payload["dye_lot"] = dyelot
    if location:
        stash_payload["location"] = location
    if notes:
        stash_payload["notes"] = notes
    if skeins is not None and skeins != "":
        stash_payload["pack"] = {"skeins": float(skeins)}
        
    try:
        response = CONTROLLER.MODEL.create_stash(stash_payload)
        if response and 'stash' in response:
            stash_id = response['stash'].get('id', 'Unknown')
            return f"Success! Stashed with ID: {stash_id}"
        else:
            return "Failed to stash yarn. Please verify credentials."
    except Exception as e:
        return f"Error occurred: {str(e)}"


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        debug=True,
        dev_tools_hot_reload=True,
    )

