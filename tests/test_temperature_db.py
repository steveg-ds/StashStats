from unittest.mock import MagicMock, patch
import pytest

from stashies.db import DBManager

@pytest.fixture
def mock_db_pool():
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn
    with patch.object(DBManager, "get_pool", return_value=mock_pool):
        yield mock_pool, mock_conn, mock_cur

def test_run_migrations_includes_temperature_tables(mock_db_pool):
    mock_pool, mock_conn, mock_cur = mock_db_pool
    DBManager.run_migrations()
    executed_sqls = [call_args[0][0] for call_args in mock_cur.execute.call_args_list]
    assert any("temperature_projects" in sql for sql in executed_sqls)
    assert any("temperature_palette_mapping" in sql for sql in executed_sqls)
    assert any("temperature_daily_logs" in sql for sql in executed_sqls)

def test_save_and_get_temperature_project(mock_db_pool):
    mock_pool, mock_conn, mock_cur = mock_db_pool
    mock_cur.fetchone.return_value = (1,)
    
    project_id = DBManager.create_temperature_project(
        name="2026 NYC Blanket",
        location="New York, NY",
        lat=40.71,
        lon=-74.00,
        start_date="2026-01-01",
        end_date="2026-12-31",
        temp_metric="mean",
        units="F",
        ravelry_project_id="998877"
    )
    assert project_id == 1
    assert mock_cur.execute.called
