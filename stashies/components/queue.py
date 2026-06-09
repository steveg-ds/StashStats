"""Dash component for the project queue manager."""
from typing import Any, Dict, List, ClassVar
import dash_bootstrap_components as dbc
from dash import html, dcc
from pydantic.dataclasses import dataclass

from .base_component import BaseComponent


@dataclass
class QueueComponent(BaseComponent):
    """
    Renders Ravelry queue list with rank badges and position controls.
    """

    def create_init_layout(self) -> html.Div:
        """Build the initial queue page layout."""
        return html.Div(
            [
                html.H4("My Project Queue", className="mt-3 text-success"),
                html.P("Organize and prioritize your upcoming crafting projects."),
                html.Div(id="queue-list-container")
            ]
        )

    def build_queue_list(self, queue_items: List[Dict[str, Any]]) -> dbc.ListGroup:
        """
        Build a list of queued projects in priority order.
        - Input:
            - queue_items (list): Raw queue records from Ravelry.
        - Output: dbc.ListGroup of items.
        """
        if not queue_items:
            return html.Div("Your queue is currently empty.", className="text-warning mt-3")

        # Sort by sort_order or position_in_queue
        sorted_items = sorted(queue_items, key=lambda x: x.get("sort_order") or x.get("position_in_queue") or 999)

        list_items = []
        n_items = len(sorted_items)

        for i, q in enumerate(sorted_items):
            q_id = q.get("id")
            q_id_str = str(q_id)
            position = q.get("sort_order") or q.get("position_in_queue") or (i + 1)

            photo_url = None
            best_photo = q.get("best_photo")
            if best_photo:
                photo_url = best_photo.get("square_url") or best_photo.get("thumbnail_url")

            img_element = html.Img(
                src=photo_url,
                style={"height": "60px", "width": "60px", "objectFit": "cover", "borderRadius": "4px"}
            ) if photo_url else html.Div(
                html.I(className="bi bi-clock-history fs-3 text-muted"),
                style={"height": "60px", "width": "60px", "backgroundColor": "#333", "borderRadius": "4px"},
                className="d-flex align-items-center justify-content-center"
            )

            # Details
            details = []
            if q.get("pattern_name"):
                details.append(f"Pattern: {q.get('pattern_name')}")
            if q.get("yarn_name"):
                yarn_str = q.get("yarn_name")
                if q.get("skeins"):
                    yarn_str += f" ({q.get('skeins')} skeins)"
                details.append(f"Yarn: {yarn_str}")

            details_text = " | ".join(details)

            # Control buttons
            controls = [
                dbc.Button(
                    html.I(className="bi bi-arrow-up"),
                    id={"type": "queue-up-btn", "index": q_id_str},
                    color="outline-success",
                    size="sm",
                    disabled=(i == 0),
                    className="me-1"
                ),
                dbc.Button(
                    html.I(className="bi bi-arrow-down"),
                    id={"type": "queue-down-btn", "index": q_id_str},
                    color="outline-success",
                    size="sm",
                    disabled=(i == n_items - 1),
                    className="me-2"
                ),
                dbc.Button(
                    html.I(className="bi bi-trash-fill"),
                    id={"type": "queue-remove-btn", "index": q_id_str},
                    color="danger",
                    size="sm"
                )
            ]

            list_item = dbc.ListGroupItem(
                dbc.Row(
                    [
                        # Position badge
                        dbc.Col(
                            html.H4(f"#{position}", className="text-success mb-0 text-center"),
                            xs=2,
                            md=1,
                            className="d-flex align-items-center justify-content-center"
                        ),
                        # Thumbnail
                        dbc.Col(
                            img_element,
                            xs=3,
                            md=1,
                            className="d-flex align-items-center justify-content-center"
                        ),
                        # Name & Details
                        dbc.Col(
                            [
                                html.H5(q.get("name") or "Unnamed Project", className="text-success mb-1"),
                                html.P(details_text, className="small text-muted mb-0") if details_text else None,
                                html.P(q.get("notes"), className="small font-italic text-muted mb-0 mt-1") if q.get("notes") else None
                            ],
                            xs=7,
                            md=7,
                            className="d-flex flex-column justify-content-center"
                        ),
                        # Controls
                        dbc.Col(
                            html.Div(controls, className="d-flex justify-content-end align-items-center h-100"),
                            xs=12,
                            md=3,
                            className="mt-2 mt-md-0"
                        )
                    ],
                    className="align-items-center"
                ),
                className="bg-dark border-secondary text-white mb-2 rounded"
            )
            list_items.append(list_item)

        return dbc.ListGroup(list_items, className="mt-3")
