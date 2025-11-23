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
            results = []

            for yarn in data:
                photo = (
                    yarn.photos.thumbnail
                    if yarn.photos is not None
                    else "https://via.placeholder.com/200x300/FF0000/FFFFFF?text=No+Image"
                )

                item = dbc.AccordionItem(
                    [
                        dbc.Row(
                            [  # Add this Row to contain both columns
                                dbc.Col(
                                    [
                                        dbc.Row(
                                            [dbc.Label(f"Company: {yarn.company}")]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label(
                                                    f"Discontinued: {yarn.discontinued}"
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label(
                                                    f"Machine Washable: {yarn.machine_washable}"
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [dbc.Label(f"Yardage: {yarn.yardage}")]
                                        ),
                                        dbc.Row([dbc.Label(f"Grams: {yarn.grams}")]),
                                    ],
                                    width=4,  # Adjust width as needed (out of 12)
                                ),
                                dbc.Col(
                                    [
                                        html.Img(
                                            src=str(photo),
                                            style={
                                                'height': '200px',
                                                'width': 'auto',
                                                'margin': '10px',
                                                'borderRadius': '8px',
                                            },
                                        ),
                                    ],
                                    width=4,  # Adjust width as needed (out of 12)
                                    className="d-flex justify-content-center align-items-center",  # Center the image
                                ),
                            ]
                        )
                    ],
                    title=yarn.name,
                )
                results.append(item)
            return dbc.Accordion(
                children=results,
                flush=True,
            )
        return dbc.Label([":("])


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
