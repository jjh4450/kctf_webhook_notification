import os
import sqlite3

from config import DB_PATH
from dto import Event


class SeenStore:
    """이미 보낸 대회의 fingerprint를 SQLite에 보관."""

    def __init__(self, path: str = DB_PATH):
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)   # /data 같은 볼륨 경로 대비
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS seen ("
            "  fingerprint TEXT PRIMARY KEY,"
            "  event_id    INTEGER,"
            "  title       TEXT,"
            "  sent_at     TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        self.conn.commit()

    def is_new(self, event: Event) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM seen WHERE fingerprint = ?", (event.fingerprint,)
        )
        return cur.fetchone() is None

    def mark_sent(self, events: list[Event]) -> None:
        self.conn.executemany(
            "INSERT OR IGNORE INTO seen (fingerprint, event_id, title) VALUES (?, ?, ?)",
            [(e.fingerprint, e.id, e.title) for e in events],
        )
        self.conn.commit()

    def __enter__(self) -> SeenStore:
        return self

    def __exit__(self, *exc) -> None:
        self.conn.close()