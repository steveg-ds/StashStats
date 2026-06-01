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

        # Build form to add to stash
        colorway_options = [{"label": c, "value": c} for c in colorways] if colorways else []
        
        stash_form = html.Div(
            [
                html.Hr(),
                html.H6("Add to Stash", className="text-primary"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Skeins"),
                                dbc.Input(
                                    type="number", 
                                    id={"type": "stash-skeins", "index": id}, 
                                    placeholder="1.0",
                                    min=0,
                                    step=0.1
                                ),
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Colorway"),
                                dbc.Select(
                                    id={"type": "stash-colorway", "index": id},
                                    options=colorway_options,
                                    placeholder="Select or leave blank",
                                ) if colorways else dbc.Input(
                                    type="text",
                                    id={"type": "stash-colorway", "index": id},
                                    placeholder="Colorway name",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Dye Lot"),
                                dbc.Input(
                                    type="text", 
                                    id={"type": "stash-dyelot", "index": id}, 
                                    placeholder="e.g. 42"
                                ),
                            ],
                            width=5,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Location"),
                                dbc.Input(
                                    type="text", 
                                    id={"type": "stash-location", "index": id}, 
                                    placeholder="e.g. Closet"
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Notes"),
                                dbc.Input(
                                    type="text", 
                                    id={"type": "stash-notes", "index": id}, 
                                    placeholder="e.g. soft texture"
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Button(
                    "Add Yarn to Stash", 
                    id={"type": "stash-submit-btn", "index": id}, 
                    color="success",
                    size="sm"
                ),
                html.Div(id={"type": "stash-status-msg", "index": id}, className="mt-2 text-info")
            ],
            style={"padding": "10px", "border": "1px solid #444", "borderRadius": "5px", "backgroundColor": "#222", "marginTop": "15px"}
        )

        labels = dbc.Col(
            specs + colorway_components + [stash_form],
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


