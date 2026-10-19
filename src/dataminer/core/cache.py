"""Cache response LLM trong SQLite: cùng request → không trả tiền hai lần.

Mỗi lần ghi được commit ngay, nên tiến trình bị ngắt giữa chừng vẫn giữ phần đã xong.
"""

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS responses (
    key           TEXT PRIMARY KEY,
    model         TEXT NOT NULL,
    created_at    REAL NOT NULL,
    request_json  TEXT NOT NULL,
    response_json TEXT NOT NULL
)
"""


class LLMCache:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def get(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT response_json FROM responses WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return None
        data: dict[str, Any] = json.loads(row[0])
        return data

    def put(self, key: str, model: str, request: dict[str, Any], response: dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO responses VALUES (?, ?, ?, ?, ?)",
                (
                    key,
                    model,
                    time.time(),
                    json.dumps(request, ensure_ascii=False),
                    json.dumps(response, ensure_ascii=False),
                ),
            )
            self._conn.commit()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            count, models = self._conn.execute(
                "SELECT COUNT(*), COUNT(DISTINCT model) FROM responses"
            ).fetchone()
        size = self.path.stat().st_size if self.path.exists() else 0
        return {"entries": count, "models": models, "size_kb": round(size / 1024, 1)}

    def close(self) -> None:
        with self._lock:
            self._conn.close()
