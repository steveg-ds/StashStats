import dash_bootstrap_components as dbc
from dash import html
from pydantic.dataclasses import dataclass
from pydantic import Field, HttpUrl
from typing import Dict, Any


from ..utils import MODEL_CONFIG


@dataclass(config=MODEL_CONFIG)
class SearchResults:
    container_id: str = Field(default='search-results')
    layout: dbc.Container = Field(init=False)

    def create_layout(self) -> dbc.Container:
        return dbc.Container(
            children=None,
            id=self.container_id,
            fluid=True,
            className="w-60 mx-auto d-flex justify-content-center",
        )

    def create_search_result(
        self, id: int, name: str, label_data: Dict[str, Any], photo: HttpUrl
    ) -> dbc.AccordionItem:

        label_components = [
            dbc.Label(f"{key.capitalize()}: {value}")
            for key, value in label_data.items()
        ]

        labels = dbc.Col(
            label_components,
            width=2,
            className="d-flex flex-column justify-content-center",
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
            width=2,  # Adjusted width to balance with labels
            className="d-flex justify-content-center align-items-center",
        )

        return dbc.AccordionItem(
            dbc.Row(
                [labels, thumbnail],
                className="d-flex justify-content-center align-items-center",
            ),
            title=name,
        )

    def __post_init__(self):
        self.layout = self.create_layout()
