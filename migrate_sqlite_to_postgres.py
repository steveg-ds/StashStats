import argparse
import os
import sqlite3
import psycopg2


def migrate_sqlite_to_postgres(sqlite_db_path: str, postgres_url: str) -> None:
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cur = sqlite_conn.cursor()

    pg_conn = psycopg2.connect(postgres_url)
    pg_cur = pg_conn.cursor()

    # Ensure target tables exist
    pg_cur.execute("""
    CREATE TABLE IF NOT EXISTS original_values (
        stash_id VARCHAR(50) PRIMARY KEY,
        yards DOUBLE PRECISION NOT NULL,
        meters DOUBLE PRECISION NOT NULL,
        skeins DOUBLE PRECISION NOT NULL,
        grams DOUBLE PRECISION NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    pg_cur.execute("""
    CREATE TABLE IF NOT EXISTS stash_history (
        id SERIAL PRIMARY KEY,
        stash_id VARCHAR(50) NOT NULL,
        event_date VARCHAR(255) NOT NULL,
        yards DOUBLE PRECISION NOT NULL,
        meters DOUBLE PRECISION NOT NULL,
        skeins DOUBLE PRECISION NOT NULL,
        grams DOUBLE PRECISION NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    pg_cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_history_stash_id ON stash_history(stash_id);
    """)
    pg_conn.commit()

    sqlite_cur.execute(
        "SELECT stash_id, yards, meters, skeins, grams, created_at FROM original_values"
    )
    rows_orig = sqlite_cur.fetchall()
    for row in rows_orig:
        pg_cur.execute(
            """
            INSERT INTO original_values (stash_id, yards, meters, skeins, grams, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (stash_id) DO NOTHING
            """,
            row,
        )

    sqlite_cur.execute(
        "SELECT id, stash_id, event_date, yards, meters, skeins, grams, created_at FROM stash_history"
    )
    rows_hist = sqlite_cur.fetchall()
    for row in rows_hist:
        pg_cur.execute(
            """
            INSERT INTO stash_history (id, stash_id, event_date, yards, meters, skeins, grams, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            row,
        )

    pg_conn.commit()

    sqlite_cur.close()
    sqlite_conn.close()
    pg_cur.close()
    pg_conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate SQLite to PostgreSQL")
    parser.add_argument("--sqlite-path", required=True, help="Path to SQLite DB file")
    parser.add_argument("--postgres-url", required=True, help="PostgreSQL connection URL")
    args = parser.parse_args()

    migrate_sqlite_to_postgres(args.sqlite_path, args.postgres_url)


if __name__ == "__main__":
    main()
