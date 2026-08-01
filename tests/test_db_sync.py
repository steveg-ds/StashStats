from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

from stashies.db import DBManager
from stashies.dataclasses.stash_sync_state import StashSyncState

@pytest.fixture
def mock_db_pool():
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, "get_pool", return_value=mock_pool):
        yield mock_pool, mock_conn, mock_cur

def test_run_migrations_includes_stash_sync_state(mock_db_pool):
    mock_pool, mock_conn, mock_cur = mock_db_pool
    DBManager.run_migrations()
    executed_sqls = [call_args[0][0] for call_args in mock_cur.execute.call_args_list]
    assert any("stash_sync_state" in sql for sql in executed_sqls)

def test_db_sync_state_lifecycle_methods(mock_db_pool):
    mock_pool, mock_conn, mock_cur = mock_db_pool
    
    # 1. Test mark_dirty
    DBManager.mark_dirty("stash_101")
    assert mock_cur.execute.called
    sql = mock_cur.execute.call_args[0][0]
    assert "INSERT INTO stash_sync_state" in sql
    assert "is_dirty = TRUE" in sql

    # 2. Test get_dirty_stash_ids
    mock_cur.fetchall.return_value = [("stash_101",), ("stash_102",)]
    dirty_ids = DBManager.get_dirty_stash_ids()
    assert dirty_ids == ["stash_101", "stash_102"]

    # 3. Test get_unsynced_count
    mock_cur.fetchone.return_value = (2,)
    count = DBManager.get_unsynced_count()
    assert count == 2

    # 4. Test get_sync_state returning Pydantic model
    now = datetime.now()
    mock_cur.fetchone.return_value = ("stash_101", True, now, None, now)
    state = DBManager.get_sync_state("stash_101")
    assert isinstance(state, StashSyncState)
    assert state.stash_id == "stash_101"
    assert state.is_dirty is True

    # 5. Test mark_synced
    DBManager.mark_synced("stash_101")
    assert mock_cur.execute.called
    sql = mock_cur.execute.call_args[0][0]
    assert "UPDATE stash_sync_state" in sql
    assert "is_dirty = FALSE" in sql
