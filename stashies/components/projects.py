"""Dash component for rendering projects as cards in the Projects tab."""
from typing import Any, Dict, List, ClassVar
import dash_bootstrap_components as dbc
from dash import html, dcc
from pydantic.dataclasses import dataclass

from .base_component import BaseComponent


@dataclass
class ProjectsComponent(BaseComponent):
    """
    Renders user projects as responsive bootstrap cards.
    """

    PROJECT_STATUS_COLORS: ClassVar = {
        "completed": "success",
        "in progress": "info",
        "hibernating": "warning",
        "frogged": "danger",
        "finished": "success",
    }

    def create_init_layout(self) -> html.Div:
        """
        Build and return the initial projects layout structure.
        """
        return html.Div(
            [
                html.H4("My Projects", className="mt-3 text-success"),
                html.P("Browse your active and completed crafting projects."),
                dbc.Row(id="projects-list-container")
            ]
        )

    def build_project_card(self, p: Dict[str, Any]) -> dbc.Col:
        """
        Build a single card column for a project entry.
        - Input:
            - p (dict): Raw project entry from Ravelry API.
        - Output: dbc.Col containing the card layout.
        """
        status_name = p.get("status_name") or "Unknown"
        status_key = status_name.lower()
        badge_color = self.PROJECT_STATUS_COLORS.get(status_key, "secondary")

        # Get first photo url
        photo_url = None
        first_photo = p.get("first_photo") or {}
        if first_photo:
            photo_url = first_photo.get("medium_url") or first_photo.get("square_url") or first_photo.get("thumbnail_url")
        elif p.get("photos"):
            photos = p.get("photos")
            if photos and len(photos) > 0:
                photo_url = photos[0].get("medium_url") or photos[0].get("square_url") or photos[0].get("thumbnail_url")

        img_element = html.Img(
            src=photo_url,
            style={"height": "140px", "objectFit": "cover", "width": "100%", "borderRadius": "4px"}
        ) if photo_url else html.Div(
            html.I(className="bi bi-journal-text fs-1 text-muted"),
            style={"height": "140px", "width": "100%", "backgroundColor": "#333", "borderRadius": "4px"},
            className="d-flex align-items-center justify-content-center"
        )

        progress_val = p.get("progress") or 0
        progress_bar = dbc.Progress(
            value=progress_val,
            label=f"{progress_val}%",
            color="success" if progress_val == 100 else "info",
            striped=True,
            animated=True,
            className="mt-2 mb-2"
        )

        card_body_contents = [
            html.Div(
                [
                    html.H5(p.get("name") or "Unnamed Project", className="card-title text-success mb-1 me-2"),
                    html.Span(
                        status_name,
                        className=f"badge bg-{badge_color} mb-2 text-white"
                    )
                ],
                className="d-flex justify-content-between align-items-start"
            ),
            html.H6(f"Craft: {p.get('craft_name') or 'Not specified'}", className="card-subtitle text-muted mb-2"),
        ]

        if p.get("pattern_name"):
            card_body_contents.append(
                html.P([html.Strong("Pattern: "), p.get("pattern_name")], className="small text-white mb-1")
            )

        card_body_contents.append(progress_bar)

        # Dates
        dates_str = []
        if p.get("started"):
            dates_str.append(f"Started: {p.get('started')}")
        if p.get("completed"):
            dates_str.append(f"Completed: {p.get('completed')}")
        if dates_str:
            card_body_contents.append(
                html.Small(" | ".join(dates_str), className="text-muted d-block mt-1")
            )

        # Notes snippet
        if p.get("notes"):
            notes_text = p.get("notes")
            if len(notes_text) > 100:
                notes_text = notes_text[:100] + "..."
            card_body_contents.append(
                html.P(notes_text, className="card-text small text-muted font-italic mt-2 mb-0")
            )

        # Ravelry Link
        links = p.get("links") or {}
        ravelry_url = None
        if links.get("project"):
            ravelry_url = links.get("project")
        
        card_content = dbc.Row(
            [
                dbc.Col(img_element, xs=12, md=3, className="d-flex align-items-center p-3"),
                dbc.Col(
                    dbc.CardBody(card_body_contents),
                    xs=12,
                    md=9
                )
            ],
            className="g-0 align-items-center"
        )

        footer_children = []
        if ravelry_url:
            footer_children.append(
                dbc.Button(
                    "View on Ravelry",
                    href=ravelry_url,
                    target="_blank",
                    color="link",
                    size="sm",
                    className="text-success p-0"
                )
            )

        card = dbc.Card(
            [
                card_content,
                dbc.CardFooter(
                    html.Div(footer_children, className="d-flex justify-content-end"),
                    className="bg-dark border-secondary"
                ) if footer_children else None
            ],
            className="mb-3 bg-dark border-secondary"
        )

        return dbc.Col(card, width=12)
