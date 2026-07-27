"""CLI wrapper for SQLite to PostgreSQL migration tool."""
from stashies.utils.migration import migrate_sqlite_to_postgres, main

if __name__ == "__main__":
    main()
