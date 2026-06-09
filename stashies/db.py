import os
import logging
import psycopg2
from psycopg2 import pool

logger = logging.getLogger("stashies.db")

class DBManager:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                # Fallback to local postgres if DATABASE_URL is not set (e.g. during local tests)
                db_url = "postgresql://stashuser:stashpassword@localhost:5432/stashstats"
            try:
                cls._pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=db_url)
                logger.info("Database connection pool initialized.")
                cls.run_migrations()
            except Exception as e:
                logger.error(f"Failed to initialize database connection pool: {e}")
                raise e
        return cls._pool

    @classmethod
    def run_migrations(cls):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
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
                    event_date VARCHAR(20) NOT NULL,
                    yards DOUBLE PRECISION NOT NULL,
                    meters DOUBLE PRECISION NOT NULL,
                    skeins DOUBLE PRECISION NOT NULL,
                    grams DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_stash_id ON stash_history(stash_id);
                """)
                conn.commit()
                logger.info("Database migrations executed successfully.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Migration failed: {e}")
            raise e
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_original_values(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = %s", (stash_id,))
                row = cur.fetchone()
                if row:
                    return {"yards": row[0], "meters": row[1], "skeins": row[2], "grams": row[3]}
                return None
        except Exception as e:
            logger.error(f"Error reading original_values for stash {stash_id}: {e}")
            return None
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_original_values(cls, stash_id: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO original_values (stash_id, yards, meters, skeins, grams)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (stash_id) DO NOTHING
                """, (stash_id, yards, meters, skeins, grams))
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving original_values for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_stash_history(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT event_date, yards, meters, skeins, grams FROM stash_history WHERE stash_id = %s ORDER BY id ASC", (stash_id,))
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
        except Exception as e:
            logger.error(f"Error reading stash_history for stash {stash_id}: {e}")
            return []
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_history_event(cls, stash_id: str, event_date: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO stash_history (stash_id, event_date, yards, meters, skeins, grams)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (stash_id, event_date, yards, meters, skeins, grams))
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving stash_history event for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)
