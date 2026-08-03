"""
Unit tests exposing root causes for StashStats R2, R3, R4, R5 bug fixes.
These tests verify behavior of Model.update_stash, AppController.handle_save_edit,
and StashPost dataclass.
"""
from unittest.mock import MagicMock, patch
import pytest

from stashies.model import Model
from stashies.app_controller import AppController
from stashies.dataclasses.stash_post import StashPost
from stashies.db import DBManager


def test_r2_update_stash_http_method_is_put():
    """
    R2 Root Cause: Model.update_stash called REQ.post_request instead of REQ.put_request.
    Ravelry API PUT endpoint requires put_request.
    """
    model = Model()
    model.REQ = MagicMock()
    model.REQ.post_request.return_value = {"stash": {"id": 12345}}
    model.REQ.put_request.return_value = {"stash": {"id": 12345}}

    res = model.update_stash(12345, {"yarn_id": 100, "notes": "test note"})

    # Must call put_request, not post_request
    model.REQ.put_request.assert_called_once()
    assert model.REQ.post_request.call_count == 0


def test_r3_handle_save_edit_ungated_db_writes():
    """
    R3 Root Cause: AppController.handle_save_edit gated local DB writes (mark_dirty, save_history_event)
    inside `if result and 'stash' in result:`. When Ravelry API call returns None (offline/error),
    local DB updates were skipped. Local DB writes must be ungated.
    """
    controller = AppController("hdr", "src", "res")
    controller.MODEL = MagicMock()
    controller.MODEL.update_stash.return_value = None  # Simulate API offline or failure

    with patch("stashies.db.DBManager") as mock_db:
        mock_db.get_original_values.return_value = {"skeins": 2.0, "yards": 100.0, "grams": 50.0}
        res_msg, is_open = controller.handle_save_edit(
            stash_id="101",
            active_tab="modal-tab-details",
            colorway="Blueberry",
            dyelot="A1",
            location="Bin 1",
            notes="Soft yarn",
            skeins=2.0,
            status_id=1,
            used_skeins=None,
            current_skeins=None,
        )

        # Local DB write mark_dirty should be called even when update_stash returns None
        mock_db.mark_dirty.assert_called_once_with("101")


def test_r4_stash_post_payload_colorway_fields():
    """
    R4 Root Cause: StashPost dataclass lacked top-level `colorway` field support,
    causing `colorway` / `colorway_name` to be dropped or missing from top-level model_dump().
    """
    payload_data = {
        "colorway": "Blueberry",
        "colorway_name": "Blueberry",
        "dye_lot": "Lot 1",
        "location": "Shelf A",
    }
    stash_post = StashPost(**payload_data)
    dumped = stash_post.model_dump(exclude_none=True)

    # Top-level colorway and colorway_name must both be preserved in serialized payload
    assert "colorway" in dumped and dumped["colorway"] == "Blueberry"
    assert "colorway_name" in dumped and dumped["colorway_name"] == "Blueberry"


def test_r4_stash_post_single_colorway_field():
    """Verify colorway field is preserved when colorway_name is omitted."""
    stash_post = StashPost(colorway="Raspberry")
    dumped = stash_post.model_dump(exclude_none=True)
    assert dumped == {"colorway": "Raspberry"}



def test_r5_handle_save_edit_ui_modal_closes_or_triggers_refresh():
    """
    R5 Root Cause: AppController.handle_save_edit returned `is_open=True` on API failure/offline response,
    which prevented the Dash UI callback (`save_stash_edit`) from incrementing `stash-update-trigger`.
    handle_save_edit must return `is_open=False` so that modal closes and Dash UI trigger updates.
    """
    controller = AppController("hdr", "src", "res")
    controller.MODEL = MagicMock()
    controller.MODEL.update_stash.return_value = None  # Simulate API failure / offline mode

    with patch("stashies.db.DBManager") as mock_db:
        mock_db.get_original_values.return_value = {"skeins": 1.0, "yards": 50.0, "grams": 25.0}
        res_msg, is_open = controller.handle_save_edit(
            stash_id="101",
            active_tab="modal-tab-details",
            colorway="Red",
            dyelot=None,
            location=None,
            notes=None,
            skeins=1.0,
            status_id=1,
            used_skeins=None,
            current_skeins=None,
        )

        # is_open must be False so that Dash UI closes modal and increments stash-update-trigger
        assert is_open is False


def test_r3_r5_usage_tab_ungated_writes_and_modal_close():
    """
    Verify usage tab ungates save_history_event and mark_dirty and returns is_open=False even when API returns None.
    """
    controller = AppController("hdr", "src", "res")
    controller.MODEL = MagicMock()
    controller.MODEL.update_stash.return_value = None  # Simulate API offline or failure

    with patch("stashies.db.DBManager") as mock_db:
        mock_db.get_original_values.return_value = {"skeins": 5.0, "yards": 500.0, "meters": 450.0, "grams": 250.0}
        res_msg, is_open = controller.handle_save_edit(
            stash_id="202",
            active_tab="modal-tab-usage",
            colorway=None,
            dyelot=None,
            location=None,
            notes=None,
            skeins=None,
            status_id=None,
            used_skeins=1.0,
            current_skeins=5.0,
            usage_date="2026-08-02",
        )

        mock_db.save_history_event.assert_called_once()
        mock_db.mark_dirty.assert_called_once_with("202")
        assert is_open is False

