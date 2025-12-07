import dash_bootstrap_components as dbc
from dash import html
from pydantic.dataclasses import dataclass
from pydantic import Field, HttpUrl
from typing import Dict, Any


from .base_component import BaseComponent


@dataclass
class SearchResults(BaseComponent):
    def create_init_layout(self) -> None:
        return None

    def create_search_result(
        self, id: int, name: str, label_data: Dict[str, Any], photo: HttpUrl
    ) -> dbc.AccordionItem:

        label_components = [
            dbc.Row(
                [
                    dbc.Label(f"{key.capitalize()}: {value}")
                    for key, value in label_data.items()
                ]
            )
        ]

        labels = dbc.Col(
            label_components,
            width=self.default_width,
        )

        thumbnail = dbc.Col(
            [
                html.Img(
                    src=str(photo),
                    style={
                        'height': '150px',
                        'width': 'auto',
                        'margin': '10px',
                        'borderRadius': '8px',
                    },
                ),
            ],
            width=self.default_width,  # Adjusted width to balance with labels
        )

        return dbc.AccordionItem(
            dbc.Row(
                [labels, thumbnail],
            ),
            title=name,
        )

    def __post_init__(self, *args: Any, **kwargs: Any):
        super().__post_init__(*args, **kwargs)  # call __post__init__ from parent class
