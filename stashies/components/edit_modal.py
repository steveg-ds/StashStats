"""Dash component for the edit stash modal."""
from typing import Any, ClassVar, Dict, List
import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic.dataclasses import dataclass

from .base_component import BaseComponent


@dataclass
class EditModal(BaseComponent):
    """
    Renders a modal for editing details and logging usage of a stashed yarn.

    - Properties:
        - STASH_STATUS_OPTIONS (ClassVar[list]): Status options dropdown mapping.
    - Methods:
        - create_init_layout: Build and return the dbc.Modal layout.
    """

    STASH_STATUS_OPTIONS: ClassVar[List[Dict[str, Any]]] = [
        {"label": "In stash", "value": 1},
        {"label": "Used up", "value": 2},
        {"label": "Gifted", "value": 3},
        {"label": "Gone / Sold", "value": 4},
    ]

    def create_init_layout(self) -> dbc.Modal:
        """
        Build the top-level edit stash modal with tabs.
        - output: dbc.Modal layout component.
        """
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Edit Stash Entry", className="text-success")),
                dbc.ModalBody(
                    [
                        dcc.Store(id="edit-stash-id-store"),
                        dcc.Store(id="edit-stash-current-skeins-store"),
                        dbc.Tabs(
                            [
                                # Tab 1: Edit Details
                                dbc.Tab(
                                    dbc.Form(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Colorway"),
                                                            dbc.Input(
                                                                id="edit-stash-colorway",
                                                                placeholder="Colorway name",
                                                                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
                                                            ),
                                                        ],
                                                        xs=12,
                                                        sm=6,
                                                        className="mb-2 mb-sm-0",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Dye Lot"),
                                                            dbc.Input(
                                                                id="edit-stash-dyelot",
                                                                placeholder="Dye lot",
                                                                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
                                                            ),
                                                        ],
                                                        xs=12,
                                                        sm=6,
                                                    ),
                                                ],
                                                className="mb-3 mt-3"
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Location"),
                                                            dbc.Input(
                                                                id="edit-stash-location",
                                                                placeholder="Storage location",
                                                                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
                                                            ),
                                                        ],
                                                        xs=12,
                                                        sm=6,
                                                        className="mb-2 mb-sm-0",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Total Skeins (exact)"),
                                                            dbc.Input(
                                                                id="edit-stash-skeins",
                                                                type="number",
                                                                min=0,
                                                                step=0.25,
                                                                placeholder="Number of skeins",
                                                                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
                                                            ),
                                                        ],
                                                        xs=12,
                                                        sm=6,
                                                    ),
                                                ],
                                                className="mb-3"
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Status"),
                                                            dcc.Dropdown(
                                                                id="edit-stash-status",
                                                                options=self.STASH_STATUS_OPTIONS,
                                                                clearable=False,
                                                                style={"color": "#000"}
                                                            ),
                                                        ],
                                                        xs=12,
                                                    ),
                                                ],
                                                className="mb-3"
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Label("Notes"),
                                                            dbc.Textarea(
                                                                id="edit-stash-notes",
                                                                placeholder="Notes...",
                                                                rows=3,
                                                                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
                                                            ),
                                                        ],
                                                        xs=12,
                                                    ),
                                                ],
                                                className="mb-3"
                                            ),
                                        ]
                                    ),
                                    label="Edit Details",
                                    tab_id="modal-tab-details",
                                ),
                                # Tab 2: Log Usage
                                dbc.Tab(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.P(
                                                            "Enter how much yarn you used. The remaining amount will be saved to Ravelry.",
                                                            className="text-muted small mt-3 mb-3"
                                                        ),
                                                        dbc.Label("Skeins Used"),
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.Input(
                                                                    id="edit-stash-used-skeins",
                                                                    type="number",
                                                                    min=0,
                                                                    step=0.25,
                                                                    placeholder="e.g. 1.5",
                                                                    style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
                                                                ),
                                                                dbc.InputGroupText("skeins", style={"backgroundColor": "#444", "color": "#ccc", "border": "1px solid #555"}),
                                                            ],
                                                            className="mb-3"
                                                        ),
                                                        html.Div(
                                                            id="edit-stash-remaining-preview",
                                                            className="mt-2 p-3 rounded",
                                                            style={"backgroundColor": "#1a2a1a", "border": "1px solid #2a5a2a", "minHeight": "60px"}
                                                        ),
                                                    ],
                                                    xs=12,
                                                )
                                            ],
                                            className="mt-2"
                                        )
                                    ],
                                    label="Log Usage",
                                    tab_id="modal-tab-usage",
                                ),
                            ],
                            id="edit-stash-modal-tabs",
                            active_tab="modal-tab-details",
                        ),
                        html.Div(id="edit-stash-status-msg", className="text-info small mt-3"),
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button("Save Changes", id="edit-stash-save-btn", color="success", className="me-2 w-100 w-sm-auto mb-2 mb-sm-0"),
                        dbc.Button("Cancel", id="edit-stash-cancel-btn", color="secondary", outline=True, className="w-100 w-sm-auto"),
                    ],
                    className="flex-column flex-sm-row",
                ),
            ],
            id="edit-stash-modal",
            is_open=False,
            backdrop="static",
            centered=True,
            size="lg",
            scrollable=True,
            style={"color": "#fff"}
        )
