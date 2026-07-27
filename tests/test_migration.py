import sqlite3
from unittest.mock import MagicMock, patch
import pytest

from migrate_sqlite_to_postgres import migrate_sqlite_to_postgres


@pytest.fixture
def temp_sqlite_db(tmp_path):
    """
    Create a temporary SQLite database file with actual tables and data matching DBManager:
    original_values and stash_history.
    """
    db_path = str(tmp_path / "test_stash.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE original_values (
            stash_id TEXT PRIMARY KEY,
            yards REAL NOT NULL,
            meters REAL NOT NULL,
            skeins REAL NOT NULL,
            grams REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE stash_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stash_id TEXT NOT NULL,
            event_date TEXT NOT NULL,
            yards REAL NOT NULL,
            meters REAL NOT NULL,
            skeins REAL NOT NULL,
            grams REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("INSERT INTO original_values (stash_id, yards, meters, skeins, grams) VALUES ('stash_101', 200.0, 182.88, 4.0, 200.0)")
    cur.execute("INSERT INTO stash_history (id, stash_id, event_date, yards, meters, skeins, grams) VALUES (1, 'stash_101', '2026-07-01', 50.0, 45.72, 1.0, 50.0)")

    conn.commit()
    conn.close()
    return db_path


def test_migrate_sqlite_to_postgres(temp_sqlite_db):
    """
    Test migrate_sqlite_to_postgres reads SQLite records from original_values and stash_history,
    and inserts them into PostgreSQL.
    Fails in RED phase because migrate_sqlite_to_postgres does not exist yet.
    """
    mock_pg_conn = MagicMock()
    mock_pg_cur = MagicMock()
    mock_pg_conn.cursor.return_value = mock_pg_cur

    postgres_url = "postgresql://postgres:postgres@localhost:5432/stashstats"

    with patch("psycopg2.connect", return_value=mock_pg_conn) as mock_connect:
        migrate_sqlite_to_postgres(temp_sqlite_db, postgres_url)

        mock_connect.assert_called_once_with(postgres_url)
        assert mock_pg_cur.execute.called or mock_pg_cur.executemany.called
        mock_pg_conn.commit.assert_called()

        executed_sqls = [
            call[0][0]
            for call in (mock_pg_cur.execute.call_args_list + mock_pg_cur.executemany.call_args_list)
        ]

        full_sql = " ".join(executed_sqls)
        assert "original_values" in full_sql
        assert "stash_history" in full_sql
