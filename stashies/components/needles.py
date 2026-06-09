"""Dash component for the needles and crochet hooks organizer."""
from typing import List, Dict, Any
import dash_bootstrap_components as dbc
from dash import html
from pydantic.dataclasses import dataclass

from .base_component import BaseComponent


@dataclass
class NeedlesComponent(BaseComponent):
    """
    Renders knitting needle and crochet hook lists from Ravelry API needles/list.json.
    """

    def create_init_layout(self) -> html.Div:
        """Build and return the initial needles container."""
        return html.Div(id="needles-list-container")

    def build_needles_tables(self, needle_records: List[Dict[str, Any]]) -> html.Div:
        """
        Group and render needles in styled dark tables.
        - Input:
            - needle_records (list): Raw needle records from Ravelry.
        - Output: html.Div containing the tables.
        """
        if not needle_records:
            return html.Div("No needles or crochet hooks found in your Ravelry inventory.", className="text-warning mt-3")

        knitting = []
        crochet = []

        for record in needle_records:
            # Ravelry records usually specify type or craft.
            # We can detect crochet hooks by having 'hook' in size info, or 'crochet' in type name.
            size_info = record.get("needle_size") or {}
            type_info = record.get("needle_type") or {}
            
            # Determine if it's crochet or knitting
            is_crochet = False
            type_name_lower = str(type_info.get("name") or "").lower()
            if "crochet" in type_name_lower or size_info.get("hook"):
                is_crochet = True

            item = {
                "id": record.get("id"),
                "comment": record.get("comment") or "",
                "type": type_info.get("name") or "Unknown",
                "length": type_info.get("length") or "",
                "us": size_info.get("us") or "",
                "metric": size_info.get("pretty_metric") or size_info.get("metric") or "",
                "hook": size_info.get("hook") or "",
            }

            if is_crochet:
                crochet.append(item)
            else:
                knitting.append(item)

        def build_row(n, is_hook=False):
            size_str = ""
            if is_hook:
                parts = []
                if n["metric"]:
                    parts.append(str(n["metric"]))
                if n["hook"]:
                    parts.append(f"US {n['hook']}")
                size_str = " / ".join(parts) if parts else "Unknown"
            else:
                parts = []
                if n["metric"]:
                    metric_val = f"{n['metric']} mm" if isinstance(n["metric"], (int, float)) else str(n["metric"])
                    parts.append(metric_val)
                if n["us"]:
                    parts.append(f"US {n['us']}")
                size_str = " / ".join(parts) if parts else "Unknown"

            length_str = f"{n['length']} in" if isinstance(n["length"], (int, float)) else str(n["length"])

            return html.Tr([
                html.Td(size_str),
                html.Td(n["type"]),
                html.Td(length_str if n["length"] else "-"),
                html.Td(n["comment"] if n["comment"] else "-"),
            ])

        sections = []

        if knitting:
            knitting_rows = [build_row(n, is_hook=False) for n in knitting]
            knitting_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Size (Metric / US)"),
                        html.Th("Type"),
                        html.Th("Length"),
                        html.Th("Comment"),
                    ], className="table-success")
                ]),
                html.Tbody(knitting_rows)
            ], striped=True, bordered=True, hover=True, responsive=True, className="mt-3 table-dark")
            
            sections.append(html.Div([
                html.H5("Knitting Needles", className="text-success mt-4"),
                knitting_table
            ]))

        if crochet:
            crochet_rows = [build_row(n, is_hook=True) for n in crochet]
            crochet_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Size (Metric / Hook)"),
                        html.Th("Type"),
                        html.Th("Length"),
                        html.Th("Comment"),
                    ], className="table-info")
                ]),
                html.Tbody(crochet_rows)
            ], striped=True, bordered=True, hover=True, responsive=True, className="mt-3 table-dark")
            
            sections.append(html.Div([
                html.H5("Crochet Hooks", className="text-info mt-4"),
                crochet_table
            ]))

        return html.Div(sections)
