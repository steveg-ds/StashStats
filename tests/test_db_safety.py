from unittest.mock import MagicMock, patch, call
import pytest
from datetime import datetime, timezone
from stashies.db import DBManager
from stashies.dataclasses.stash_sync_state import StashSyncState


@pytest.fixture(autouse=True)
def reset_pool():
    DBManager._pool = None
    yield
    DBManager._pool = None


def test_save_original_values_rollback_on_commit_error():
    """conn.rollback() called when commit raises in save_original_values."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit.side_effect = Exception("commit failed")
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, 'get_pool', return_value=mock_pool):
        DBManager.save_original_values('123', 100.0, 91.0, 2.0, 200.0)
        mock_conn.rollback.assert_called_once()


def test_delete_stash_data_rollback_on_commit_error():
    """conn.rollback() called when commit raises in delete_stash_data."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit.side_effect = Exception("commit failed")
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, 'get_pool', return_value=mock_pool):
        DBManager.delete_stash_data('123')
        mock_conn.rollback.assert_called_once()


def test_delete_history_event_rollback_on_commit_error():
    """conn.rollback() called when commit raises in delete_history_event."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit.side_effect = Exception("commit failed")
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, 'get_pool', return_value=mock_pool):
        result = DBManager.delete_history_event(1)
        mock_conn.rollback.assert_called_once()


def test_save_history_event_rollback_on_commit_error():
    """conn.rollback() called when commit raises in save_history_event."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit.side_effect = Exception("commit failed")
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, 'get_pool', return_value=mock_pool):
        DBManager.save_history_event('123', '2026-01-01', 100.0, 91.0, 2.0, 200.0)
        mock_conn.rollback.assert_called_once()


def test_mark_dirty_rollback_on_commit_error():
    """conn.rollback() called when commit raises in mark_dirty."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit.side_effect = Exception("commit failed")
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, 'get_pool', return_value=mock_pool):
        DBManager.mark_dirty('123')
        mock_conn.rollback.assert_called_once()


def test_mark_synced_rollback_on_commit_error():
    """conn.rollback() called when commit raises in mark_synced."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_conn.commit.side_effect = Exception("commit failed")
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, 'get_pool', return_value=mock_pool):
        DBManager.mark_synced('123')
        mock_conn.rollback.assert_called_once()


def test_create_temperature_project_rollback_on_commit_error():
    """conn.rollback() called when commit raises in create_temperature_project."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = (1,)
    mock_conn.commit.side_effect = Exception("commit failed")
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, 'get_pool', return_value=mock_pool):
        result = DBManager.create_temperature_project(
            name='Test', location='NYC', lat=40.7, lon=-74.0,
            start_date='2026-01-01', end_date='2026-12-31'
        )
        mock_conn.rollback.assert_called_once()


def test_stash_sync_state_updated_at_is_timezone_aware():
    """StashSyncState.updated_at default is timezone-aware (UTC)."""
    state = StashSyncState(stash_id='test_123')
    assert state.updated_at.tzinfo is not None, "updated_at must be timezone-aware"
    assert state.updated_at.tzinfo == timezone.utc or state.updated_at.utcoffset() is not None
