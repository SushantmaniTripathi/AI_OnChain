"""
utils/database.py — SQLite cache + report storage
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from config import DB_PATH, CACHE_TTL_MINUTES


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables on first run."""
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at  TEXT    NOT NULL,
            whale_data  TEXT,
            token_data  TEXT,
            gas_data    TEXT,
            summary     TEXT,
            risk_score  INTEGER
        );

        CREATE TABLE IF NOT EXISTS api_cache (
            cache_key   TEXT    PRIMARY KEY,
            data        TEXT    NOT NULL,
            cached_at   TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS whale_alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_hash     TEXT,
            wallet      TEXT,
            value_eth   REAL,
            value_usd   REAL,
            direction   TEXT,
            token       TEXT,
            detected_at TEXT
        );
    """)
    conn.commit()
    conn.close()


def cache_get(key: str):
    """Return cached value if still fresh, else None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT data, cached_at FROM api_cache WHERE cache_key = ?", (key,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    cached_at = datetime.fromisoformat(row["cached_at"])
    if datetime.utcnow() - cached_at > timedelta(minutes=CACHE_TTL_MINUTES):
        return None
    return json.loads(row["data"])


def cache_set(key: str, data):
    """Store value in cache."""
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO api_cache (cache_key, data, cached_at)
           VALUES (?, ?, ?)""",
        (key, json.dumps(data, default=str), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def save_report(whale_data, token_data, gas_data, summary, risk_score):
    """Persist a completed report."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO reports (created_at, whale_data, token_data, gas_data, summary, risk_score)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            datetime.utcnow().isoformat(),
            json.dumps(whale_data, default=str),
            json.dumps(token_data, default=str),
            json.dumps(gas_data, default=str),
            summary,
            risk_score,
        )
    )
    conn.commit()
    conn.close()


def get_recent_reports(limit=10):
    """Fetch last N reports."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    reports = []
    for row in rows:
        r = dict(row)
        for field in ["whale_data", "token_data", "gas_data"]:
            if r[field]:
                r[field] = json.loads(r[field])
        reports.append(r)
    return reports