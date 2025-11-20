from dash import Dash, html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from stashies.components import Header, SEARCH_BAR
from stashies import Model

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
    title="Stash Stats",  # Browser tab title
)

ERROR_MODAL = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Error!"), close_button=True),
        dbc.ModalBody("No search results found!"),
        dbc.ModalFooter(dbc.Button("Close", id="close-dismiss")),
    ],
    id="error-modal",
    keyboard=True,
    centered=True,
    is_open=False,
    autoFocus=True,
    enforceFocus=True,
)

SEARCH_RESULTS = dbc.Container([], id="search-results")
header = Header()
MODEL = Model()

app.layout = dbc.Container([header.layout(), SEARCH_BAR, SEARCH_RESULTS, ERROR_MODAL])


@callback(
    Output('search-results', 'children'),
    [
        Input('category-select', 'value'),
        Input('search-query', 'value'),
        Input('search-sort', 'value'),
        Input('search-button', 'n_clicks'),
    ],
)
def process_search(category, query, sort, button_clicks):
    if button_clicks is None:
        raise PreventUpdate
    else:
        data = None
        if category == 'yarns':
            data = MODEL.search_yarn(query=query, sort=sort)
        if data is None:
            return None
        else:
            return dbc.Label(["~~ Search Results ~~"])

        return dbc.Label(["Elephants are the only animal that can't jump"])


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
