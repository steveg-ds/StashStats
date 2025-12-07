from dash import html
import dash_bootstrap_components as dbc
from typing import List, Any
from pydantic.dataclasses import dataclass
from pydantic import Field
from .base_component import BaseComponent


@dataclass
class Header(BaseComponent):

    def create_init_layout(self) -> List[dbc.Row]:
        return [
            dbc.Row(
                [
                    html.Img(
                        src="../static/Images/logo_color.png",
                        style=dict(width="75%", height="125px"),
                    ),
                    html.Hr(style={"margin": "20px 0"}),
                ],
                className="justify-content-center align-items-center",
            )
        ]

    def __post_init__(self, *args: Any, **kwargs: Any):
        super().__post_init__(*args, **kwargs)  # call __post__init__ from parent class
