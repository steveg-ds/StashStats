from typing import Dict, List

import dash_bootstrap_components as dbc
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

from stashies.utils import create_logger
from stashies.app_controller import AppController
from dotenv import load_dotenv

load_dotenv()

LOGGER = create_logger(logger_name='AppLogger')

app = Dash(
    __name__,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Stash Stats",
)

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
    
    # We pass 'sort' to the controller, the user's Search component uses 'best_match' which may need mapping
    # but the API might accept it or ignore it. For now just pass it along.
    return CONTROLLER.search_yarn(query=query, sort=sort)


@callback(
    Output({"type": "stash-status-msg", "index": MATCH}, "children"),
    Input({"type": "stash-submit-btn", "index": MATCH}, "n_clicks"),
    State({"type": "stash-skeins", "index": MATCH}, "value"),
    State({"type": "stash-colorway", "index": MATCH}, "value"),
    State({"type": "stash-dyelot", "index": MATCH}, "value"),
    State({"type": "stash-location", "index": MATCH}, "value"),
    State({"type": "stash-notes", "index": MATCH}, "value"),
    State({"type": "stash-submit-btn", "index": MATCH}, "id"),
)
def handle_add_to_stash(n_clicks, skeins, colorway, dyelot, location, notes, button_id):
    if n_clicks is None or not n_clicks:
        raise PreventUpdate

    yarn_id = button_id["index"]
    
    # Structure data payload matching Stash (POST) schema requirements
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
        
    try:
        response = CONTROLLER.MODEL.create_stash(stash_payload)
        if response and 'stash' in response:
            stash_id = response['stash'].get('id', 'Unknown')
            return f"Success! Stashed with ID: {stash_id}"
        else:
            return "Failed to stash yarn. Please verify credentials."
    except Exception as e:
        return f"Error occurred: {str(e)}"


@callback(
    Output("analytics-tab-content", "children"),
    Input("app-tabs", "value"),
)
def render_analytics(tab_value):
    if tab_value != "tab-analytics":
        return no_update

    stash_list = CONTROLLER.MODEL.get_stash_list()
    if not stash_list:
        return html.Div("No stashed yarns found or API request failed.", className="text-warning mt-3")

    import pandas as pd
    import plotly.express as px

    # Extract date and yardage details
    data = []
    for s in stash_list:
        created_str = s.get("created_at")
        if not created_str:
            continue
            
        yarn_info = s.get("yarn") or {}
        yardage = yarn_info.get("yardage") or 0
        
        packs = s.get("packs") or []
        skeins = 1.0
        if packs:
            skeins_val = packs[0].get("skeins")
            if skeins_val is not None:
                skeins = float(skeins_val)
        
        total_yards = yardage * skeins
        
        try:
            date_part = created_str.split(" ")[0]
            dt = pd.to_datetime(date_part, format="%Y/%m/%d")
            data.append({"date": dt, "yards": total_yards})
        except Exception:
            continue

    if not data:
        return html.Div("No valid stashed yarn records with creation dates found.", className="text-info mt-3")

    df = pd.DataFrame(data)
    df = df.sort_values("date")
    
    df.set_index("date", inplace=True)
    df_monthly = df.resample("ME").sum().reset_index()
    df_monthly["cumulative_yards"] = df_monthly["yards"].cumsum()

    fig = px.line(
        df_monthly,
        x="date",
        y="cumulative_yards",
        title="Cumulative Stashed Yardage Over Time",
        labels={"date": "Date", "cumulative_yards": "Total Stashed Yards"},
        markers=True,
        template="plotly_dark"
    )
    
    fig.update_traces(line_color="#00bc8c")

    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H4("Stash Analytics Overview", className="mt-3 text-success"),
                    html.P("Analyzing total yardage of yarns in your personal stash."),
                    dcc.Graph(figure=fig)
                ],
                width=12
            )
        ]
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        debug=True,
        dev_tools_hot_reload=True,
    )

