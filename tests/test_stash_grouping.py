from unittest.mock import MagicMock
import dash_bootstrap_components as dbc
from dash import html
from stashies.app_controller import AppController

def test_render_stash_cards_grouping():
    # Setup controller with mocked model
    controller = AppController(header_id="h", search_id="s", result_id="r")
    controller.MODEL = MagicMock()
    
    # Mock two stash items sharing the same yarn brand and name
    mock_stash = [
        {
            "id": 1,
            "name": "Yarn A",
            "colorway_name": "Colorway 1",
            "stash_status": {"id": 1, "name": "Active"},
            "yarn": {
                "name": "Yarn A",
                "yarn_company_name": "Brand X",
            },
            "packs": [{"skeins": 2.0, "total_yards": 400.0, "total_grams": 100.0}]
        },
        {
            "id": 2,
            "name": "Yarn A",
            "colorway_name": "Colorway 2",
            "stash_status": {"id": 1, "name": "Active"},
            "yarn": {
                "name": "Yarn A",
                "yarn_company_name": "Brand X",
            },
            "packs": [{"skeins": 1.0, "total_yards": 200.0, "total_grams": 50.0}]
        }
    ]
    
    controller.MODEL.get_stash_list.return_value = mock_stash

    # Render stash cards list
    cols = controller.render_stash_cards(query=None)
    
    assert len(cols) == 1
    # Verify we got a Card (custom accordion container)
    card = cols[0].children
    assert isinstance(card, dbc.Card)
    
    header, collapse = card.children
    assert isinstance(header, html.Div)
    assert isinstance(collapse, dbc.Collapse)
    
    # Verify the collapsed body has the two colorway rows
    body = collapse.children
    assert isinstance(body, html.Div)
    # 2 colorway row elements
    assert len(body.children) == 2


def test_toggle_edit_modal_robust_matching():
    import datetime
    from dash import no_update
    
    # Setup controller with mocked model
    controller = AppController(header_id="h", search_id="s", result_id="r")
    controller.MODEL = MagicMock()
    controller.MODEL.get_stash_history.return_value = []

    # Test case 1: Cancel button triggered
    res = controller.toggle_edit_modal(
        edit_clicks=[],
        cancel_click=1,
        store_data_list=[],
        btn_ids=[],
        triggered_id="edit-stash-cancel-btn.n_clicks"
    )
    assert res[0] is False
    assert res[1] is no_update
    assert res[12] == datetime.date.today().isoformat()
    assert res[15] == ""

    # Test case 2: Valid edit button click and match found (with numeric/string matching)
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[
            {"id": 123, "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1, "type": "yarn"}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == {"id": 123, "name": "Soft Wool", "type": "yarn"}
    assert res[2] == 5.0
    assert res[3] == "Red"
    assert res[4] == "A"
    assert res[5] == "Box"
    assert res[6] == "notes"
    assert res[7] == 5.0
    assert res[8] == 1
    assert res[13] == "edit entry: Soft Wool"
    assert "Originally stashed" in res[15]

    # Test case 3: Match with mismatched types (index string vs integer ID)
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[
            {"id": "123", "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1, "type": "yarn"}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == {"id": "123", "name": "Soft Wool", "type": "yarn"}

    # Test case 4: Triggered ID doesn't parse
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[{"id": 123}],
        btn_ids=[{"index": 123}],
        triggered_id="invalid-json"
    )
    assert res == (no_update,) * 16


def test_search_yarn_sort_mapping_and_schema_validation():
    import os
    os.environ.setdefault("API_USERNAME", "test_user")
    os.environ.setdefault("API_KEY", "test_key")
    from stashies.model import Model
    from stashies.dataclasses import Yarn

    model = Model()
    model.REQ = MagicMock()

    mock_response = {
        "yarns": [
            {
                "id": 100,
                "name": "Super Bulky Wool",
                "discontinued": False,
                "grams": 100,
                "yardage": 80,
                "yarn_company_name": "Cave Company",
                "machine_washable": True,
                "colorways": [{"name": "Granite"}, {"name": "Granite"}, {"name": "Basalt"}],
                "photos": [{"medium_url": "https://example.com/photo.jpg"}]
            }
        ]
    }
    model.REQ.get_request.return_value = mock_response

    yarns = model.search_yarn(query="wool", sort="best_match")

    model.REQ.get_request.assert_called_once_with(
        endpoint="yarns/search.json",
        params={"query": "wool", "page": 1, "page_size": 10, "sort": "best"}
    )

    assert yarns is not None
    assert len(yarns) == 1
    yarn = yarns[0]
    assert isinstance(yarn, Yarn)
    assert yarn.id == 100
    assert yarn.name == "Super Bulky Wool"
    assert yarn.company == "Cave Company"
    assert yarn.colorways == ["Basalt", "Granite"]


def test_delete_components_in_modal_layout():
    from stashies.components.edit_modal import EditModal
    modal = EditModal(container_id="modal-test")
    layout = modal.create_init_layout()
    
    # Traverse layout children to find the delete components
    body_children = layout.children[1].children
    confirm_dialog = next((c for c in body_children if getattr(c, 'id', None) == "edit-stash-delete-confirm"), None)
    assert confirm_dialog is not None, "edit-stash-delete-confirm not found in ModalBody"
    assert confirm_dialog.message == "Are you sure you want to permanently delete this stash entry?"

    footer_children = layout.children[2].children
    delete_btn = next((c for c in footer_children if getattr(c, 'id', None) == "edit-stash-delete-btn"), None)
    assert delete_btn is not None, "edit-stash-delete-btn not found in ModalFooter"
    assert delete_btn.color == "danger"


def test_handle_delete_stash():
    controller = AppController(header_id="h", search_id="s", result_id="r")
    controller.MODEL = MagicMock()
    
    # Mock model's delete_stash return value
    controller.MODEL.delete_stash.return_value = True
    msg, is_open = controller.handle_delete_stash(123, "yarn")
    assert msg == "Entry deleted successfully."
    assert is_open is False
    controller.MODEL.delete_stash.assert_called_once_with(123, "yarn")

    # Mock delete failure
    controller.MODEL.delete_stash.reset_mock()
    controller.MODEL.delete_stash.return_value = False
    msg, is_open = controller.handle_delete_stash(123, "yarn")
    assert msg == "Failed to delete entry."
    assert is_open is True


def test_get_analytics_dataframe_with_history():
    from stashies.model import Model
    model = Model()
    
    stash_list = [
        {
            "id": 101,
            "created_at": "2026/05/01 12:00:00 -0400",
            "updated_at": "2026/05/10 12:00:00 -0400",
            "yarn": {
                "id": 123,
                "name": "Yarn A",
                "yarn_company_name": "Brand X",
                "yardage": 200,
                "grams": 100
            },
            "original_values": {
                "yards": 400.0,
                "meters": 365.76,
                "skeins": 2.0,
                "grams": 200.0
            },
            "history": [
                {
                    "date": "2026-05-05",
                    "yards": -100.0,
                    "meters": -91.44,
                    "skeins": -0.5,
                    "grams": -50.0
                }
            ],
            "packs": [{"skeins": 1.5}]
        }
    ]
    
    df = model.get_analytics_dataframe(stash_list, {})
    assert not df.empty
    
    import pandas as pd
    row1 = df[df["date"] == pd.to_datetime("2026-05-01")]
    assert len(row1) == 1
    assert row1["cumulative_skeins"].iloc[0] == 2.0
    
    row2 = df[df["date"] == pd.to_datetime("2026-05-05")]
    assert len(row2) == 1
    assert row2["cumulative_skeins"].iloc[0] == 1.5


def test_analytics_ols_trendline():
    import pandas as pd
    from stashies.components.analytics import AnalyticsComponent

    df = pd.DataFrame({
        "date": pd.date_range(start="2026-01-01", periods=10, freq="D"),
        "cumulative_yards": [10.0, 15.0, 18.0, 25.0, 30.0, 32.0, 40.0, 42.0, 48.0, 55.0]
    })

    analytics = AnalyticsComponent(container_id="test-container")
    metric_info = analytics.METRIC_MAP["yards"]

    # Build figure with show_trendline=True and show_prediction=True
    fig = analytics.build_figure(df, metric_info, show_trendline=True, show_prediction=True)
    
    # Assert trendline exists and is correct
    traces = [t for t in fig.data if t.name == "OLS Trendline"]
    assert len(traces) == 1
    trend_trace = traces[0]
    assert trend_trace.type == "scatter"
    
    # Verify calculated trendline endpoints
    y_vals = list(trend_trace.y)
    assert abs(y_vals[0] - 9.6) < 1e-5
    assert abs(y_vals[-1] - 53.4) < 1e-5

    # Assert prediction trace exists and is correct
    pred_traces = [t for t in fig.data if t.name == "90-Day Prediction"]
    assert len(pred_traces) == 1
    pred_trace = pred_traces[0]
    assert pred_trace.type == "scatter"
    
    # Endpoints: first point is at the last historical date, second point is 90 days in the future
    x_dates = list(pred_trace.x)
    assert len(x_dates) == 2
    assert x_dates[0] == df["date"].max()
    assert x_dates[1] == df["date"].max() + pd.Timedelta(days=90)
    
    y_pred_vals = list(pred_trace.y)
    # y at last point: 9.6 + 4.86666... * 9 = 53.4
    # y at 90 days later (x = 9 + 90 = 99): 9.6 + 4.86666... * 99 = 491.4
    assert abs(y_pred_vals[0] - 53.4) < 1e-5
    assert abs(y_pred_vals[1] - 491.4) < 1e-5







