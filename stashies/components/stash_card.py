"""Dash component for rendering stash entries as cards with edit triggers."""
from typing import Any, ClassVar, Dict
import dash_bootstrap_components as dbc
from dash import html, dcc
from pydantic.dataclasses import dataclass

from .base_component import BaseComponent


@dataclass
class StashCard(BaseComponent):
    """
    Renders stash entries as cards and provides edit hooks.

    - Properties:
        - STASH_STATUS_COLORS (ClassVar[dict]): Map of stash status IDs to badge color schemes.
    - Methods:
        - create_init_layout: No-op; container starts empty and is populated by callbacks.
        - create_card: Build a single dbc.Col containing the stash card and its store.
    """

    STASH_STATUS_COLORS: ClassVar[Dict[int, str]] = {
        1: "success",
        2: "secondary",
        3: "info",
        4: "danger",
    }

    def create_init_layout(self) -> None:
        """
        No-op implementation — stash cards list starts empty.
        """
        return None

    def create_card(self, s: Dict[str, Any], totals: Dict[str, float]) -> dbc.Col:
        """
        Build a single card column for a stash entry with edit buttons and state store.
        - Input
            - s (dict): Raw stash entry from Ravelry API.
            - totals (dict): Calculated totals dictionary containing yards, meters, skeins, grams.
        - output: dbc.Col containing the card layout.
        """
        yarn_info = s.get("yarn") or {}
        status = s.get("stash_status") or {}
        status_name = status.get("name") or "Unknown"
        status_id = status.get("id") or 1

        badge_color = self.STASH_STATUS_COLORS.get(status_id, "success")

        photo_url = None
        photos = yarn_info.get("photos") or []
        if photos and len(photos) > 0:
            photo_url = photos[0].get("medium_url") or photos[0].get("square_url")
        elif yarn_info.get("first_photo"):
            photo_url = yarn_info.get("first_photo", {}).get("medium_url") or yarn_info.get("first_photo", {}).get("square_url")

        img_element = html.Img(src=photo_url, style={"height": "120px", "objectFit": "cover", "width": "100%", "borderRadius": "4px"}) if photo_url else None

        y = totals.get("yards", 0.0)
        m = totals.get("meters", 0.0)
        sk = totals.get("skeins", 0.0)
        g = totals.get("grams", 0.0)

        is_fiber = s.get("type") == "fiber"
        if is_fiber:
            qty_text = f"{g:,.0f} g"
            if y > 0:
                qty_text += f" ({y:,.0f} yds / {m:,.0f} m)"
            quantity_element = html.Span([html.Strong("Weight: "), qty_text])
        else:
            quantity_element = html.Span([html.Strong("Quantity: "), f"{sk:.1f} skeins ({y:,.0f} yds / {m:,.0f} m / {g:,.0f} g)"])

        card_body_contents = [
            html.Div(
                [
                    html.H5(s.get("name") or "Unnamed Yarn", className="card-title text-success mb-1 me-2"),
                    html.Span(
                        status_name,
                        className=f"badge bg-{badge_color} mb-2 text-white"
                    )
                ],
                className="d-flex justify-content-between align-items-start"
            ),
            html.H6(yarn_info.get("yarn_company_name") or "Unknown Brand", className="card-subtitle text-muted mb-2"),
            html.Div(
                [
                    html.Span([html.Strong("Colorway: "), s.get("colorway_name") or "Not specified", " | "]),
                    html.Span([html.Strong("Dye Lot: "), s.get("dye_lot"), " | "]) if s.get("dye_lot") else None,
                    html.Span([html.Strong("Location: "), s.get("location"), " | "]) if s.get("location") else None,
                    quantity_element,
                ],
                className="small text-white"
            ),
        ]
        if s.get("notes"):
            card_body_contents.append(
                html.P(s.get("notes"), className="card-text small text-muted font-italic mt-2 mb-0")
            )

        if photo_url:
            card_content = dbc.Row(
                [
                    dbc.Col(img_element, xs=12, md=2, className="d-flex align-items-center p-3"),
                    dbc.Col(
                        dbc.CardBody(card_body_contents),
                        xs=12,
                        md=10
                    )
                ],
                className="g-0 align-items-center"
            )
        else:
            card_content = dbc.CardBody(card_body_contents)

        stash_id_str = str(s.get("id", ""))
        edit_btn = dbc.Button(
            [html.I(className="bi bi-pencil-fill me-1"), "Edit"],
            id={"type": "stash-edit-btn", "index": stash_id_str},
            color="outline-success",
            size="sm",
            className="mt-2 w-100 w-md-auto",
        )

        item_store = dcc.Store(
            id={"type": "stash-data-store", "index": stash_id_str},
            data={
                "id": s.get("id"),
                "colorway": s.get("colorway_name") or "",
                "dye_lot": s.get("dye_lot") or "",
                "location": s.get("location") or "",
                "notes": s.get("notes") or "",
                "skeins": sk,
                "status_id": status_id,
            }
        )

        card = dbc.Card(
            [
                card_content,
                dbc.CardFooter(
                    edit_btn,
                    className="bg-dark border-secondary d-flex justify-content-end"
                )
            ],
            className="mb-3 bg-dark border-secondary"
        )
        return dbc.Col([item_store, card], width=12)
