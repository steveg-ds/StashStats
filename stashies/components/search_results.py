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
        self,
        id: int,
        name: str,
        company: str,
        grams: Optional[int],
        yardage: Optional[int],
        discontinued: Optional[bool],
        machine_washable: Optional[bool],
        colorways: Optional[List[str]],
        photo: HttpUrl,
    ) -> dbc.AccordionItem:
        # Build specification labels list
        specs = []
        specs.append(html.P(html.Strong(f"Company: {company}")))
        if grams is not None:
            specs.append(html.P(f"Weight: {grams}g"))
        if yardage is not None:
            specs.append(html.P(f"Yardage: {yardage} yards"))
        if discontinued is not None:
            specs.append(html.P(f"Discontinued: {'Yes' if discontinued else 'No'}"))
        if machine_washable is not None:
            specs.append(html.P(f"Machine Washable: {'Yes' if machine_washable else 'No'}"))

        # Build colorway badges if available
        colorway_components = []
        if colorways:
            colorway_components.append(html.Strong("Colorways:"))
            colorway_components.append(
                html.Div(
                    [
                        dbc.Badge(c, color="secondary", className="me-1 mb-1")
                        for c in colorways
                    ],
                    style={"flexWrap": "wrap", "display": "flex", "marginTop": "5px"},
                )
            )

        labels = dbc.Col(
            specs + colorway_components,
            width=8,
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
            width=4,
        )

        return dbc.AccordionItem(
            dbc.Row(
                [labels, thumbnail],
            ),
            title=f"{name} ({company})",
        )

    def __post_init__(self, *args: Any, **kwargs: Any):
        super().__post_init__(*args, **kwargs)  # call __post__init__ from parent class

