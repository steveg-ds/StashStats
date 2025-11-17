from dash import html
import dash_bootstrap_components as dbc


class Header:
    def layout(self) -> dbc.Row:
        return dbc.Row(
            [
                html.Img(
                    src="../static/Images/logo_color.png",
                    style=dict(width="25%", height="125px"),
                ),
                html.Hr(style={"margin": "20px 0"}),
            ],
            className="justify-content-center align-items-center",
        )
