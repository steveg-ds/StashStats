"""Temperature Blanket UI Tab Component."""
import dash_bootstrap_components as dbc
from dash import html, dcc
from ..base import Base
from .temperature_modal import TemperatureModal


class TemperatureBlanketComponent(Base):
    """Component for rendering the Temperature Blanket tab layout and 365-day grid visualization."""

    def __init__(self):
        self.modal = TemperatureModal()

    def render_layout(self) -> html.Div:
        """Render Temperature Blanket top-level tab container."""
        return html.Div(
            [
                dbc.Row([
                    dbc.Col([
                        html.H4("Temperature Blanket Tracker", className="mb-0"),
                        html.P("Visualize daily temperatures, calculate yarn yardage, and log blanket progress.", className="text-muted small"),
                    ], width=8),
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="bi bi-plus-circle me-2"), "New Temperature Blanket"],
                            id="open-temp-modal-btn",
                            color="success",
                            size="sm",
                            className="float-end"
                        )
                    ], width=4, className="align-self-center"),
                ], className="mb-4 pb-2 border-bottom align-items-center"),

                # Temperature Blanket Modal
                self.modal.create_modal_layout(),

                # Main 365-Day Visualization & Project Section
                html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("365-Day Color Grid & Progress", className="card-title mb-3"),
                            html.Div([
                                html.P("No active temperature blanket projects found. Click 'New Temperature Blanket' above to get started!", className="text-center text-muted py-5")
                            ], id="temp-grid-visualization"),
                        ])
                    ])
                ], id="temperature-blanket-main-content")
            ],
            id="temperature-blanket-container",
            className="p-3"
        )
