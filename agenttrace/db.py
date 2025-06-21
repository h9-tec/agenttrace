import datetime as _dt
import os
import sqlite3
from pathlib import Path
from typing import Optional

_DEFAULT_PATH = Path.home() / ".agenttrace" / "logs.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    func_name TEXT,
    start_ts TEXT,
    end_ts TEXT,
    git_sha TEXT
);

CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    ts TEXT,
    kind TEXT,
    payload TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
"""


def _connect(db_path: Path = _DEFAULT_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    return conn


def init_db(db_path: Path = _DEFAULT_PATH):
    conn = _connect(db_path)
    conn.executescript(_SCHEMA)
    conn.commit()
    conn.close()


class RunRecorder:
    """Context manager to record a run and its steps."""

    def __init__(self, func_name: str, git_sha: Optional[str] = None, db_path: Path = _DEFAULT_PATH):
        self.func_name = func_name
        self.git_sha = git_sha or "unknown"
        self.db_path = db_path
        init_db(self.db_path)
        self.conn = _connect(self.db_path)
        self.run_id: Optional[int] = None

    def __enter__(self):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO runs (func_name, start_ts, git_sha) VALUES (?, ?, ?)",
            (self.func_name, _dt.datetime.utcnow().isoformat(), self.git_sha),
        )
        self.run_id = cur.lastrowid
        self.conn.commit()
        return self

    def log_step(self, kind: str, payload: str):
        assert self.run_id is not None
        self.conn.execute(
            "INSERT INTO steps (run_id, ts, kind, payload) VALUES (?, ?, ?, ?)",
            (self.run_id, _dt.datetime.utcnow().isoformat(), kind, payload),
        )
        self.conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.execute(
            "UPDATE runs SET end_ts=? WHERE id=?",
            (_dt.datetime.utcnow().isoformat(), self.run_id),
        )
        self.conn.commit()
        self.conn.close() 