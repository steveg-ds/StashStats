import json
from dash import (
    Dash,
    Input,
    Output,
    State,
    callback,
    callback_context,
    dcc,
    html,
    no_update,
    MATCH,
    ALL,
)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from stashies.app_controller import AppController
from stashies.utils import create_logger

load_dotenv(override=True)

LOGGER = create_logger(logger_name='AppLogger', log_file='dev_changes.log')

app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)
server = app.server

CONTROLLER = AppController(
    header_id="app-header",
    search_id="app-search",
    result_id="app-results"
)

app.layout = dbc.Container(children=CONTROLLER.create_initial_layout())


@callback(
    Output("app-results", "children"),
    Input("search-button", "n_clicks"),
    State("search-query", "value"),
    State("search-sort", "value"),
    State("search-category", "value"),
)
def handle_search(n_clicks, query, sort, category):
    if not query:
        raise PreventUpdate
    return CONTROLLER.search_yarn(query=query, sort=sort)


@callback(
    Output({"type": "stash-status-msg", "index": MATCH}, "children"),
    Input({"type": "stash-submit-btn", "index": MATCH}, "n_clicks"),
    State({"type": "stash-skeins", "index": MATCH}, "value"),
    State({"type": "stash-colorway", "index": MATCH}, "value"),
    State({"type": "stash-dyelot", "index": MATCH}, "value"),
    State({"type": "stash-location", "index": MATCH}, "value"),
    State({"type": "stash-notes", "index": MATCH}, "value"),
    State({"type": "stash-date-added", "index": MATCH}, "date"),
    State({"type": "stash-submit-btn", "index": MATCH}, "id"),
)
def handle_add_to_stash(n_clicks, skeins, colorway, dyelot, location, notes, date_added, button_id):
    if n_clicks is None or not n_clicks:
        raise PreventUpdate
    yarn_id = button_id["index"]
    return CONTROLLER.handle_add_to_stash(yarn_id, skeins, colorway, dyelot, location, notes, date_added)


@callback(
    Output("analytics-tab-content", "children"),
    Input("app-tabs", "value"),
)
def render_analytics_layout(tab_value):
    if tab_value != "tab-analytics":
        return no_update
    return CONTROLLER.render_analytics_layout()


@callback(
    Output("analytics-content-area", "children"),
    Input("analytics-metric-selector", "value"),
)
def update_analytics_content(selected_metric):
    return CONTROLLER.render_analytics_content(selected_metric)


@callback(
    Output("stash-tab-content", "children"),
    Input("app-tabs", "value"),
)
def render_stash_tab(tab_value):
    if tab_value != "tab-stash":
        return no_update
    return CONTROLLER.render_stash_tab_layout()


@callback(
    Output("stash-list-container", "children"),
    Input("stash-search-query", "value"),
    Input("app-tabs", "value"),
)
def filter_stash_items(query, tab_value):
    if tab_value != "tab-stash":
        return no_update
    return CONTROLLER.render_stash_cards(query)


@callback(
    Output("edit-stash-modal", "is_open"),
    Output("edit-stash-id-store", "data"),
    Output("edit-stash-current-skeins-store", "data"),
    Output("edit-stash-colorway", "value"),
    Output("edit-stash-dyelot", "value"),
    Output("edit-stash-location", "value"),
    Output("edit-stash-notes", "value"),
    Output("edit-stash-skeins", "value"),
    Output("edit-stash-status", "value"),
    Output("edit-stash-status-msg", "children"),
    Output("edit-stash-used-skeins", "value"),
    Output("edit-stash-modal-tabs", "active_tab"),
    Output("edit-stash-usage-date", "date"),
    Input({"type": "stash-edit-btn", "index": ALL}, "n_clicks"),
    Input("edit-stash-cancel-btn", "n_clicks"),
    State({"type": "stash-data-store", "index": ALL}, "data"),
    State({"type": "stash-edit-btn", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def toggle_edit_modal(edit_clicks, cancel_click, store_data_list, btn_ids):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    triggered_id = ctx.triggered[0]["prop_id"]
    return CONTROLLER.toggle_edit_modal(edit_clicks, cancel_click, store_data_list, btn_ids, triggered_id)


@callback(
    Output("edit-stash-remaining-preview", "children"),
    Input("edit-stash-used-skeins", "value"),
    State("edit-stash-current-skeins-store", "data"),
    prevent_initial_call=True,
)
def update_remaining_preview(used, current_skeins):
    return CONTROLLER.render_remaining_preview(used, current_skeins)


@callback(
    Output("edit-stash-status-msg", "children", allow_duplicate=True),
    Output("edit-stash-modal", "is_open", allow_duplicate=True),
    Input("edit-stash-save-btn", "n_clicks"),
    State("edit-stash-id-store", "data"),
    State("edit-stash-modal-tabs", "active_tab"),
    State("edit-stash-colorway", "value"),
    State("edit-stash-dyelot", "value"),
    State("edit-stash-location", "value"),
    State("edit-stash-notes", "value"),
    State("edit-stash-skeins", "value"),
    State("edit-stash-status", "value"),
    State("edit-stash-used-skeins", "value"),
    State("edit-stash-current-skeins-store", "data"),
    State("edit-stash-usage-date", "date"),
    prevent_initial_call=True,
)
def save_stash_edit(n_clicks, stash_id, active_tab,
                    colorway, dyelot, location, notes, skeins, status_id,
                    used_skeins, current_skeins, usage_date):
    if not n_clicks or not stash_id:
        raise PreventUpdate
    return CONTROLLER.handle_save_edit(
        stash_id, active_tab, colorway, dyelot, location, notes,
        skeins, status_id, used_skeins, current_skeins, usage_date
    )


@callback(
    Output("projects-tab-content", "children"),
    Input("app-tabs", "value"),
)
def render_projects_tab(tab_value):
    if tab_value != "tab-projects":
        return no_update
    return CONTROLLER.render_projects_tab_layout()


@callback(
    Output("projects-list-container", "children"),
    Input("projects-tab-content", "children"),
    State("app-tabs", "value"),
)
def load_projects_list(tab_content, tab_value):
    if tab_value != "tab-projects" or not tab_content:
        raise PreventUpdate
    return CONTROLLER.render_projects_list()


@callback(
    Output("queue-tab-content", "children"),
    Input("app-tabs", "value"),
)
def render_queue_tab(tab_value):
    if tab_value != "tab-queue":
        return no_update
    return CONTROLLER.render_queue_tab_layout()


@callback(
    Output("queue-list-container", "children"),
    Input("queue-tab-content", "children"),
    State("app-tabs", "value"),
)
def load_queue_list(tab_content, tab_value):
    if tab_value != "tab-queue" or not tab_content:
        raise PreventUpdate
    return CONTROLLER.render_queue_list()


@callback(
    Output("needles-tab-content", "children"),
    Input("app-tabs", "value"),
)
def render_needles_tab(tab_value):
    if tab_value != "tab-needles":
        return no_update
    return CONTROLLER.render_needles_tab_layout()


@callback(
    Output("needles-list-container", "children"),
    Input("needles-tab-content", "children"),
    State("app-tabs", "value"),
)
def load_needles_list(tab_content, tab_value):
    if tab_value != "tab-needles" or not tab_content:
        raise PreventUpdate
    return CONTROLLER.render_needles_list()


@callback(
    Output("queue-list-container", "children", allow_duplicate=True),
    Input({"type": "queue-up-btn", "index": ALL}, "n_clicks"),
    Input({"type": "queue-down-btn", "index": ALL}, "n_clicks"),
    Input({"type": "queue-remove-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def handle_queue_actions(up_clicks, down_clicks, remove_clicks):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    triggered_prop = ctx.triggered[0]["prop_id"]
    try:
        btn_id_str = triggered_prop.split(".")[0]
        btn_id = json.loads(btn_id_str)
        btn_type = btn_id["type"]
        queue_id = btn_id["index"]
    except Exception:
        raise PreventUpdate
        
    n_clicks = ctx.triggered[0]["value"]
    if not n_clicks:
        raise PreventUpdate
        
    if btn_type == "queue-up-btn":
        CONTROLLER.handle_reposition_queue(queue_id, "up")
    elif btn_type == "queue-down-btn":
        CONTROLLER.handle_reposition_queue(queue_id, "down")
    elif btn_type == "queue-remove-btn":
        CONTROLLER.handle_remove_queue(queue_id)
        
    return CONTROLLER.render_queue_list()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        debug=True,
        dev_tools_hot_reload=True,
    )
