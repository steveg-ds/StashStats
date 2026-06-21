"""MVC Controller layer for StashStats. Wires together the Model and UI components, orchestrating search and stash interactions."""
import datetime
from typing import Any, Dict, List, Tuple, Union, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from .base import Base
from .components import (
    Header, Search, SearchResults, StashCard, EditModal, AnalyticsComponent,
    ProjectsComponent
)
from .model import Model


class AppController(Base):
    """
    Orchestrates interactions between the Model layer and Dash UI components.

    - Properties:
        - MODEL (Model): Data layer for Ravelry API calls.
        - HEADER (Header): Page header component.
        - SEARCH (Search): Search bar component.
        - SEARCH_RESULTS (SearchResults): Results display component.
        - STASH_CARD (StashCard): Component for rendering individual stash cards.
        - EDIT_MODAL (EditModal): Component for editing stash entries.
        - ANALYTICS (AnalyticsComponent): Component for visualising stash analytics.
    - Methods:
        - create_initial_layout: Builds the top-level tabbed Dash layout.
        - search_yarn: Runs a yarn search and returns rendered accordion results.
        - render_stash_tab_layout: Renders the layout structure for the personal stash tab.
        - render_stash_cards: Filters stash list and renders cards.
        - render_analytics_layout: Renders layout structure for the analytics tab.
        - render_analytics_content: Generates the figure objects and stats cards.
        - render_remaining_preview: Calculations live preview in log usage modal tab.
        - handle_add_to_stash: Wires adding a yarn search result to Ravelry stash.
        - handle_save_edit: Wires modal save for both usage and details tabs.
        - toggle_edit_modal: Wire triggering/populating the edit modal.
    """

    def __init__(
        self,
        header_id: str,
        search_id: str,
        result_id: str,
        stash_card_id: str = "app-stash-card",
        modal_id: str = "edit-stash-modal-container",
        analytics_id: str = "app-analytics"
    ):
        """
        Initialise controller with component IDs used as Dash element identifiers.
        - Input
            - header_id (str): DOM id for the header container.
            - search_id (str): DOM id for the search bar container.
            - result_id (str): DOM id for the search results container.
            - stash_card_id (str): DOM id for stash cards component. Defaults to 'app-stash-card'.
            - modal_id (str): DOM id for edit modal container. Defaults to 'edit-stash-modal'.
            - analytics_id (str): DOM id for analytics container. Defaults to 'app-analytics'.
        """
        self.MODEL: 'Model' = Model()
        self.HEADER: 'Header' = Header(container_id=header_id)
        self.SEARCH: 'Search' = Search(container_id=search_id)
        self.SEARCH_RESULTS: 'SearchResults' = SearchResults(container_id=result_id)
        self.STASH_CARD: 'StashCard' = StashCard(container_id=stash_card_id)
        self.EDIT_MODAL: 'EditModal' = EditModal(container_id=modal_id)
        self.ANALYTICS: 'AnalyticsComponent' = AnalyticsComponent(container_id=analytics_id)
        self.PROJECTS: 'ProjectsComponent' = ProjectsComponent(container_id="app-projects")

    def create_initial_layout(self) -> List[dbc.Container]:
        """
        Build the top-level Dash layout with tabbed navigation.
        - output: List containing the header container and a tabbed panel with Personal Stash, Stash Analytics, and Yarn Search tabs.
        """
        username = self.MODEL.get_current_username()
        self.HEADER.update_layout(username)
        tabs_layout = html.Div(
            [
                dcc.Tabs(
                    id="app-tabs",
                    value="tab-search",
                    children=[
                        dcc.Tab(
                            label="Personal Stash",
                            value="tab-stash",
                            children=[
                                html.Div(style={"height": "20px"}),
                                dbc.Container(id="stash-tab-content")
                            ],
                            style={"backgroundColor": "#222", "color": "#fff"},
                            selected_style={"backgroundColor": "#333", "color": "#00bc8c"}
                        ),
                        dcc.Tab(
                            label="Stash Analytics",
                            value="tab-analytics",
                            children=[
                                html.Div(style={"height": "20px"}),
                                dbc.Container(id="analytics-tab-content")
                            ],
                            style={"backgroundColor": "#222", "color": "#fff"},
                            selected_style={"backgroundColor": "#333", "color": "#00bc8c"}
                        ),
                        dcc.Tab(
                            label="Projects",
                            value="tab-projects",
                            children=[
                                html.Div(style={"height": "20px"}),
                                dbc.Container(id="projects-tab-content")
                            ],
                            style={"backgroundColor": "#222", "color": "#fff"},
                            selected_style={"backgroundColor": "#333", "color": "#00bc8c"}
                        ),
                        dcc.Tab(
                            label="Yarn Search",
                            value="tab-search",
                            children=[
                                html.Div(style={"height": "20px"}),
                                self.SEARCH.container,
                                self.SEARCH_RESULTS.container,
                            ],
                            style={"backgroundColor": "#222", "color": "#fff"},
                            selected_style={"backgroundColor": "#333", "color": "#00bc8c"}
                        )
                    ],
                    style={"overflowX": "auto"}
                )
            ]
        )

        return [
            self.HEADER.container,
            dbc.Container(tabs_layout),
            self.EDIT_MODAL.container
        ]

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
        category: str = None,
    ) -> dbc.Col:
        """
        Execute a yarn search and render results as an accordion.
        - Input
            - query (str): Search keyword(s).
            - sort (str): Sort order. Defaults to 'best'.
            - category (str): Optional category filter.
        - output: dbc.Col with accordion of results, or html.Div('No results found.').
        """
        sort_map = {
            "best_match": "best",
            "highest_rating": "rating",
            "most_projects": "projects"
        }
        api_sort = sort_map.get(sort, sort)
        yarns = self.MODEL.search_yarn(query=query, sort=api_sort, category=category)

        if yarns is not None:
            self.LOGGER.debug(f"Query: {query}, # of Yarns Found: {len(yarns)}")
            
            accordion_items: List[dbc.AccordionItem] = []
            for y in yarns:
                full_yarn = self.MODEL.get_full_yarn(y.id)
                if not full_yarn:
                    full_yarn = y
                
                if full_yarn.photos:
                    photo_urls = [p.medium for p in full_yarn.photos]
                else:
                    from .dataclasses import YarnPhotos
                    photo_urls = [YarnPhotos().medium]
                
                item = self.SEARCH_RESULTS.create_search_result(
                    id=full_yarn.id,
                    name=full_yarn.name,
                    company=full_yarn.company,
                    grams=full_yarn.grams,
                    yardage=full_yarn.yardage,
                    discontinued=full_yarn.discontinued,
                    machine_washable=full_yarn.machine_washable,
                    colorways=full_yarn.colorways,
                    photos=photo_urls,
                )
                accordion_items.append(item)
                
            return dbc.Col(dbc.Accordion(accordion_items, start_collapsed=True), width=12) # modified width for mobile-friendly search results wrapper width
        else:
            self.LOGGER.error(f'Query: {query}, No Results Found')
            return html.Div("No results found.")

    def render_stash_tab_layout(self) -> html.Div:
        """
        Render layout structure for Personal Stash tab.
        - output: html.Div container.
        """
        # Placing search query and sorting inputs side-by-side using Bootstrap columns.
        # xs=12 stacks on mobile/small screens; md=8 and md=4 sum to 12 to align them on medium+ screens.
        search_col = dbc.Col(
            dbc.Input(
                id="stash-search-query",
                placeholder="Filter stash by yarn name, brand, or colorway...",
                className="mb-4 mt-3",
                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #444"},
                debounce=True
            ),
            xs=12, md=8
        )
        sort_col = dbc.Col(
            dbc.Select(
                id="stash-sort-by",
                options=[
                    {"label": "Brand (A-Z)", "value": "brand_asc"},
                    {"label": "Name (A-Z)", "value": "name_asc"},
                    {"label": "Quantity (High-Low)", "value": "qty_desc"},
                    {"label": "Date Added (Newest)", "value": "date_desc"}
                ],
                value="brand_asc",
                className="mb-4 mt-3",
                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #444"}
            ),
            xs=12, md=4
        )
        filter_row = dbc.Row([search_col, sort_col])

        pagination = dbc.Pagination(
            id="stash-page",
            active_page=1,
            max_value=1,
            fully_expanded=False,
            previous_next=True,
            class_name="justify-content-center"
        )
        pagination.page_count = 1

        # Instantiate pagination row below the stash container list to navigate through pages.
        pagination_row = dbc.Row(
            dbc.Col(
                pagination,
                width=12,
                className="mt-3 d-flex justify-content-center"
            )
        )

        return html.Div(
            [
                html.H4("My Personal Stash", className="mt-3 text-success"),
                html.P("Browse and filter your stashed yarn collection."),
                filter_row,
                dbc.Row(id="stash-list-container"),
                pagination_row
            ]
        )

    def render_stash_cards(
        self,
        query: Optional[str],
        sort_by: str = "brand_asc",
        active_page: Optional[int] = None
    ) -> Union[List[dbc.Col], Tuple[List[dbc.Col], int]]:
        """
        Filter, group by yarn, and render stash accordion list.
        - Input:
            - query (str | None): Search query for stash filtration.
            - sort_by (str): Sorting criteria. Defaults to 'brand_asc'.
            - active_page (int | None): Currently active page. Defaults to None.
        - output: List of dbc.Col containing the single accordion container, or a tuple of (list, total_pages) if page is specified.
        """
        stash_list = self.MODEL.get_stash_list()
        if not stash_list:
            fallback_msg = [html.Div("No stashed yarns found or API request failed.", className="text-warning mt-3")]
            return (fallback_msg, 1) if active_page is not None else fallback_msg

        filtered = stash_list
        if query:
            q = query.lower()
            filtered = []
            for s in stash_list:
                name = (s.get("name") or "").lower()
                yarn_info = s.get("yarn") or {}
                brand = (yarn_info.get("yarn_company_name") or "").lower()
                colorway = (s.get("colorway_name") or "").lower()
                if q in name or q in brand or q in colorway:
                    filtered.append(s)

        if not filtered:
            fallback_msg = [html.Div("No matching stash entries found.", className="text-info mt-3 ms-2")]
            return (fallback_msg, 1) if active_page is not None else fallback_msg

        # Group metrics computing loop. Organises stash list entries by unique brand/name combinations.
        # Aggregates totals per group (e.g. skeins, yards) to extract total skeins and max dates for sorting.
        grouped_data = {}
        from .model import get_primary_totals
        for s in filtered:
            yarn_info = s.get("yarn") or {}
            brand = yarn_info.get("yarn_company_name") or "Unknown Brand"
            name = yarn_info.get("name") or s.get("name") or "Unnamed Yarn"
            key = (brand, name)
            
            packs = s.get("packs") or []
            totals = get_primary_totals(packs, yarn_info)
            
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append((s, totals))

        # Sorting branching logic to order the grouped stash records based on selected dropdown value.
        if sort_by == "name_asc":
            sorted_groups = sorted(
                grouped_data.items(),
                key=lambda x: (x[0][1].lower(), x[0][0].lower())
            )
        elif sort_by == "qty_desc":
            # qty_desc branch calculates total skeins across all items in group to sort descending.
            sorted_groups = sorted(
                grouped_data.items(),
                key=lambda x: (
                    -sum(totals.get("skeins") or 0.0 for _, totals in x[1]),
                    x[0][0].lower(),
                    x[0][1].lower()
                )
            )
        elif sort_by == "date_desc":
            # date_desc parses creation timestamps to float representation to perform chronological sorting.
            import datetime
            def get_group_max_timestamp(items):
                max_ts = 0.0
                for s, _ in items:
                    c_at = s.get("created_at")
                    if c_at:
                        try:
                            dt = datetime.datetime.strptime(c_at.split(" ")[0], "%Y/%m/%d")
                            ts = dt.timestamp()
                            if ts > max_ts:
                                max_ts = ts
                        except Exception:
                            pass
                return max_ts

            sorted_groups = sorted(
                grouped_data.items(),
                key=lambda x: (
                    -get_group_max_timestamp(x[1]),
                    x[0][0].lower(),
                    x[0][1].lower()
                )
            )
        else: # Default: brand_asc
            sorted_groups = sorted(
                grouped_data.items(),
                key=lambda x: (x[0][0].lower(), x[0][1].lower())
            )

        # Pagination logic: calculates the ceiling total page count (math.ceil)
        # and slices the sorted groups using the current active page index.
        import math
        total_groups = len(sorted_groups)
        page_count = max(1, math.ceil(total_groups / 10))
        
        if active_page is not None:
            active_page = max(1, min(active_page, page_count))
            start_idx = (active_page - 1) * 10
            end_idx = start_idx + 10
            sliced_groups = sorted_groups[start_idx:end_idx]
        else:
            sliced_groups = sorted_groups

        accordion_items = []
        for (brand, name), items in sliced_groups:
            # Calculate combined totals
            comb_t = {"yards": 0.0, "meters": 0.0, "skeins": 0.0, "grams": 0.0}
            for _, totals in items:
                comb_t["yards"] += totals.get("yards") or 0.0
                comb_t["meters"] += totals.get("meters") or 0.0
                comb_t["skeins"] += totals.get("skeins") or 0.0
                comb_t["grams"] += totals.get("grams") or 0.0

            # Wrap details and item lists into accordion group card components.
            accordion_item = self.STASH_CARD.create_grouped_accordion_item(
                brand=brand,
                name=name,
                items_with_totals=items,
                combined_totals=comb_t
            )
            accordion_items.append(accordion_item)

        cols = [dbc.Col(item, width=12) for item in accordion_items]
        # Return either a tuple containing (columns list, total_pages) if page is specified, or only columns list.
        if active_page is not None:
            return cols, page_count
        else:
            return cols

    def render_analytics_layout(self) -> dbc.Row:
        """
        Render basic structural layout for analytics tab content.
        - output: dbc.Row container from AnalyticsComponent.
        """
        layout = self.ANALYTICS.create_init_layout("yards")
        content = self.render_analytics_content("yards")
        layout.children[0].children[3].children = content
        return layout

    def render_analytics_content(self, selected_metric: str, moving_average: bool = False) -> html.Div:
        """
        Extract data and render visual elements for analytics page.
        - Input
            - selected_metric (str): Selected metric option.
            - moving_average (bool): True if showing moving average.
        - output: html.Div container.
        """
        stash_list = self.MODEL.get_stash_list()
        if not stash_list:
            return html.Div("No stashed yarns found or API request failed.", className="text-warning mt-3")

        proj_map = self.MODEL.get_project_map()
        daily_df = self.MODEL.get_analytics_dataframe(stash_list, proj_map)

        if daily_df.empty:
            return html.Div("No valid stashed yarn records with creation dates found.", className="text-info mt-3")

        curr_yards = daily_df["cumulative_yards"].iloc[-1]
        curr_meters = daily_df["cumulative_meters"].iloc[-1]
        curr_skeins = daily_df["cumulative_skeins"].iloc[-1]
        curr_grams = daily_df["cumulative_grams"].iloc[-1]

        stats_cards = self.ANALYTICS.build_stats_cards(
            curr_yards=curr_yards,
            curr_meters=curr_meters,
            curr_skeins=curr_skeins,
            curr_grams=curr_grams,
            selected_metric=selected_metric,
        )

        if selected_metric == "animated":
            df = self.MODEL.get_animated_analytics_dataframe(stash_list, proj_map)
            fig = self.ANALYTICS.build_animated_figure(df, is_mobile=True)
            return html.Div(
                [
                    stats_cards,
                    dcc.Graph(figure=fig, config={'responsive': True}, style={'minWidth': '0'})
                ]
            )

        df = daily_df

        if moving_average:
            import pandas as pd
            df_daily = df.set_index("date").resample("D").asfreq()
            cumulative_cols = ["cumulative_yards", "cumulative_meters", "cumulative_skeins", "cumulative_grams"]
            df_daily[cumulative_cols] = df_daily[cumulative_cols].ffill()
            df_daily[cumulative_cols] = df_daily[cumulative_cols].fillna(0.0)
            for col in cumulative_cols:
                df_daily[col] = df_daily[col].rolling(window=30, min_periods=1).mean()
            df = df_daily.reset_index()

        if selected_metric == "all":
            figs = {}
            for k, m_info in self.ANALYTICS.METRIC_MAP.items():
                figs[k] = self.ANALYTICS.build_figure(df, m_info, is_mobile=True, moving_average=moving_average)
            grid = self.ANALYTICS.build_grid(figs)
            return html.Div([stats_cards, grid])
        else:
            m_info = self.ANALYTICS.METRIC_MAP.get(selected_metric, self.ANALYTICS.METRIC_MAP["yards"])
            fig = self.ANALYTICS.build_figure(df, m_info, is_mobile=True, moving_average=moving_average)
            return html.Div(
                [
                    stats_cards,
                    dcc.Graph(figure=fig, config={'responsive': True}, style={'minWidth': '0'})
                ]
            )

    def render_remaining_preview(self, used: Optional[float], current_skeins: Optional[float]) -> html.Div:
        """
        Generate preview calculations content for edit modal.
        - Input
            - used (float | None): Cents of skeins used.
            - current_skeins (float | None): Total skeins baseline quantity.
        - output: html.Div.
        """
        if used is None:
            return html.Span("Enter an amount above to see what will remain.", className="text-muted small")

        current = float(current_skeins or 0)
        used_f = float(used)
        remaining = current - used_f

        if used_f < 0:
            return html.Span("Amount used can't be negative.", className="text-danger small")
        if used_f > current:
            return html.Div(
                [
                    html.Span(f"⚠ Used ({used_f:.2g}) exceeds current ({current:.2g} skeins). ", className="text-warning small"),
                    html.Span("Remaining will be set to 0.", className="text-warning small"),
                ]
            )

        return html.Div(
            [
                html.Div(
                    [
                        html.Span("Currently have: ", className="text-muted small"),
                        html.Strong(f"{current:.2g} skeins", className="text-white"),
                    ],
                    className="mb-1"
                ),
                html.Div(
                    [
                        html.Span("Used: ", className="text-muted small"),
                        html.Strong(f"{used_f:.2g} skeins", className="text-warning"),
                        html.Span("  →  Remaining: ", className="text-muted small"),
                        html.Strong(f"{remaining:.2g} skeins", className="text-success"),
                    ]
                ),
            ]
        )

    def handle_add_to_stash(
        self,
        yarn_id: Union[str, int],
        skeins: Optional[float],
        colorway: Optional[str],
        dyelot: Optional[str],
        location: Optional[str],
        notes: Optional[str],
        date_added: Optional[str] = None
    ) -> str:
        """
        Structure payload and execute stash addition API.
        - Input
            - yarn_id (str | int): ID of target yarn.
            - skeins (float | None): Weight/skeins quantity.
            - colorway (str | None): Chosen color variant.
            - dyelot (str | None): Dyelot code.
            - location (str | None): Physical location.
            - notes (str | None): Stash notes.
            - date_added (str | None): Date stash was added.
        - output: Text response explaining API result.
        """
        stash_payload = {
            "yarn_id": int(yarn_id),
            "stash_status_id": 1
        }
        if colorway:
            stash_payload["colorway_name"] = colorway
        if dyelot:
            stash_payload["dye_lot"] = dyelot
        if location:
            stash_payload["location"] = location
        if notes:
            stash_payload["notes"] = notes
        if skeins is not None and skeins != "":
            stash_payload["pack"] = {"skeins": float(skeins)}
            if date_added:
                stash_payload["pack"]["purchased_date"] = date_added
        elif date_added:
            stash_payload["pack"] = {"purchased_date": date_added}
            
        try:
            response = self.MODEL.create_stash(stash_payload)
            if response and 'stash' in response:
                stash_id = response['stash'].get('id', 'Unknown')
                return f"Success! Stashed with ID: {stash_id}"
            else:
                return "Failed to stash yarn. Please verify credentials."
        except Exception as e:
            return f"Error occurred: {str(e)}"

    def handle_save_edit(
        self,
        stash_id: Union[str, int],
        active_tab: str,
        colorway: Optional[str],
        dyelot: Optional[str],
        location: Optional[str],
        notes: Optional[str],
        skeins: Optional[float],
        status_id: Optional[int],
        used_skeins: Optional[float],
        current_skeins: Optional[float],
        usage_date: Optional[str] = None,
    ) -> Tuple[str, bool]:
        """
        Process the updates and save changes via model.
        - Input
            - stash_id (str | int): Target stash entry.
            - active_tab (str): Active tab ID in the modal.
            - colorway (str | None): Colorway updates.
            - dyelot (str | None): Dye lot updates.
            - location (str | None): Storage location updates.
            - notes (str | None): Notes updates.
            - skeins (float | None): Count of total skeins.
            - status_id (int | None): Selected stash status.
            - used_skeins (float | None): Count of used skeins (usage log).
            - current_skeins (float | None): Stashed skeins baseline.
            - usage_date (str | None): Date yarn was used.
        - output: Tuple of status message and modal visibility boolean.
        """
        if active_tab == "modal-tab-usage":
            if used_skeins is None:
                return "Enter an amount used first.", True
            current = float(current_skeins or 0)
            used_f = float(used_skeins)
            if used_f < 0:
                return "Amount used can't be negative.", True
            remaining = max(0.0, current - used_f)
            payload = {"pack": {"skeins": remaining}}
            if usage_date:
                from .db import DBManager
                DBManager.set_pending_usage_date(stash_id, usage_date)
            try:
                result = self.MODEL.update_stash(stash_id, payload)
                if result and "stash" in result:
                    self.LOGGER.info(f"[WRITE] stash_id={stash_id} | usage | used={used_f} remaining={remaining}")
                    return f"Saved! {used_f:.2g} skeins used → {remaining:.2g} remaining. Refresh stash tab to update list.", False
                else:
                    self.LOGGER.warning(f"[WRITE FAILED] stash_id={stash_id} | usage | payload={payload}")
                    return "Save failed — check logs.", True
            except Exception as e:
                self.LOGGER.error(f"[WRITE ERROR] stash_id={stash_id} | {e}")
                return f"Error: {e}", True
        else:
            payload = {"stash_status_id": int(status_id) if status_id else 1}
            if colorway is not None:
                payload["colorway_name"] = colorway
            if dyelot is not None:
                payload["dye_lot"] = dyelot
            if location is not None:
                payload["location"] = location
            if notes is not None:
                payload["notes"] = notes
            if skeins is not None:
                payload["pack"] = {"skeins": float(skeins)}
            try:
                result = self.MODEL.update_stash(stash_id, payload)
                if result and "stash" in result:
                    self.LOGGER.info(f"[WRITE] stash_id={stash_id} | details | payload={payload}")
                    return "Saved! Refresh the stash tab to see updates.", False
                else:
                    self.LOGGER.warning(f"[WRITE FAILED] stash_id={stash_id} | details | payload={payload}")
                    return "Save failed — check logs.", True
            except Exception as e:
                self.LOGGER.error(f"[WRITE ERROR] stash_id={stash_id} | {e}")
                return f"Error: {e}", True

    def build_history_table(self, stash_id: str) -> html.Div:
        history = self.MODEL.get_stash_history(stash_id)
        if not history:
            return html.Div("No usage history logged yet.", className="text-muted small mt-2")
        
        rows = []
        for event in reversed(history):
            sk = -event.get("skeins", 0.0)
            yds = -event.get("yards", 0.0)
            g = -event.get("grams", 0.0)
            date = event.get("date", "Unknown Date")
            
            rows.append(html.Tr([
                html.Td(date),
                html.Td(f"{sk:.2f} sk"),
                html.Td(f"{yds:,.0f} yds"),
                html.Td(f"{g:,.0f} g"),
            ]))
            
        table = dbc.Table(
            [
                html.Thead(html.Tr([html.Th("Date"), html.Th("Skeins"), html.Th("Yards"), html.Th("Weight")])),
                html.Tbody(rows)
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            size="sm",
            style={"fontSize": "0.85rem", "color": "#ccc", "borderColor": "#555"}
        )
        return html.Div([
            html.H6("Usage History", className="text-success mt-3 mb-2"),
            table
        ])

    def toggle_edit_modal(
        self,
        edit_clicks: list,
        cancel_click: Any,
        store_data_list: list,
        btn_ids: list,
        triggered_id: str,
    ) -> Tuple[bool, Any, Any, Any, Any, Any, Any, Any, Any, str, Any, str, str, Any, Any]:
        """
        Handle opening the edit modal and loading the correct initial state.
        - Input
            - edit_clicks (list): Edit buttons click counts.
            - cancel_click (Any): Cancel click count.
            - store_data_list (list): Data list from individual card stores.
            - btn_ids (list): IDs of triggered edit buttons.
            - triggered_id (str): Raw dash trigger identification.
        - output: Tuple representing all values needed for modal callback output.
        """
        import json
        from dash import no_update
        
        if "edit-stash-cancel-btn" in triggered_id:
            return False, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", None, "modal-tab-details", datetime.date.today().isoformat(), no_update, None

        try:
            triggered_obj = json.loads(triggered_id.split(".")[0])
            btn_index = triggered_obj.get("index", "")
        except Exception:
            return (no_update,) * 14

        sd = None
        for data in (store_data_list or []):
            if data and str(data.get("id")) == str(btn_index):
                sd = data
                break

        clicks = None
        for i, btn_id in enumerate(btn_ids or []):
            if str(btn_id.get("index", "")) == str(btn_index):
                if i < len(edit_clicks):
                    clicks = edit_clicks[i]
                break

        if not clicks:
            return (no_update,) * 15

        if not sd:
            return (no_update,) * 15

        current_skeins = sd.get("skeins") or 0
        yarn_name = sd.get("name") or "Unnamed Yarn"
        history_table = self.build_history_table(sd.get("id"))
        return (
            True,
            {"id": sd.get("id"), "name": yarn_name},
            current_skeins,
            sd.get("colorway") or "",
            sd.get("dye_lot") or "",
            sd.get("location") or "",
            sd.get("notes") or "",
            current_skeins,
            sd.get("status_id") or 1,
            "",
            None,
            "modal-tab-details",
            datetime.date.today().isoformat(),
            f"edit entry: {yarn_name}",
            history_table,
        )

    def render_projects_tab_layout(self) -> html.Div:
        """Render layout structure for Projects tab."""
        return self.PROJECTS.create_init_layout()

    def render_projects_list(self) -> List[dbc.Col]:
        """Fetch and render projects as card components."""
        projects = self.MODEL.get_projects_list()
        if not projects:
            return [dbc.Col(html.Div("No projects found or API request failed.", className="text-warning mt-3"))]
        return [self.PROJECTS.build_project_card(p) for p in projects]



