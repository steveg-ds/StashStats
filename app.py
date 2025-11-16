from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

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

header = dbc.Row(
    [
        html.Img(
            src="/static/Images/logo_color.png",
            style=dict(width="40%", height="125px"),
        ),
        html.Hr(style={"margin": "20px 0"}),
    ],
    className="justify-content-center align-items-center",
)

form = dbc.Form(
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Search"),
                            dbc.Input(placeholder="Cool Yarn", id="search-query"),
                        ]
                    ),
                ],
                width="auto",
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Sort By"),
                        dbc.Select(
                            id="search-sort",
                            options=[
                                {"label": "Best Match", "value": "best_match"},
                                {"label": "Highest Rating", "value": "high_rating"},
                                {"label": "Most Projects", "value": "most_projects"},
                            ],
                            value="best_match",
                            placeholder="Best Match",
                        ),
                    ]
                ),
                width="auto",
            ),
            dbc.Col(dbc.Button("Submit", color="primary"), width="auto"),
        ],
        justify="center",
    ),
)

app.layout = dbc.Container([html.Div(header), html.Div(form)])


if __name__ == "__main__":
    app.run(
        host="100.124.126.4",
        debug=True,
        dev_tools_hot_reload=True,
    )
