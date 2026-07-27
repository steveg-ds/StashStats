import argparse
import sqlite3
import psycopg2


def migrate_sqlite_to_postgres(sqlite_db_path: str, postgres_url: str) -> None:
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cur = sqlite_conn.cursor()

    pg_conn = psycopg2.connect(postgres_url)
    pg_cur = pg_conn.cursor()

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
