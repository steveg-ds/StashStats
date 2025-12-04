from dash import Dash, html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from stashies import AppController
from stashies.components import Header, Search

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        dbc.icons.FONT_AWESOME,  # For the sun/moon icons
    ],
    prevent_initial_callbacks=True,
    meta_tags=[  # Add meta tags for responsiveness
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    title="Stash Stats",
)
CONTROLLER = AppController()

app.layout = dbc.Container(
    [
        CONTROLLER.HEADER.layout,
        CONTROLLER.SEARCH.layout,
        CONTROLLER.SEARCH_RESULTS.layout,
    ],
    fluid=True,
)


@callback(
    Output(f'{CONTROLLER.SEARCH_RESULTS.container_id}', 'children'),
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
        if category == 'yarns':
            return CONTROLLER.search_yarn(query, sort)

    return None


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
