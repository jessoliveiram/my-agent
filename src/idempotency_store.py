"""Small SQLite-backed store for mutation idempotency."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class IdempotencyStore:
    """Persist completed mutation results by idempotency key."""

    def __init__(self, database_path: str):
        self.database_path = database_path
        self._initialize()

    def get(self, key: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT result FROM idempotency WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def put(self, key: str, result: dict[str, Any]) -> None:
        payload = json.dumps(result, sort_keys=True)
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO idempotency(key, result) VALUES (?, ?)",
                (key, payload),
            )

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS idempotency ("
                "key TEXT PRIMARY KEY, result TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        path = Path(self.database_path)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(path)
