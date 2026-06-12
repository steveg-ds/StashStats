"""Dash component for the StashStats page header."""
from dash import html
import dash_bootstrap_components as dbc
from typing import List, Any
from pydantic.dataclasses import dataclass
from pydantic import Field
from .base_component import BaseComponent


@dataclass
class Header(BaseComponent):
    """
    Renders the StashStats logo and a horizontal rule as the page header.

    - Methods:
        - create_init_layout: Returns logo image and divider row.
        - __post_init__: Calls parent post-init to build container.
    """

    def create_init_layout(self) -> List[dbc.Row]:
        """Build header layout containing the app logo and a horizontal divider."""
        return [
            dbc.Row(
                [
                    html.Img(
                        src="/static/Images/logo_color.png",
                        style=dict(width="75%", height="125px"),
                    ),
                    html.Hr(style={"margin": "20px 0"}),
                ],
                className="justify-content-center align-items-center",
            )
        ]

    def update_layout(self, username: str = None) -> None:
        """Update header container children with the username greeting if present."""
        logo_row = dbc.Row(
            [
                html.Img(
                    src="/static/Images/logo_color.png",
                    style=dict(width="75%", height="125px"),
                ),
            ],
            className="justify-content-center align-items-center",
        )
        
        children = [logo_row]
        
        if username:
            greeting_row = dbc.Row(
                [
                    html.H5(f"Hello {username}!", className="text-info text-center mt-2", id="header-greeting"),
                ],
                className="justify-content-center align-items-center",
            )
            children.append(greeting_row)
            
        children.append(html.Hr(style={"margin": "20px 0"}))
        self.container.children = children

    def __post_init__(self, *args: Any, **kwargs: Any):
        """Calls parent __post_init__ to construct the header container."""
        super().__post_init__(*args, **kwargs)  # call __post__init__ from parent class
