from dash import (
    Dash,
    callback,
    Input,
    Output,
    State,
    callback_context,
    ALL,
)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from json import loads
from stashies import AppController
from stashies.utils import create_logger

LOGGER = create_logger(logger_name='AppLogger')

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
    ],
    prevent_initial_callbacks=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)
CONTROLLER = AppController(
    header_id='header-container', search_id='search-container', result_id='results-id'
)

app.layout = dbc.Container(children=CONTROLLER.create_initial_layout(), fluid=True)


@callback(
    Output('results-id', 'children'),
    [
        Input('search-category', 'value'),
        Input('search-query', 'value'),
        Input('search-sort', 'value'),
        Input('search-button', 'n_clicks'),
    ],
)
def process_search(category, query, sort, button_clicks):
    if button_clicks is None:
        raise PreventUpdate
    else:
        LOGGER.debug("Search btn pressed")
        if category == 'yarns':
            return CONTROLLER.search_yarn(query, sort)

    return None


@app.callback(
    [
        Output("yarn-modal", "is_open"),
        Output("yarn-modal-header", "children"),
        Output("yarn-modal-body", "children"),
        Output("yarn-modal-close-btn", "children"),
        Output("yarn-modal-action-btn", "children"),
    ],
    Input({"type": "search-result-button", "index": ALL}, "n_clicks"),
    Input("yarn-modal-close-btn", "n_clicks"),
    Input("yarn-modal-action-btn", "n_clicks"),
    [State("yarn-modal", "is_open")],
    prevent_initial_call=True,
)
def open_yarn_modal(n_clicks_list, close_btn, action_btn, is_open):
    # TODO: add this functionality to an AppController function
    ## 1. Check if modal is open:
    ##  - if open + close_btn clicks == 1: close modal
    ## 2. check callback_context logic to populate the modal with yarn data
    ##  - display error message if something goes wrong
    ##  - If no error, display stuff for adding yarn to stash: colorways, # of skeins, etc
    ##  -
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate

    # Get the triggered button info
    triggered_id = ctx.triggered[0]["prop_id"]
    button_id_str = triggered_id.split(".")[0]
    button_id = loads(button_id_str)
    yarn_id = button_id["index"]

    # Check if this was a real click (n_clicks > 0)
    # Get all button IDs to find the index
    all_button_ids = []
    for inp in ctx.inputs_list[0]:  # First input group
        all_button_ids.append(inp["id"]["index"])  # Extract yarn_id from button ID

    # Find the position of yarn_id in the list
    try:
        button_index = all_button_ids.index(yarn_id)

        # Check if this button was actually clicked
        if n_clicks_list[button_index] is None:
            # Button exists but hasn't been clicked yet
            LOGGER.debug(f"Button {yarn_id} exists but n_clicks is None")
            raise PreventUpdate

        LOGGER.debug(f"Button {yarn_id}")
        modal_children = CONTROLLER.populate_yarn_modal(yarn_id=yarn_id)
        return CONTROLLER.populate_yarn_modal(yarn_id=yarn_id)

        return [True, modal_children]
    except ValueError:
        LOGGER.error(f"Button with yarn_id {yarn_id} not found in inputs")
        raise PreventUpdate


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
