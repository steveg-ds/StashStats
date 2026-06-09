import os
import logging
import sqlite3
from typing import Optional

logger = logging.getLogger("stashies.db")

class SQLitePool:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure parent directory exists
        db_dir = os.getenv("SQLITE_DB_PATH", "/app/data/stash.db")
        parent_dir = os.path.dirname(db_dir)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

    def getconn(self) -> sqlite3.Connection:
        # Establish connection with thread-safety flag
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Enable WAL mode for high concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def putconn(self, conn: sqlite3.Connection) -> None:
        # Close connection to release resource handles
        conn.close()

class DBManager:
    _pool = None
    _pending_dates = {}

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            db_path = os.getenv("SQLITE_DB_PATH", "/app/data/stash.db")
            try:
                cls._pool = SQLitePool(db_path)
                logger.info(f"SQLite database pool initialized at {db_path}.")
                cls.run_migrations()
            except Exception as e:
                logger.error(f"Failed to initialize SQLite database: {e}")
                raise e
        return cls._pool

    @classmethod
    def run_migrations(cls):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS original_values (
                    stash_id TEXT PRIMARY KEY,
                    yards REAL NOT NULL,
                    meters REAL NOT NULL,
                    skeins REAL NOT NULL,
                    grams REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
                CREATE TABLE IF NOT EXISTS stash_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stash_id TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    yards REAL NOT NULL,
                    meters REAL NOT NULL,
                    skeins REAL NOT NULL,
                    grams REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_stash_id ON stash_history(stash_id);
                """)
                conn.commit()
                logger.info("SQLite database migrations executed successfully.")
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise e
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_original_values(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = ?", 
                    (str(stash_id),)
                )
                row = cur.fetchone()
                if row:
                    return {"yards": row[0], "meters": row[1], "skeins": row[2], "grams": row[3]}
                return None
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error reading original_values for stash {stash_id}: {e}")
            return None
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_original_values(cls, stash_id: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT INTO original_values (stash_id, yards, meters, skeins, grams)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (stash_id) DO NOTHING
                """, (str(stash_id), yards, meters, skeins, grams))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error saving original_values for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_stash_history(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT event_date, yards, meters, skeins, grams FROM stash_history WHERE stash_id = ? ORDER BY id ASC", 
                    (str(stash_id),)
                )
                rows = cur.fetchall()
                history = []
                for row in rows:
                    history.append({
                        "date": row[0],
                        "yards": row[1],
                        "meters": row[2],
                        "skeins": row[3],
                        "grams": row[4]
                    })
                return history
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error reading stash_history for stash {stash_id}: {e}")
            return []
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_history_event(cls, stash_id: str, event_date: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT INTO stash_history (stash_id, event_date, yards, meters, skeins, grams)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (str(stash_id), event_date, yards, meters, skeins, grams))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error saving stash_history event for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def set_pending_usage_date(cls, stash_id: str, usage_date: str):
        cls._pending_dates[str(stash_id)] = usage_date

    @classmethod
    def pop_pending_usage_date(cls, stash_id: str) -> Optional[str]:
        return cls._pending_dates.pop(str(stash_id), None)
