"""SQLite connection management and transaction helper.

Design notes:
- Uses isolation_level=None (manual transaction control) so that the
  transaction() context manager has full BEGIN/COMMIT/ROLLBACK control.
- WAL mode: better read concurrency, safe crash recovery.
- Foreign keys: enforced via PRAGMA on every new connection.
- schema.sql is read from the same directory as this file and executed
  on __init__ (idempotent via IF NOT EXISTS).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


class Database:
    """Manages a single SQLite connection with explicit transaction support."""

    def __init__(self, db_path: str) -> None:
        # isolation_level=None → autocommit disabled, we manage transactions
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._apply_pragmas()
        self._init_schema()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_connection(self) -> sqlite3.Connection:
        return self._conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for an explicit ACID transaction.

        Yields the connection so callers can execute statements.
        Commits on clean exit, rolls back on any exception.
        """
        conn = self._conn
        conn.execute("BEGIN")
        try:
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_pragmas(self) -> None:
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

    def _init_schema(self) -> None:
        schema_path = Path(__file__).parent / "schema.sql"
        sql = schema_path.read_text(encoding="utf-8")
        self._conn.executescript(sql)
