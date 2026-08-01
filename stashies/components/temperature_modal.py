"""Temperature Blanket Creation Wizard Modal Component."""
import math
from typing import Tuple, Dict, Any, List
import dash_bootstrap_components as dbc
from dash import html, dcc
from ..base import Base


def calculate_tier_yardage(
    day_count: int,
    yards_per_row: float,
    rows_per_day: int = 1,
    buffer_pct: float = 0.10,
    yards_per_skein: float = 200.0
) -> Tuple[float, int]:
    """
    Calculate required total yards and skeins for a temperature tier based on frequency.

    Args:
        day_count (int): Number of days falling into temperature tier.
        yards_per_row (float): Yards consumed per row.
        rows_per_day (int): Rows per day (1 for single temp, 2 for dual stripe).
        buffer_pct (float): Safety buffer percentage (e.g. 0.10 for 10%).
        yards_per_skein (float): Total yards per skein of yarn.

    Returns:
        Tuple[float, int]: (Total required yards including buffer, Total required skeins).
    """
    base_yards = day_count * yards_per_row * rows_per_day
    total_yards = base_yards * (1.0 + buffer_pct)
    if yards_per_skein <= 0:
        skeins_needed = 1
    else:
        skeins_needed = math.ceil(total_yards / yards_per_skein)
    return round(total_yards, 2), max(1, skeins_needed)


class TemperatureModal(Base):
    """Component for building the Temperature Blanket project setup modal wizard."""

    def __init__(self, container_id: str = "temperature-blanket-modal-container"):
        self.container_id = container_id

    def create_modal_layout(self) -> dbc.Modal:
        """Build multi-step wizard modal layout for creating a Temperature Blanket project."""
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Create Temperature Blanket Project")),
                dbc.ModalBody(
                    html.Div([
                        html.P("Design and calculate yarn requirements for your temperature blanket.", className="text-muted"),
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Project Name"),
                                    dbc.Input(id="temp-project-name", placeholder="e.g. 2026 NYC Temperature Blanket"),
                                ], width=12, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Location (City / Lat, Lon)"),
                                    dbc.Input(id="temp-project-location", placeholder="e.g. New York, NY or 40.71, -74.00"),
                                ], width=6, className="mb-3"),
                                dbc.Col([
                                    dbc.Label("Temperature Metric"),
                                    dbc.Select(
                                        id="temp-project-metric",
                                        options=[
                                            {"label": "Daily Mean / Average (Standard Default)", "value": "mean"},
                                            {"label": "Daily High", "value": "high"},
                                            {"label": "Daily Low", "value": "low"},
                                            {"label": "Dual Stripe (High + Low)", "value": "dual_stripe"},
                                        ],
                                        value="mean"
                                    ),
                                ], width=6, className="mb-3"),
                            ]),
                        ])
                    ], id="temp-modal-wizard-body")
                ),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="temp-modal-cancel-btn", color="secondary", className="me-2"),
                    dbc.Button("Create Project", id="temp-modal-submit-btn", color="success"),
                ])
            ],
            id="temperature-project-modal",
            is_open=False,
            size="lg"
        )
