from datetime import datetime
import pytest
from pydantic import ValidationError
from stashies.dataclasses.stash_sync_state import StashSyncState

def test_stash_sync_state_defaults():
    state = StashSyncState(stash_id="12345")
    assert state.stash_id == "12345"
    assert state.is_dirty is False
    assert state.last_synced_at is None
    assert state.sync_error is None
    assert isinstance(state.updated_at, datetime)

def test_stash_sync_state_custom_values():
    now = datetime.now()
    state = StashSyncState(
        stash_id="67890",
        is_dirty=True,
        last_synced_at=now,
        sync_error="Network timeout"
    )
    assert state.stash_id == "67890"
    assert state.is_dirty is True
    assert state.last_synced_at == now
    assert state.sync_error == "Network timeout"

def test_stash_sync_state_validation_error():
    with pytest.raises(ValidationError):
        StashSyncState(stash_id=123, is_dirty="invalid_bool_value")
