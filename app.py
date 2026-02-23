from json import loads

import dash_bootstrap_components as dbc
from dash import ALL, MATCH, Dash, Input, Output, State, callback
from dash import callback_context as ctx
from dash.exceptions import PreventUpdate

from stashies import AppController, Model
from stashies.utils import create_logger

LOGGER = create_logger(logger_name='AppLogger')

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
    ],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)
CONTROLLER = AppController(
    header_id='header-container', search_id='search-container', result_id='results-id'
)

app.layout = dbc.Container(children=CONTROLLER.create_initial_layout(), fluid=True)


@callback(
    Output('results-id', 'children'),
    Output('search-button', 'n_clicks'),
    Input('search-category', 'value'),
    Input('search-query', 'value'),
    Input('search-sort', 'value'),
    Input({"type": "yarn-accordion-item", "index": ALL}, "n_clicks"),
    Input('search-button', 'n_clicks'),
)
def process_search(category, query, sort, accordion_clicks, button_clicks):
    # Dash now passes accordion_clicks as a LIST of values
    if button_clicks is None and not any(accordion_clicks):
        raise PreventUpdate

    # Check which one actually triggered the callback
    triggered_id = ctx.triggered_id

    # If the search button was clicked OR an accordion item was clicked
    if category == 'yarns':
        LOGGER.debug(f"Search triggered by: {triggered_id}")
        return CONTROLLER.search_yarn(query, sort), None

    return no_update, no_update


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
