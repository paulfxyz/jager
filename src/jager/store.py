"""SQLite storage: Jager's memory (and his conscience).

One small file, no server, no ORM. Python's standard ``sqlite3`` is plenty.

Why SQLite?  Because "docker compose up" should not need a database admin, and
because a single-owner buddy writes a few rows per day. WAL mode makes it
crash-safe and lets readers and the writer coexist.

Things worth knowing
--------------------
* **Every SQL statement is parameterised.** No string-built SQL anywhere, so no
  injection, even if a comment contains ``'; DROP TABLE posts; --`` (people try).
* **The action log is append-only, enforced by the database.** Triggers abort any
  UPDATE or DELETE on it. If Jager ever misbehaves, the log is the truth, and
  nobody (not even a bug) can quietly rewrite history.
* **Dedupe table** remembers webhook ids, because Zernio may deliver the same
  event more than once. Old ids are purged so the file does not grow forever.
* A single lock serialises writes from our threads. SQLite is happy that way and
  it is one less thing to debug at 2 AM.
"""

from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv        (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS seen      (id TEXT PRIMARY KEY, ts REAL NOT NULL);
CREATE TABLE IF NOT EXISTS protected (key TEXT PRIMARY KEY, ts REAL NOT NULL);
CREATE TABLE IF NOT EXISTS handled   (key TEXT PRIMARY KEY, ts REAL NOT NULL);
CREATE TABLE IF NOT EXISTS pending (
    id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, payload TEXT NOT NULL,
    summary TEXT NOT NULL, created REAL NOT NULL, expires REAL NOT NULL, status TEXT NOT NULL DEFAULT 'open');
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT, starts REAL NOT NULL, ends REAL NOT NULL,
    delay_s INTEGER NOT NULL, platforms TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS spend (day TEXT PRIMARY KEY, usd REAL NOT NULL);
CREATE TABLE IF NOT EXISTS log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, kind TEXT NOT NULL,
    status TEXT NOT NULL, detail TEXT NOT NULL);
-- The log is a diary written in permanent marker: no edits, no deletions.
CREATE TRIGGER IF NOT EXISTS log_no_update BEFORE UPDATE ON log
BEGIN SELECT RAISE(ABORT, 'the action log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS log_no_delete BEFORE DELETE ON log
BEGIN SELECT RAISE(ABORT, 'the action log is append-only'); END;
"""


class Store:
    def __init__(self, path: str = "data/jager.db"):
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.path = path
        self._lock = threading.RLock()
        # check_same_thread=False: we guard access with our own lock instead.
        self._db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")      # crash-safe, readers don't block the writer
        self._db.execute("PRAGMA synchronous=NORMAL")    # fast, still safe with WAL
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.executescript(SCHEMA)
        if path != ":memory:":
            with contextlib.suppress(OSError):
                os.chmod(path, 0o600)                    # only the owner reads the diary

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        """A transaction: all-or-nothing, so a crash cannot leave half-written state."""
        with self._lock:
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield self._db
                self._db.execute("COMMIT")
            except BaseException:
                self._db.execute("ROLLBACK")
                raise

    def close(self) -> None:
        with self._lock:
            self._db.close()

    # ------------------------------------------------------------------ kv
    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            row = self._db.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    def set(self, key: str, value: Any) -> None:
        with self._tx() as db:
            db.execute("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                       (key, json.dumps(value)))

    def delete(self, key: str) -> None:
        with self._tx() as db:
            db.execute("DELETE FROM kv WHERE key=?", (key,))

    # --------------------------------------------------------------- dedupe
    def first_time(self, event_id: str) -> bool:
        """True the first time we see ``event_id``, False for every duplicate delivery.

        Uses INSERT OR IGNORE so two simultaneous deliveries cannot both win.
        """
        with self._tx() as db:
            cur = db.execute("INSERT OR IGNORE INTO seen(id,ts) VALUES(?,?)", (event_id, time.time()))
            return cur.rowcount == 1

    def purge(self, older_than_s: float = 7 * 86400) -> None:
        cutoff = time.time() - older_than_s
        with self._tx() as db:
            db.execute("DELETE FROM seen WHERE ts<?", (cutoff,))
            db.execute("DELETE FROM handled WHERE ts<?", (time.time() - 90 * 86400,))

    # ------------------------------------------------------- protect / handled
    def protect(self, key: str) -> None:
        with self._tx() as db:
            db.execute("INSERT OR IGNORE INTO protected(key,ts) VALUES(?,?)", (key, time.time()))

    def is_protected(self, key: str) -> bool:
        with self._lock:
            return self._db.execute("SELECT 1 FROM protected WHERE key=?", (key,)).fetchone() is not None

    def mark_handled(self, key: str) -> None:
        with self._tx() as db:
            db.execute("INSERT OR IGNORE INTO handled(key,ts) VALUES(?,?)", (key, time.time()))

    def is_handled(self, key: str) -> bool:
        with self._lock:
            return self._db.execute("SELECT 1 FROM handled WHERE key=?", (key,)).fetchone() is not None

    # ------------------------------------------------------------- pending
    def open_pending(self, kind: str, payload: dict, summary: str, ttl_s: int) -> int:
        """Create the single open confirmation. Any older open one is cancelled first (one question at a time)."""
        now = time.time()
        with self._tx() as db:
            db.execute("UPDATE pending SET status='cancelled' WHERE status='open'")
            cur = db.execute("INSERT INTO pending(kind,payload,summary,created,expires) VALUES(?,?,?,?,?)",
                             (kind, json.dumps(payload), summary, now, now + ttl_s))
            return int(cur.lastrowid)

    def current_pending(self) -> dict | None:
        """The open, unexpired confirmation, if any. Expired ones are closed on the way."""
        now = time.time()
        with self._tx() as db:
            db.execute("UPDATE pending SET status='expired' WHERE status='open' AND expires<?", (now,))
            row = db.execute("SELECT * FROM pending WHERE status='open' ORDER BY id DESC LIMIT 1").fetchone()
        if not row:
            return None
        d = dict(row)
        d["payload"] = json.loads(d["payload"])
        return d

    def close_pending(self, pid: int, status: str) -> None:
        with self._tx() as db:
            db.execute("UPDATE pending SET status=? WHERE id=?", (status, pid))

    # --------------------------------------------------------------- rules
    def add_rule(self, starts: float, ends: float, delay_s: int, platforms: list[str]) -> int:
        with self._tx() as db:
            cur = db.execute("INSERT INTO rules(starts,ends,delay_s,platforms,created) VALUES(?,?,?,?,?)",
                             (starts, ends, delay_s, json.dumps(platforms), time.time()))
            return int(cur.lastrowid)

    def active_rules(self) -> list[dict]:
        """Rules whose window has not fully passed (plus the delay, so late deletes still happen)."""
        now = time.time()
        with self._lock:
            rows = self._db.execute("SELECT * FROM rules WHERE active=1 AND ends+delay_s+3600>?", (now,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["platforms"] = json.loads(d["platforms"])
            out.append(d)
        return out

    def stop_rules(self) -> int:
        with self._tx() as db:
            return db.execute("UPDATE rules SET active=0 WHERE active=1").rowcount

    # ---------------------------------------------------------------- spend
    def spent_today(self) -> float:
        day = datetime.now(UTC).strftime("%Y-%m-%d")
        with self._lock:
            row = self._db.execute("SELECT usd FROM spend WHERE day=?", (day,)).fetchone()
        return float(row["usd"]) if row else 0.0

    def add_spend(self, usd: float) -> None:
        day = datetime.now(UTC).strftime("%Y-%m-%d")
        with self._tx() as db:
            db.execute("INSERT INTO spend(day,usd) VALUES(?,?) ON CONFLICT(day) DO UPDATE SET usd=usd+excluded.usd", (day, usd))

    # ------------------------------------------------------------------ log
    def log(self, event: str, outcome: str, /, **detail: Any) -> None:
        """Append to the diary. Never log secrets or full message bodies; ids and short snippets only."""
        with self._tx() as db:
            db.execute("INSERT INTO log(ts,kind,status,detail) VALUES(?,?,?,?)",
                       (time.time(), event, outcome, json.dumps(detail, default=str)))

    def export_log(self) -> list[dict]:
        with self._lock:
            rows = self._db.execute("SELECT * FROM log ORDER BY id").fetchall()
        return [{"id": r["id"], "time": datetime.fromtimestamp(r["ts"], UTC).isoformat(),
                 "kind": r["kind"], "status": r["status"], "detail": json.loads(r["detail"])} for r in rows]
