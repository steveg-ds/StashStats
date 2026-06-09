"""Dash component for rendering stash analytics plots and metric summaries."""
from typing import Any, ClassVar, Dict
import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic.dataclasses import dataclass

from .base_component import BaseComponent


@dataclass
class AnalyticsComponent(BaseComponent):
    """
    Renders stash analytics metrics and figures with responsive mobile layout grids.

    - Properties:
        - METRIC_MAP (ClassVar[dict]): Map of metrics configurations including color and labels.
    - Methods:
        - create_init_layout: Build and return the initial container content.
        - build_stats_cards: Build metric summary cards.
        - build_figure: Create a plotly line figure with responsive styles.
        - build_grid: Create a grid layout for multiple charts.
    """

    METRIC_MAP: ClassVar[Dict[str, Dict[str, str]]] = {
        "yards": {
            "col": "cumulative_yards",
            "label": "Total Stashed Yards",
            "title": "Cumulative Stashed Yardage Over Time",
            "suffix": "yards",
            "format": ",.0f",
            "color": "#00bc8c",
        },
        "meters": {
            "col": "cumulative_meters",
            "label": "Total Stashed Meters",
            "title": "Cumulative Stashed Meters Over Time",
            "suffix": "m",
            "format": ",.0f",
            "color": "#00bc8c",
        },
        "skeins": {
            "col": "cumulative_skeins",
            "label": "Total Stashed Skeins",
            "title": "Cumulative Stashed Skeins Over Time",
            "suffix": "skeins",
            "format": ",.1f",
            "color": "#17a2b8",
        },
        "grams": {
            "col": "cumulative_grams",
            "label": "Total Stashed Weight",
            "title": "Cumulative Stashed Weight Over Time",
            "suffix": "g",
            "format": ",.0f",
            "color": "#ffc107",
        },
    }

    def create_init_layout(self, selected_metric: str = "yards") -> dbc.Row:
        """
        Build the initial layout container with metric dropdown selector and graph container.
        - output: dbc.Row layout for analytics.
        """
        metric_selector = html.Div(
            [
                html.Label("Select Metric:", className="text-success fw-bold me-2"),
                dcc.Dropdown(
                    id="analytics-metric-selector",
                    options=[
                        {"label": "All Metrics (Grid)", "value": "all"},
                        {"label": "Meters (m)", "value": "meters"},
                        {"label": "Skeins (qty)", "value": "skeins"},
                        {"label": "Weight (grams)", "value": "grams"},
                        {"label": "Yardage (yards)", "value": "yards"},
                    ],
                    value=selected_metric,
                    clearable=False,
                    style={"width": "250px", "color": "#000000"},
                )
            ],
            className="d-flex align-items-center mb-3 mt-3"
        )

        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Stash Analytics Overview", className="mt-3 text-success"),
                        html.P("Analyze your personal stash details over time."),
                        metric_selector,
                        html.Div(id="analytics-content-area")
                    ],
                    width=12
                )
            ]
        )

    def build_stats_cards(
        self,
        curr_yards: float,
        curr_meters: float,
        curr_skeins: float,
        curr_grams: float,
        selected_metric: str
    ) -> dbc.Row:
        """
        Build responsive grid cards displaying current stashed totals.
        - Input
            - curr_yards (float): Current yards total.
            - curr_meters (float): Current meters total.
            - curr_skeins (float): Current skeins total.
            - curr_grams (float): Current grams total.
            - selected_metric (str): The metric currently selected for line graph.
        - output: dbc.Row containing cards.
        """
        return dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Yardage", className="card-title text-muted small"),
                                html.H3(f"{curr_yards:,.0f} yds", className="text-success mb-0"),
                            ]
                        ),
                        className=f"bg-dark border-{'success' if selected_metric in ('yards', 'all') else 'secondary'}"
                    ),
                    xs=6,
                    md=3,
                    className="mb-3",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Meters", className="card-title text-muted small"),
                                html.H3(f"{curr_meters:,.0f} m", className="text-success mb-0"),
                            ]
                        ),
                        className=f"bg-dark border-{'success' if selected_metric in ('meters', 'all') else 'secondary'}"
                    ),
                    xs=6,
                    md=3,
                    className="mb-3",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Skeins", className="card-title text-muted small"),
                                html.H3(f"{curr_skeins:,.1f}", className="text-info mb-0"),
                            ]
                        ),
                        className=f"bg-dark border-{'info' if selected_metric in ('skeins', 'all') else 'secondary'}"
                    ),
                    xs=6,
                    md=3,
                    className="mb-3",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Weight", className="card-title text-muted small"),
                                html.H3(f"{curr_grams:,.0f} g", className="text-warning mb-0"),
                            ]
                        ),
                        className=f"bg-dark border-{'warning' if selected_metric in ('grams', 'all') else 'secondary'}"
                    ),
                    xs=6,
                    md=3,
                    className="mb-3",
                ),
            ],
            className="mb-4 mt-3"
        )

    def build_figure(self, df: Any, metric_info: Dict[str, Any], is_mobile: bool = False) -> Any:
        """
        Create a Plotly Line figure using the metric metadata configuration.
        - Input
            - df (DataFrame): Sorted pandas DataFrame containing analytics timeseries.
            - metric_info (dict): Sub-dict of METRIC_MAP for the selected metric.
            - is_mobile (bool): True to render using compact margins/fonts.
        - output: plotly.graph_objects.Figure instance.
        """
        import plotly.express as px
        fig = px.line(
            df,
            x="date",
            y=metric_info["col"],
            title=metric_info["title"],
            labels={"date": "Date", metric_info["col"]: metric_info["label"]},
            markers=True,
            line_shape="hv",
            template="plotly_dark"
        )
        
        font_size = 10 if is_mobile else 12
        title_size = 12 if is_mobile else 14
        margin_l = 30 if is_mobile else 55
        margin_r = 10 if is_mobile else 20
        margin_t = 35 if is_mobile else 40
        margin_b = 35 if is_mobile else 40

        fig.update_layout(
            hovermode="x unified",
            font=dict(size=font_size, color="#ffffff"),
            title_font=dict(size=title_size, color="#00bc8c"),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickfont=dict(size=font_size)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", tickformat=",", tickfont=dict(size=font_size)),
            hoverlabel=dict(bgcolor="#222222", font_size=font_size, font_color="#ffffff"),
            margin=dict(l=margin_l, r=margin_r, t=margin_t, b=margin_b),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        fig.update_traces(
            hovertemplate=f"<b>{metric_info['label']}:</b> %{{y:{metric_info['format']}}} {metric_info['suffix']}<extra></extra>",
            line_color=metric_info.get("color", "#00bc8c"),
            marker=dict(size=4 if is_mobile else 6)
        )
        return fig

    def build_grid(self, figs: Dict[str, Any]) -> html.Div:
        """
        Build single column on mobile, or two column on desktop chart grid.
        - Input
            - figs (dict): Dict of plotly line figures.
        - output: html.Div containing grid layout.
        """
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(figure=figs["yards"], config={'responsive': True}, style={'minWidth': '0'}),
                            xs=12,
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            dcc.Graph(figure=figs["meters"], config={'responsive': True}, style={'minWidth': '0'}),
                            xs=12,
                            md=6,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(figure=figs["skeins"], config={'responsive': True}, style={'minWidth': '0'}),
                            xs=12,
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            dcc.Graph(figure=figs["grams"], config={'responsive': True}, style={'minWidth': '0'}),
                            xs=12,
                            md=6,
                            className="mb-3",
                        ),
                    ]
                )
            ]
        )
