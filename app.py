import json
import os
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

load_dotenv(override=False)

LOGGER = create_logger(
    logger_name='AppLogger',
    log_file='dev_changes.log' if os.getenv("DEV_LOGGING") == "1" else None
)

app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* DARKLY expanded accordion: active-bg=#ebeff2 (light), active-color=#325172 (dark) = unreadable */
            .accordion-button:not(.collapsed) {
                color: #fff !important;
                background-color: #303030 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


CONTROLLER = AppController(
    header_id="app-header",
    search_id="app-search",
    result_id="app-results"
)

def serve_layout():
    return dbc.Container(children=CONTROLLER.create_initial_layout())

app.layout = serve_layout


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
    return CONTROLLER.search_yarn(query=query, sort=sort, category=category)


@callback(
    Output({"type": "search-collapse", "index": MATCH}, "is_open"),
    Input({"type": "search-collapse-btn", "index": MATCH}, "n_clicks"),
    State({"type": "search-collapse", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_search_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open



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
    Input("analytics-moving-average-checkbox", "value"),
)
def update_analytics_content(selected_metric, moving_average):
    return CONTROLLER.render_analytics_content(selected_metric, moving_average)


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
    Output("stash-page", "max_value"),
    Output("stash-page", "active_page"),
    Input("stash-search-query", "value"),
    Input("stash-sort-by", "value"),
    Input("stash-page", "active_page"),
    Input("app-tabs", "value"),
    Input("stash-update-trigger", "data"),
)
def filter_stash_items(query, sort_by, active_page, tab_value, trigger_data):
    # Callback Inputs/Outputs tie together search query, sorting, active page, current tab, and update trigger.
    # Inputs: query, sort_by, active_page, tab_value, trigger_data.
    # Outputs: Stash list cards, total pages (max_value), and the active page.
    if tab_value != "tab-stash":
        return no_update, no_update, no_update
    
    # Context parsing: Check which input triggered the callback.
    # If the search query or sorting option is changed, reset the page to 1.
    ctx = callback_context
    triggered_id = ""
    if ctx.triggered:
        triggered_id = ctx.triggered[0]["prop_id"]
    
    if "stash-search-query" in triggered_id or "stash-sort-by" in triggered_id:
        active_page = 1

    sort_by = sort_by or "brand_asc"
    active_page = active_page or 1
    
    # Call the controller to render stash cards and calculate total pages based on current filters.
    # Returns: lists of cards, total pages count, and the active page value.
    cards, total_pages = CONTROLLER.render_stash_cards(query, sort_by, active_page)
    return cards, total_pages, active_page


@callback(
    Output({"type": "yarn-collapse", "index": MATCH}, "is_open"),
    Input({"type": "yarn-collapse-btn", "index": MATCH}, "n_clicks"),
    State({"type": "yarn-collapse", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_yarn_collapse(n_clicks, is_open):
    if n_clicks is None or not n_clicks:
        raise PreventUpdate
    return not is_open


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
    Output("edit-stash-modal-tabs", "value"),
    Output("edit-stash-usage-date", "value"),
    Output("edit-stash-modal-title", "children"),
    Output("edit-stash-history-table", "children"),
    Output("edit-stash-original-info", "children"),
    Input({"type": "stash-edit-btn", "index": ALL}, "n_clicks"),
    Input("edit-stash-cancel-btn", "n_clicks"),
    State({"type": "stash-data-store", "index": ALL}, "data"),
    State({"type": "stash-edit-btn", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def toggle_edit_modal(edit_clicks, cancel_click, store_data_list, btn_ids):
    # State passing and validation of parameters/inputs:
    # State containing list of stash items' data and their button IDs is passed.
    # Trigger is validated using callback context to see if modal is opened or cancelled.
    # If open is requested, validates that a click actually occurred before continuing.
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    triggered_id = ctx.triggered[0]["prop_id"]
    if "edit-stash-cancel-btn" not in triggered_id:
        if not edit_clicks or not any(click for click in edit_clicks if click):
            raise PreventUpdate
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
    Output("stash-update-trigger", "data"),
    Input("edit-stash-save-btn", "n_clicks"),
    State("edit-stash-id-store", "data"),
    State("edit-stash-modal-tabs", "value"),
    State("edit-stash-colorway", "value"),
    State("edit-stash-dyelot", "value"),
    State("edit-stash-location", "value"),
    State("edit-stash-notes", "value"),
    State("edit-stash-skeins", "value"),
    State("edit-stash-status", "value"),
    State("edit-stash-used-skeins", "value"),
    State("edit-stash-current-skeins-store", "data"),
    State("edit-stash-usage-date", "value"),
    State("stash-update-trigger", "data"),
    prevent_initial_call=True,
)
def save_stash_edit(n_clicks, stash_id, active_tab,
                    colorway, dyelot, location, notes, skeins, status_id,
                    used_skeins, current_skeins, usage_date, trigger_data):
    # State passing and validation:
    # Passes inputs from modal fields (colorway, dyelot, location, notes, skeins, status, usage_date)
    # and State stores (stash_id, current_skeins, active_tab, and the trigger tracker).
    # Validates parameters/inputs by checking that save button was clicked and stash_id exists.
    if not n_clicks or not stash_id:
        raise PreventUpdate
    actual_id = stash_id.get("id") if isinstance(stash_id, dict) else stash_id
    res_msg, is_open = CONTROLLER.handle_save_edit(
        actual_id, active_tab, colorway, dyelot, location, notes,
        skeins, status_id, used_skeins, current_skeins, usage_date
    )
    # Cache trigger incrementation:
    # If the modal is successfully saved and closed (is_open is False),
    # increment the update trigger tracker to refresh the stash list.
    new_trigger_data = trigger_data
    if not is_open:
        new_trigger_data = (trigger_data or 0) + 1
    return res_msg, is_open, new_trigger_data


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
    Output("edit-stash-delete-confirm", "displayed"),
    Input("edit-stash-delete-btn", "n_clicks"),
    prevent_initial_call=True,
)
def trigger_delete_confirm(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return True


@callback(
    Output("edit-stash-status-msg", "children", allow_duplicate=True),
    Output("edit-stash-modal", "is_open", allow_duplicate=True),
    Output("stash-update-trigger", "data", allow_duplicate=True),
    Input("edit-stash-delete-confirm", "submit_n_clicks"),
    State("edit-stash-id-store", "data"),
    State("stash-update-trigger", "data"),
    prevent_initial_call=True,
)
def handle_delete_confirm_submit(submit_n_clicks, stash_id, trigger_data):
    if not submit_n_clicks or not stash_id:
        raise PreventUpdate
    
    actual_id = stash_id.get("id") if isinstance(stash_id, dict) else stash_id
    stash_type = stash_id.get("type", "yarn") if isinstance(stash_id, dict) else "yarn"
    
    res_msg, is_open = CONTROLLER.handle_delete_stash(actual_id, stash_type)
    
    new_trigger_data = trigger_data
    if not is_open:
        new_trigger_data = (trigger_data or 0) + 1
        
    return res_msg, is_open, new_trigger_data

@callback(
    Output("edit-stash-history-table", "children", allow_duplicate=True),
    Output("edit-stash-status-msg", "children", allow_duplicate=True),
    Output("stash-update-trigger", "data", allow_duplicate=True),
    Input({"type": "delete-usage-btn", "index": ALL}, "n_clicks"),
    State("edit-stash-id-store", "data"),
    State("stash-update-trigger", "data"),
    prevent_initial_call=True,
)
def delete_usage_entry(delete_clicks, stash_store_data, trigger_data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
        
    triggered_id = ctx.triggered[0]["prop_id"]
    if "n_clicks" not in triggered_id:
        raise PreventUpdate
        
    try:
        triggered_obj = json.loads(triggered_id.split(".")[0])
        event_id = triggered_obj.get("index", "")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        LOGGER.debug(f"Failed to parse delete-usage-btn ID '{triggered_id}': {e}")
        raise PreventUpdate
        
    if not event_id:
        raise PreventUpdate
        
    actual_id = stash_store_data.get("id") if isinstance(stash_store_data, dict) else stash_store_data
    if not actual_id:
        raise PreventUpdate
        
    success = CONTROLLER.MODEL.delete_stash_history_event(int(event_id))
    if success:
        new_table = CONTROLLER.build_history_table(str(actual_id))
        msg = html.Span("Usage entry deleted.", className="text-success")
        new_trigger = (trigger_data or 0) + 1
        return new_table, msg, new_trigger
    else:
        new_table = CONTROLLER.build_history_table(str(actual_id))
        msg = html.Span("Failed to delete usage entry.", className="text-danger")
        return new_table, msg, no_update


@callback(
    Output("stash-sync-status-msg", "children"),
    Output("stash-sync-badge", "children"),
    Output("stash-sync-badge", "color"),
    Output("stash-update-trigger", "data", allow_duplicate=True),
    Input("stash-sync-btn", "n_clicks"),
    State("stash-update-trigger", "data"),
    prevent_initial_call=True,
)
def handle_manual_sync(n_clicks, trigger_data):
    if not n_clicks:
        raise PreventUpdate
    count = CONTROLLER.execute_batch_sync()
    new_trigger = (trigger_data or 0) + 1
    msg = f"Synced {count} items successfully."
    return msg, "0 pending", "secondary", new_trigger


if __name__ == "__main__":
    debug_mode = os.getenv('APP_DEBUG', 'false').lower() == 'true'
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8050")),
        debug=debug_mode,
        dev_tools_hot_reload=debug_mode,
    )

