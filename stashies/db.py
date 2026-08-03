import os
from stashies.base import Base
import psycopg2
import psycopg2.pool
from typing import Optional
from stashies.dataclasses.stash_sync_state import StashSyncState


class PostgresPool(Base):
    """
    Connection pool manager for PostgreSQL database.
    """

    def __new__(cls):
        # We use simple connection pool
        return psycopg2.pool.ThreadedConnectionPool(1, 20, os.getenv("DATABASE_URL"))



class DBManager(Base):
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
            try:
                cls._pool = PostgresPool()
                cls.LOGGER.info("Postgres database pool initialized.")
                cls.run_migrations()
            except Exception as e:
                # Fallback to local logger or direct print if cls.LOGGER initialization failed (unlikely)
                cls.LOGGER.error(f"Failed to initialize Postgres database: {e}")
                raise e
        return cls._pool

    @classmethod
    def run_migrations(cls):
        """
        Create target database tables and indexes if they do not exist.
        """
        cls.LOGGER.debug("Starting Postgres database migrations")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS original_values (
                    stash_id VARCHAR(50) PRIMARY KEY,
                    yards DOUBLE PRECISION NOT NULL,
                    meters DOUBLE PRECISION NOT NULL,
                    skeins DOUBLE PRECISION NOT NULL,
                    grams DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
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
                cur.execute("""
                CREATE TABLE IF NOT EXISTS stash_sync_state (
                    stash_id VARCHAR(50) PRIMARY KEY,
                    is_dirty BOOLEAN DEFAULT FALSE,
                    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sync_error TEXT DEFAULT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_stash_id ON stash_history(stash_id);
                """)
                conn.commit()
                cls.LOGGER.info("Postgres database migrations executed successfully.")
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Migration failed: {e}")
            raise e
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_original_values(cls, stash_id: str):
        """
        Get the original quantities of a stash entry.
        """
        cls.LOGGER.debug(f"Fetching original_values for stash_id={stash_id}")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = %s", 
                    (str(stash_id),)
                )
                row = cur.fetchone()
                if row:
                    val = {"yards": row[0], "meters": row[1], "skeins": row[2], "grams": row[3]}
                    cls.LOGGER.debug(f"Found original_values for stash_id={stash_id}: {val}")
                    return val
                cls.LOGGER.debug(f"No original_values found for stash_id={stash_id}")
                return None
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Error reading original_values for stash {stash_id}: {e}")
            return None
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_bulk_original_values(cls, stash_ids: list):
        """
        Retrieve original values in bulk for a collection of stash IDs.
        """
        if not stash_ids:
            return {}
        cls.LOGGER.debug(f"Bulk fetching original_values for {len(stash_ids)} stash IDs")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                placeholders = ",".join("%s" for _ in stash_ids)
                cur.execute(
                    f"SELECT stash_id, yards, meters, skeins, grams FROM original_values WHERE stash_id IN ({placeholders})", 
                    tuple(str(sid) for sid in stash_ids)
                )
                rows = cur.fetchall()
                results = {}
                for row in rows:
                    results[row[0]] = {"yards": row[1], "meters": row[2], "skeins": row[3], "grams": row[4]}
                cls.LOGGER.debug(f"Bulk fetched original_values: found {len(results)} matches")
                return results
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Error reading bulk original_values: {e}")
            return {}
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_original_values(cls, stash_id: str, yards: float, meters: float, skeins: float, grams: float):
        """
        Save original quantities for a stash entry, ignoring if already set.
        """
        cls.LOGGER.debug(f"Saving original_values for stash_id={stash_id} (yards={yards}, meters={meters}, skeins={skeins}, grams={grams})")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT INTO original_values (stash_id, yards, meters, skeins, grams)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (stash_id) DO NOTHING
                """, (str(stash_id), yards, meters, skeins, grams))
                conn.commit()
                cls.LOGGER.debug(f"original_values saved/checked for stash_id={stash_id}")
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            cls.LOGGER.error(f"Error saving original_values for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def delete_stash_data(cls, stash_id: str):
        """
        Delete all data related to a stash entry from original_values and stash_history.
        """
        cls.LOGGER.debug(f"Deleting DB stash data for stash_id={stash_id}")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM original_values WHERE stash_id = %s", (str(stash_id),))
                cur.execute("DELETE FROM stash_history WHERE stash_id = %s", (str(stash_id),))
                conn.commit()
                cls.LOGGER.info(f"Postgres database entries deleted for stash_id={stash_id}")
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            cls.LOGGER.error(f"Failed to delete stash data for stash_id={stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_history_event(cls, event_id: int):
        """
        Fetch a single stash history event by its auto-increment ID.
        """
        cls.LOGGER.debug(f"Fetching history event with id={event_id}")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT stash_id, event_date, yards, meters, skeins, grams FROM stash_history WHERE id = %s",
                    (event_id,)
                )
                row = cur.fetchone()
                if row:
                    return {
                        "id": event_id,
                        "stash_id": row[0],
                        "date": row[1],
                        "yards": row[2],
                        "meters": row[3],
                        "skeins": row[4],
                        "grams": row[5]
                    }
                return None
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Error fetching history event {event_id}: {e}")
            return None
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def delete_history_event(cls, event_id: int):
        """
        Delete a single history event by its auto-increment ID.
        """
        cls.LOGGER.info(f"Deleting history event with id={event_id}")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM stash_history WHERE id = %s", (event_id,))
                conn.commit()
                return True
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            cls.LOGGER.error(f"Error deleting history event {event_id}: {e}")
            return False
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_stash_history(cls, stash_id: str):
        """
        Retrieve chronological history events recorded for a stash ID.
        """
        cls.LOGGER.debug(f"Fetching history events for stash_id={stash_id}")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT id, event_date, yards, meters, skeins, grams FROM stash_history WHERE stash_id = %s ORDER BY id ASC", 
                    (str(stash_id),)
                )
                rows = cur.fetchall()
                history = []
                for row in rows:
                    history.append({
                        "id": row[0],
                        "date": row[1],
                        "yards": row[2],
                        "meters": row[3],
                        "skeins": row[4],
                        "grams": row[5]
                    })
                cls.LOGGER.debug(f"Fetched {len(history)} history events for stash_id={stash_id}")
                return history
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Error reading stash_history for stash {stash_id}: {e}")
            return []
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_bulk_stash_history(cls, stash_ids: list):
        """
        Fetch chronological stash histories in bulk for a collection of stash IDs.
        """
        if not stash_ids:
            return {}
        cls.LOGGER.debug(f"Bulk fetching history for {len(stash_ids)} stash IDs")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                placeholders = ",".join("%s" for _ in stash_ids)
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
                cls.LOGGER.debug(f"Bulk fetched history events for {len(history)} stash IDs")
                return history
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Error reading bulk stash_history: {e}")
            return {}
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_history_event(cls, stash_id: str, event_date: str, yards: float, meters: float, skeins: float, grams: float):
        """
        Record a stash history event with specified date and quantities.
        """
        cls.LOGGER.debug(f"Saving history event for stash_id={stash_id} (date={event_date}, yards={yards}, meters={meters}, skeins={skeins}, grams={grams})")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT INTO stash_history (stash_id, event_date, yards, meters, skeins, grams)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (str(stash_id), event_date, yards, meters, skeins, grams))
                conn.commit()
                cls.LOGGER.debug(f"Stash history event saved for stash_id={stash_id}")
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            cls.LOGGER.error(f"Error saving stash_history event for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def set_pending_usage_date(cls, stash_id: str, usage_date: str):
        """
        Set a temporary usage date for a stash ID.
        """
        cls.LOGGER.debug(f"Setting pending usage date for stash_id={stash_id} to {usage_date}")
        cls._pending_dates[str(stash_id)] = usage_date

    @classmethod
    def pop_pending_usage_date(cls, stash_id: str) -> Optional[str]:
        """
        Retrieve and remove the pending usage date for a stash ID.
        """
        date = cls._pending_dates.pop(str(stash_id), None)
        cls.LOGGER.debug(f"Popped pending usage date for stash_id={stash_id}: {date}")
        return date

    @classmethod
    def mark_dirty(cls, stash_id: str):
        """Mark a stash entry as having unpushed local changes."""
        cls.LOGGER.debug(f"Marking stash_id={stash_id} as dirty")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT INTO stash_sync_state (stash_id, is_dirty, updated_at)
                VALUES (%s, TRUE, CURRENT_TIMESTAMP)
                ON CONFLICT (stash_id) DO UPDATE SET is_dirty = TRUE, updated_at = CURRENT_TIMESTAMP
                """, (str(stash_id),))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            cls.LOGGER.error(f"Failed to mark stash {stash_id} dirty: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_dirty_stash_ids(cls) -> list:
        """Retrieve list of stash IDs with pending local changes."""
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT stash_id FROM stash_sync_state WHERE is_dirty = TRUE")
                rows = cur.fetchall()
                return [str(r[0]) for r in rows]
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Failed to fetch dirty stash IDs: {e}")
            return []
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_sync_state(cls, stash_id: str) -> Optional[StashSyncState]:
        """Retrieve sync state record parsed via StashSyncState Pydantic model."""
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT stash_id, is_dirty, last_synced_at, sync_error, updated_at FROM stash_sync_state WHERE stash_id = %s",
                    (str(stash_id),)
                )
                row = cur.fetchone()
                if row:
                    return StashSyncState(
                        stash_id=row[0],
                        is_dirty=row[1],
                        last_synced_at=row[2],
                        sync_error=row[3],
                        updated_at=row[4]
                    )
                return None
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Error fetching sync state for stash {stash_id}: {e}")
            return None
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def mark_synced(cls, stash_id: str):
        """Mark a stash entry as successfully synced with Ravelry API."""
        cls.LOGGER.debug(f"Marking stash_id={stash_id} as synced")
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                UPDATE stash_sync_state 
                SET is_dirty = FALSE, last_synced_at = CURRENT_TIMESTAMP, sync_error = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE stash_id = %s
                """, (str(stash_id),))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            cls.LOGGER.error(f"Failed to mark stash {stash_id} synced: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_unsynced_count(cls) -> int:
        """Return total count of pending unsynced stash entries."""
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM stash_sync_state WHERE is_dirty = TRUE")
                row = cur.fetchone()
                return row[0] if row else 0
            finally:
                cur.close()
        except Exception as e:
            cls.LOGGER.error(f"Failed to fetch unsynced count: {e}")
            return 0
        finally:
              cls.get_pool().putconn(conn)
