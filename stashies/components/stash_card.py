"""Dash component for rendering stash entries as cards with edit triggers."""
from typing import Any, ClassVar, Dict, List
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

        # Get photos from stash item first, then fallback to yarn photos
        photos = s.get("photos")
        if not photos:
            first_photo = s.get("first_photo")
            if first_photo:
                photos = [first_photo]
            else:
                photos = yarn_info.get("photos") or []
                if not photos and yarn_info.get("first_photo"):
                    photos = [yarn_info.get("first_photo")]

        photo_urls = []
        for p in (photos or []):
            url = p.get("medium_url") or p.get("square_url") or p.get("small_url") or p.get("thumbnail_url")
            if url:
                photo_urls.append(url)

        if len(photo_urls) > 1:
            carousel_items = [{"key": str(i), "src": str(url)} for i, url in enumerate(photo_urls)]
            img_element = dbc.Carousel(
                items=carousel_items,
                controls=True,
                indicators=True,
                interval=None,
                style={
                    "height": "120px",
                    "width": "120px",
                    "borderRadius": "4px",
                    "overflow": "hidden",
                }
            )
        elif len(photo_urls) == 1:
            img_element = html.Img(
                src=photo_urls[0],
                style={"height": "120px", "objectFit": "cover", "width": "100%", "borderRadius": "4px"}
            )
        else:
            img_element = None

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

        stash_id_str = str(s.get("id", ""))
        from ..model import Model
        sync_state = Model.get_sync_state(stash_id_str)

        card_badges = []
        if sync_state and sync_state.is_dirty:
            card_badges.append(dbc.Badge("Pending Sync", color="warning", className="me-2"))
        card_badges.append(html.Span(status_name, className=f"badge bg-{badge_color} mb-2 text-white"))

        card_body_contents = [
            html.Div(
                [
                    html.H5(s.get("name") or "Unnamed Yarn", className="card-title text-success mb-1 me-2"),
                    html.Div(card_badges, className="d-flex align-items-center flex-wrap")
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

        if img_element is not None:
            card_content = dbc.Row(
                [
                    dbc.Col(img_element, xs=12, md=2, className="d-flex align-items-center justify-content-center p-3"),
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
                "name": s.get("name") or yarn_info.get("name") or "Unnamed Yarn",
                "brand": yarn_info.get("yarn_company_name") or "",
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

    def create_colorway_row(self, s: Dict[str, Any], totals: Dict[str, float]) -> html.Div:
        """
        Build a single row layout for a specific colorway of a yarn.
        - Input:
            - s (dict): Raw stash entry from Ravelry API.
            - totals (dict): Calculated totals dictionary.
        - output: html.Div containing the colorway row layout.
        """
        status = s.get("stash_status") or {}
        status_name = status.get("name") or "Unknown"
        status_id = status.get("id") or 1
        badge_color = self.STASH_STATUS_COLORS.get(status_id, "success")

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
            quantity_element = html.Span([html.Strong("Qty: "), f"{sk:.1f} sk ({y:,.0f} yds / {m:,.0f} m / {g:,.0f} g)"])

        stash_id_str = str(s.get("id", ""))
        edit_btn = dbc.Button(
            [html.I(className="bi bi-pencil-fill me-1"), "Edit"],
            id={"type": "stash-edit-btn", "index": stash_id_str},
            color="outline-success",
            size="sm",
            className="ms-2",
            style={"padding": "2px 8px", "fontSize": "0.8rem"}
        )

        yarn_info = s.get("yarn") or {}
        item_store = dcc.Store(
            id={"type": "stash-data-store", "index": stash_id_str},
            data={
                "id": s.get("id"),
                "name": s.get("name") or yarn_info.get("name") or "Unnamed Yarn",
                "brand": yarn_info.get("yarn_company_name") or "",
                "colorway": s.get("colorway_name") or "",
                "dye_lot": s.get("dye_lot") or "",
                "location": s.get("location") or "",
                "notes": s.get("notes") or "",
                "skeins": sk,
                "status_id": status_id,
                "created_at": s.get("created_at"),
                "original_values": s.get("original_values") or {
                    "yards": y,
                    "meters": m,
                    "skeins": sk,
                    "grams": g,
                },
                "type": s.get("type"),
            }
        )

        from ..model import Model
        sync_state = Model.get_sync_state(stash_id_str)
        pending_badge = dbc.Badge("Pending Sync", color="warning", className="me-2") if (sync_state and sync_state.is_dirty) else None

        col_elements = []
        if pending_badge:
            col_elements.append(pending_badge)
        col_elements.extend([
            quantity_element,
            html.Span(status_name, className=f"badge bg-{badge_color} ms-2 text-white"),
            edit_btn
        ])

        row_content = dbc.Row(
            [
                dbc.Col(
                    [
                        html.Span(s.get("colorway_name") or "Not specified", className="fw-bold text-success me-2"),
                        html.Span(f"Dye Lot: {s.get('dye_lot')}", className="text-muted small me-2") if s.get("dye_lot") else None,
                        html.Span(f"Loc: {s.get('location')}", className="text-muted small") if s.get("location") else None,
                    ],
                    xs=12, md=6,
                    className="d-flex align-items-center flex-wrap"
                ),
                dbc.Col(
                    col_elements,
                    xs=12, md=6,
                    className="d-flex align-items-center justify-content-md-end mt-2 mt-md-0"
                )
            ],
            className="py-2 align-items-center"
        )

        notes_content = None
        if s.get("notes"):
            notes_content = dbc.Row(
                dbc.Col(
                    html.P(s.get("notes"), className="text-muted small mb-0 ps-3 border-start border-secondary"),
                    width=12
                ),
                className="pb-2"
            )

        return html.Div(
            [
                item_store,
                row_content,
                notes_content,
                html.Hr(className="my-1 border-secondary")
            ],
            className="colorway-row px-2"
        )

    def create_grouped_accordion_item(
        self,
        brand: str,
        name: str,
        items_with_totals: List[tuple],
        combined_totals: Dict[str, float]
    ) -> dbc.Card:
        """
        Build a single Card acting as a custom accordion item grouping all colorways.
        - Input:
            - brand (str): Yarn manufacturer/brand.
            - name (str): Yarn product name.
            - items_with_totals (list[tuple]): List of (raw_stash_dict, totals_dict) pairs.
            - combined_totals (dict): Summed totals for yards, meters, skeins, grams.
        - output: dbc.Card containing the collapsible grouped list.
        """
        # Find first available photo in any colorway/yarn
        photo_url = None
        for s, _ in items_with_totals:
            yarn_info = s.get("yarn") or {}
            photos = s.get("photos")
            if not photos:
                first_photo = s.get("first_photo")
                if first_photo:
                    photos = [first_photo]
                else:
                    photos = yarn_info.get("photos") or []
                    if not photos and yarn_info.get("first_photo"):
                        photos = [yarn_info.get("first_photo")]
            for p in photos:
                url = p.get("medium_url") or p.get("square_url") or p.get("small_url") or p.get("thumbnail_url")
                if url:
                    photo_url = url
                    break
            if photo_url:
                break

        badge_text = f"{len(items_with_totals)} items | {combined_totals['skeins']:.1f} sk"
        if combined_totals["yards"] > 0:
            badge_text += f" | {combined_totals['yards']:,.0f} yds"
        elif combined_totals["grams"] > 0:
            badge_text += f" | {combined_totals['grams']:,.0f} g"

        # Unique index for pattern matching toggle
        group_id = f"{brand}-{name}".replace(" ", "_").replace("/", "_")

        header_layout = html.Div(
            [
                html.Img(
                    src=photo_url,
                    style={
                        "height": "35px",
                        "width": "35px",
                        "borderRadius": "4px",
                        "objectFit": "cover",
                        "marginRight": "12px",
                        "border": "1px solid #444"
                    }
                ) if photo_url else html.Div(
                    style={
                        "height": "35px",
                        "width": "35px",
                        "borderRadius": "4px",
                        "backgroundColor": "#333",
                        "marginRight": "12px",
                        "border": "1px solid #444"
                    }
                ),
                html.Span(f"{brand} — {name}", className="fw-bold text-white me-auto"),
                dbc.Badge(
                    badge_text,
                    color="success",
                    className="text-white small"
                ),
                html.I(className="bi bi-chevron-down ms-3 text-muted")
            ],
            id={"type": "yarn-collapse-btn", "index": group_id},
            className="d-flex align-items-center w-100 p-3 bg-dark border-bottom border-secondary",
            style={"cursor": "pointer", "userSelect": "none"}
        )

        rows = []
        for s, totals in items_with_totals:
            rows.append(self.create_colorway_row(s, totals))

        # Remove the final trailing <hr> from the last row
        if rows:
            rows[-1].children.pop()

        body_layout = dbc.Collapse(
            html.Div(rows, className="bg-dark text-white rounded p-3"),
            id={"type": "yarn-collapse", "index": group_id},
            is_open=False
        )

        return dbc.Card(
            [header_layout, body_layout],
            className="mb-2 bg-dark border-secondary overflow-hidden"
        )
