"""SQLite scan history, stored in the user's local application data directory."""

import os
import sqlite3
from pathlib import Path


def default_db_path() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif os.sys.platform == "darwin":
        root = Path.home() / "Library/Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return root / "GuihGuihCyber" / "history.sqlite3"


class HistoryStore:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        db = self._connect()
        try:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, started_at TEXT NOT NULL, root_path TEXT NOT NULL, files_scanned INTEGER NOT NULL, findings INTEGER NOT NULL, errors INTEGER NOT NULL, cancelled INTEGER NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS scan_files (id INTEGER PRIMARY KEY, scan_id INTEGER NOT NULL REFERENCES scans(id), path TEXT NOT NULL, sha256 TEXT, size INTEGER NOT NULL, status TEXT NOT NULL, findings_json TEXT NOT NULL, error TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS quarantine (id TEXT PRIMARY KEY, original_path TEXT NOT NULL, stored_path TEXT NOT NULL, sha256 TEXT NOT NULL, created_at TEXT NOT NULL, state TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS preferences (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS security_alerts (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, rule_id TEXT NOT NULL, event_count INTEGER NOT NULL, window_seconds REAL NOT NULL)")
            db.commit()
        finally:
            db.close()

    def save_scan(self, report: dict) -> int:
        import json
        db = self._connect()
        try:
            cursor = db.execute("INSERT INTO scans(started_at,root_path,files_scanned,findings,errors,cancelled) VALUES(?,?,?,?,?,?)", (report["started_at"], report["root_path"], report["files_scanned"], report["finding_count"], report["error_count"], int(report["cancelled"])))
            scan_id = cursor.lastrowid
            for item in report["files"]:
                db.execute("INSERT INTO scan_files(scan_id,path,sha256,size,status,findings_json,error) VALUES(?,?,?,?,?,?,?)", (scan_id, item["path"], item["sha256"], item["size"], item["status"], json.dumps(item["findings"], ensure_ascii=False), item["error"]))
            db.commit()
            return int(scan_id)
        finally:
            db.close()

    def recent_scans(self, limit: int = 20) -> list[dict]:
        db = self._connect()
        try:
            rows = db.execute("SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            db.close()

    def get_preference(self, key: str, default: str | None = None) -> str | None:
        db = self._connect()
        try:
            row = db.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default
        finally:
            db.close()

    def set_preference(self, key: str, value: str) -> None:
        db = self._connect()
        try:
            db.execute(
                "INSERT INTO preferences(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
            db.commit()
        finally:
            db.close()

    def save_security_alert(self, alert: dict) -> int:
        db = self._connect()
        try:
            cursor = db.execute(
                "INSERT INTO security_alerts(created_at, rule_id, event_count, window_seconds) "
                "VALUES(?, ?, ?, ?)",
                (alert["created_at"], alert["rule_id"], alert["event_count"], alert["window_seconds"]),
            )
            db.commit()
            return int(cursor.lastrowid)
        finally:
            db.close()

    def recent_security_alerts(self, limit: int = 50) -> list[dict]:
        db = self._connect()
        try:
            rows = db.execute(
                "SELECT * FROM security_alerts ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            db.close()
