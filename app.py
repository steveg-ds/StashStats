from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from stashies.components import Header, SearchBar

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


header = Header()
search_bar = SearchBar()
app.layout = dbc.Container([header.layout(), search_bar.layout()])


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
