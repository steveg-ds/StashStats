from dash import html
import dash_bootstrap_components as dbc

from pydantic.dataclasses import dataclass
from pydantic import Field
from ..utils import MODEL_CONFIG


@dataclass(config=MODEL_CONFIG)
class Header:

    layout: dbc.Container = Field(init=False)

    container_id: str = Field(default='header-id')

    def create_layout(self) -> dbc.Container:
        return dbc.Container(
            [
                dbc.Row(
                    [
                        html.Img(
                            src="../static/Images/logo_color.png",
                            style=dict(width="25%", height="125px"),
                        ),
                        html.Hr(style={"margin": "20px 0"}),
                    ],
                    className="justify-content-center align-items-center",
                )
            ],
            id=self.container_id,
        )

    def __post_init__(self):
        self.layout = self.create_layout()
