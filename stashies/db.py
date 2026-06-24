import os
from stashies.utils.logger_func import create_logger
import sqlite3
from typing import Optional

logger = create_logger("DBManager")

class SQLitePool:
    """
    Connection pool manager for SQLite database.
    """

    db_path: str
    '''Path to the database file.'''

    def __init__(self, db_path: str):
        """
        Initialize the SQLitePool.
        """
        db_path: str
        '''Path to the database file.'''

        self.db_path = db_path
        # Ensure parent directory exists
        db_dir = os.getenv("SQLITE_DB_PATH", "/app/data/stash.db")
        parent_dir = os.path.dirname(db_dir)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

    def getconn(self) -> sqlite3.Connection:
        """
        Establish and return a new SQLite database connection.
        """
        # Connection pooling approach: creates connections on-demand using sqlite3.connect.
        # Since SQLite is a serverless, single-file database, this approach achieves
        # connection pooling by opening and closing connections dynamically, while
        # utilizing OS-level file caching.
        #
        # Thread-safety: check_same_thread=False allows sharing the connection handle
        # across multiple threads, allowing concurrent read/write operations without
        # raising thread-bound exceptions.
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Concurrency: Enable Write-Ahead Logging (WAL) journal mode.
        # This allows concurrent readers and a writer to access the database without blocking,
        # dramatically increasing throughput and preventing lock contention in multi-threaded environments.
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def putconn(self, conn: sqlite3.Connection) -> None:
        """
        Close a connection and release its resource handles.
        """
        conn: sqlite3.Connection
        '''Database connection to release.'''

        # Close connection to release resource handles
        conn.close()

class DBManager:
    """
    Database manager coordinating schema migrations, tracking original stash values,
    and recording stash usage history events.
    """

    _pool = None
    '''SQLite Pool instance.'''

    _pending_dates = {}
    '''
    Pending usage dates map for stash edits.
    This acts as a temporary dictionary to hold usage dates passed from the UI callback
    before the detail view refresh, bridging the state gap during the multi-step transaction.
    '''

    @classmethod
    def get_pool(cls):
        """
        Get or initialize the database connection pool.
        """
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
        """
        Create target database tables and indexes if they do not exist.
        """
        # Schema Initialization:
        # 1. original_values table: tracks initial quantities of stash entries when they
        #    are first entered (serves as the baseline for delta calculations).
        # 2. stash_history table: records chronological timeline events of stash usage,
        #    storing physical quantities (yards, meters, skeins, grams) at specific event dates.
        # 3. idx_history_stash_id index: optimizes queries looking up chronological
        #    history records filtered by a specific stash_id.
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
        """
        Get the original quantities of a stash entry.
        """
        stash_id: str
        '''Stash entry ID.'''

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
    def get_bulk_original_values(cls, stash_ids: list):
        """
        Retrieve original values in bulk for a collection of stash IDs.
        """
        stash_ids: list
        '''List of stash IDs to fetch.'''

        if not stash_ids:
            return {}
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                placeholders = ",".join("?" for _ in stash_ids)
                cur.execute(
                    f"SELECT stash_id, yards, meters, skeins, grams FROM original_values WHERE stash_id IN ({placeholders})", 
                    tuple(str(sid) for sid in stash_ids)
                )
                rows = cur.fetchall()
                results = {}
                for row in rows:
                    results[row[0]] = {"yards": row[1], "meters": row[2], "skeins": row[3], "grams": row[4]}
                return results
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error reading bulk original_values: {e}")
            return {}
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_original_values(cls, stash_id: str, yards: float, meters: float, skeins: float, grams: float):
        """
        Save original quantities for a stash entry, ignoring if already set.
        """
        stash_id: str
        '''Stash entry ID.'''
        yards: float
        '''Original yards of yarn.'''
        meters: float
        '''Original meters of yarn.'''
        skeins: float
        '''Original number of skeins.'''
        grams: float
        '''Original grams weight.'''

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
        """
        Retrieve chronological history events recorded for a stash ID.
        """
        stash_id: str
        '''Stash entry ID.'''

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
    def get_bulk_stash_history(cls, stash_ids: list):
        """
        Fetch chronological stash histories in bulk for a collection of stash IDs.
        """
        stash_ids: list
        '''List of stash IDs to query.'''

        if not stash_ids:
            return {}
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                placeholders = ",".join("?" for _ in stash_ids)
                cur.execute(
                    f"SELECT stash_id, event_date, yards, meters, skeins, grams FROM stash_history WHERE stash_id IN ({placeholders}) ORDER BY stash_id, id ASC", 
                    tuple(str(sid) for sid in stash_ids)
                )
                rows = cur.fetchall()
                history = {str(sid): [] for sid in stash_ids}
                for row in rows:
                    sid = row[0]
                    if sid not in history:
                        history[sid] = []
                    history[sid].append({
                        "date": row[1],
                        "yards": row[2],
                        "meters": row[3],
                        "skeins": row[4],
                        "grams": row[5]
                    })
                return history
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error reading bulk stash_history: {e}")
            return {}
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_history_event(cls, stash_id: str, event_date: str, yards: float, meters: float, skeins: float, grams: float):
        """
        Record a stash history event with specified date and quantities.
        """
        stash_id: str
        '''Stash entry ID.'''
        event_date: str
        '''Usage event date.'''
        yards: float
        '''Yards of yarn at event.'''
        meters: float
        '''Meters of yarn at event.'''
        skeins: float
        '''Number of skeins at event.'''
        grams: float
        '''Grams weight at event.'''

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
        """
        Set a temporary usage date for a stash ID.
        """
        stash_id: str
        '''Stash entry ID.'''
        usage_date: str
        '''Pending usage date string.'''

        cls._pending_dates[str(stash_id)] = usage_date

    @classmethod
    def pop_pending_usage_date(cls, stash_id: str) -> Optional[str]:
        """
        Retrieve and remove the pending usage date for a stash ID.
        """
        stash_id: str
        '''Stash entry ID.'''

        return cls._pending_dates.pop(str(stash_id), None)
