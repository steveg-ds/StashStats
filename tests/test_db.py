from unittest.mock import MagicMock, patch
import pytest

from stashies.db import DBManager


@pytest.fixture(autouse=True)
def reset_db_manager_pool():
    """Ensure DBManager._pool is reset before and after each test."""
    DBManager._pool = None
    yield
    DBManager._pool = None


def test_get_pool():
    """
    Test DBManager.get_pool initializes and returns psycopg2.pool.SimpleConnectionPool.
    Fails in RED phase against current SQLite implementation.
    """
    mock_pool_inst = MagicMock()
    with patch("psycopg2.pool.SimpleConnectionPool", create=True, return_value=mock_pool_inst) as mock_pool_cls:
        pool = DBManager.get_pool()
        mock_pool_cls.assert_called_once()
        assert pool is mock_pool_inst
        assert DBManager._pool is mock_pool_inst


def test_run_migrations():
    """
    Test DBManager.run_migrations executes Postgres schema creation DDL
    using connection from psycopg2 connection pool.
    Fails in RED phase against current SQLite implementation.
    """
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur

    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn

    with patch.object(DBManager, "get_pool", return_value=mock_pool):
        DBManager.run_migrations()

        mock_pool.getconn.assert_called_once()
        mock_conn.cursor.assert_called_once()

        assert mock_cur.execute.called
        executed_sqls = [call_args[0][0] for call_args in mock_cur.execute.call_args_list]

        assert any("original_values" in sql for sql in executed_sqls)
        assert any("stash_history" in sql for sql in executed_sqls)

        full_sql = " ".join(executed_sqls)
        assert "AUTOINCREMENT" not in full_sql, "DDL contains SQLite AUTOINCREMENT"
        assert "SERIAL" in full_sql or "BIGSERIAL" in full_sql, "DDL missing Postgres SERIAL syntax"

        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_conn)


def test_get_original_values():
    """
    Test DBManager.get_original_values queries database using %s parameter placeholder (psycopg2).
    Fails in RED phase against current SQLite implementation (uses ? placeholder).
    """
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = (100.0, 91.44, 2.0, 100.0)

    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn

    with patch.object(DBManager, "get_pool", return_value=mock_pool):
        res = DBManager.get_original_values("stash_123")

        mock_cur.execute.assert_called_once_with(
            "SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = %s",
            ("stash_123",)
        )
        assert res == {"yards": 100.0, "meters": 91.44, "skeins": 2.0, "grams": 100.0}
        mock_cur.close.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_conn)
