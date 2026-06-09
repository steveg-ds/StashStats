"""Dash component for rendering yarn search results as an accordion with inline stash-add forms."""
import datetime
import dash_bootstrap_components as dbc
from dash import html, dcc
from pydantic.dataclasses import dataclass
from pydantic import Field, HttpUrl
from typing import Dict, Any, Optional, List


from .base_component import BaseComponent


@dataclass
class SearchResults(BaseComponent):
    """
    Renders yarn search results and provides an inline 'Add to Stash' form per result.

    - Methods:
        - create_init_layout: No-op; container starts empty and is populated by callbacks.
        - create_search_result: Build a single dbc.AccordionItem for one yarn result.
        - __post_init__: Calls parent post-init to construct the container.
    """
    def create_init_layout(self) -> None:
        """
        No-op implementation — results container starts empty.
        Results are injected by the search callback at runtime.
        """
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
        photos: List[HttpUrl],
    ) -> dbc.AccordionItem:
        """
        Build a single accordion item displaying yarn details and an inline stash form.
        - Input
            - id (int): Ravelry yarn ID; used as index in pattern-matching Dash callback IDs.
            - name (str): Yarn product name shown as accordion title.
            - company (str): Manufacturer name.
            - grams (int | None): Skein weight in grams.
            - yardage (int | None): Skein length in yards.
            - discontinued (bool | None): Whether the yarn is discontinued.
            - machine_washable (bool | None): Whether machine washing is safe.
            - colorways (list[str] | None): Known colorway names; drives dropdown vs freetext input.
            - photo (HttpUrl): Thumbnail image URL.
        - output: dbc.AccordionItem containing specs, colorway badges, stash form, and thumbnail.
        """
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
                            xs=12,
                            sm=4,
                            className="mb-2 mb-sm-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Colorway"),
                                # Use a dropdown when colorways are known; fall back to freetext input otherwise
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
                            xs=12,
                            sm=4,
                            className="mb-2 mb-sm-0",
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
                            xs=12,
                            sm=4,
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
                            xs=12,
                            sm=6,
                            className="mb-2 mb-sm-0",
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
                            xs=12,
                            sm=6,
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Date Added"),
                                html.Br(),
                                dcc.DatePickerSingle(
                                    id={"type": "stash-date-added", "index": id},
                                    date=datetime.date.today().isoformat(),
                                    display_format="YYYY-MM-DD",
                                    className="w-100"
                                ),
                            ],
                            xs=12,
                        )
                    ],
                    className="mb-3",
                ),
                dbc.Button(
                    "Add Yarn to Stash", 
                    id={"type": "stash-submit-btn", "index": id}, 
                    color="success",
                    size="sm",
                    className="w-100",
                ),
                html.Div(id={"type": "stash-status-msg", "index": id}, className="mt-2 text-info")
            ],
            style={"padding": "10px", "border": "1px solid #444", "borderRadius": "5px", "backgroundColor": "#222", "marginTop": "15px"}
        )

        labels = dbc.Col(
            specs + colorway_components + [stash_form],
            xs=12,
            md=8,
        )

        if photos and len(photos) > 1:
            carousel_items = [{"key": str(i), "src": str(url)} for i, url in enumerate(photos)]
            img_element = dbc.Carousel(
                items=carousel_items,
                controls=True,
                indicators=True,
                interval=None,
                style={
                    'height': '150px',
                    'width': '150px',
                    'margin': '10px',
                    'borderRadius': '8px',
                    'overflow': 'hidden',
                }
            )
        elif photos:
            img_element = html.Img(
                src=str(photos[0]),
                style={
                    'height': '150px',
                    'width': 'auto',
                    'margin': '10px',
                    'borderRadius': '8px',
                },
            )
        else:
            img_element = None

        thumbnail = dbc.Col(
            [img_element] if img_element is not None else [],
            xs=12,
            md=4,
            className="d-flex align-items-center justify-content-center"
        )

        return dbc.AccordionItem(
            dbc.Row(
                [labels, thumbnail],
            ),
            title=f"{name} ({company})",
        )

    def __post_init__(self, *args: Any, **kwargs: Any):
        """
        Calls parent __post_init__ to build the container element.
        """
        super().__post_init__(*args, **kwargs)  # call __post__init__ from parent class


