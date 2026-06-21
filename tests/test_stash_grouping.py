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
            {"id": 123, "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == {"id": 123, "name": "Soft Wool"}
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
            {"id": "123", "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == {"id": "123", "name": "Soft Wool"}

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



