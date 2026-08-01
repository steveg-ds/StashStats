from unittest.mock import MagicMock, patch
import pytest

from stashies.app_controller import AppController

def test_execute_batch_sync():
    controller = AppController("h_id", "s_id", "r_id")
    controller.MODEL.get_dirty_stash_ids = MagicMock(return_value=["stash_101", "stash_102"])
    controller.MODEL.sync_stash_entry_to_ravelry = MagicMock(return_value=True)
    controller.MODEL.mark_synced = MagicMock()
    
    count = controller.execute_batch_sync()
    assert count == 2
    assert controller.MODEL.sync_stash_entry_to_ravelry.call_count == 2
    assert controller.MODEL.mark_synced.call_count == 2
    controller.MODEL.mark_synced.assert_any_call("stash_101")
    controller.MODEL.mark_synced.assert_any_call("stash_102")
