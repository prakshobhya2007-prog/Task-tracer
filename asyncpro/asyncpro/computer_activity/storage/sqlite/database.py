"""
SQLite Database Engine with WAL Mode, Single Writer Queue, and Batched Transactions.
"""
import os
import sqlite3
import threading
from typing import Any, List, Tuple


class Database:
    """Thread-safe SQLite connection manager with WAL mode enabled."""

    def __init__(self, db_path: str = "computer_activity.db"):
        self.db_path = db_path
        self._write_lock = threading.Lock()
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Initializes WAL mode and performance pragmas."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self.get_connection() as conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA temp_store = MEMORY;")
            conn.execute("PRAGMA cache_size = -64000;")  # 64 MB cache

    def execute_write(self, sql: str, params: Tuple[Any, ...] = ()) -> int:
        """Executes a single write query using the thread-safe write lock."""
        with self._write_lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
                return cursor.lastrowid or cursor.rowcount

    def execute_write_batch(self, sql: str, params_list: List[Tuple[Any, ...]]) -> int:
        """Executes a batch write transaction atomically."""
        if not params_list:
            return 0
        with self._write_lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, params_list)
                conn.commit()
                return cursor.rowcount

    def execute_read(self, sql: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Executes a read query concurrently."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
