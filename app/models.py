from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Path to the SQLite database storing project information and schedules
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


def _get_conn() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create required tables if they do not exist."""
    conn = _get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id TEXT NOT NULL,
                name TEXT NOT NULL,
                metadata TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                scheduled_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Project helpers
# ---------------------------------------------------------------------------

def save_project(folder_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> int:
    """Insert a new project record and return its ID."""
    init_db()
    conn = _get_conn()
    try:
        meta_json = json.dumps(metadata) if metadata is not None else None
        cur = conn.execute(
            "INSERT INTO projects (folder_id, name, metadata) VALUES (?, ?, ?)",
            (folder_id, name, meta_json),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    """Return a project row as a dictionary or ``None`` if not found."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cur.fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    data = dict(row)
    if data.get("metadata"):
        data["metadata"] = json.loads(data["metadata"])
    return data


# ---------------------------------------------------------------------------
# Schedule helpers
# ---------------------------------------------------------------------------

def add_schedule(
    project_id: int,
    scheduled_at: datetime,
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    """Persist a scheduled upload for a project."""
    init_db()
    conn = _get_conn()
    try:
        meta_json = json.dumps(metadata) if metadata is not None else None
        cur = conn.execute(
            "INSERT INTO schedules (project_id, scheduled_at, metadata) VALUES (?, ?, ?)",
            (project_id, scheduled_at.isoformat(), meta_json),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_schedules(project_id: int) -> List[Dict[str, Any]]:
    """Return all scheduled uploads for the given project ordered by time."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT * FROM schedules WHERE project_id = ? ORDER BY scheduled_at",
            (project_id,),
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    schedules: List[Dict[str, Any]] = []
    for r in rows:
        item = dict(r)
        if item.get("metadata"):
            item["metadata"] = json.loads(item["metadata"])
        schedules.append(item)
    return schedules


def update_schedule_status(schedule_id: int, status: str) -> None:
    """Update the status field inside the schedule metadata."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT metadata FROM schedules WHERE id = ?",
            (schedule_id,),
        )
        row = cur.fetchone()
        meta = {}
        if row and row[0]:
            try:
                meta = json.loads(row[0])
            except json.JSONDecodeError:
                meta = {}
        meta["status"] = status
        conn.execute(
            "UPDATE schedules SET metadata = ? WHERE id = ?",
            (json.dumps(meta), schedule_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_statuses() -> List[Dict[str, Any]]:
    """Return status information for all schedules."""
    init_db()
    conn = _get_conn()
    try:
        cur = conn.execute(
            "SELECT id, project_id, scheduled_at, metadata FROM schedules"
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    results: List[Dict[str, Any]] = []
    for row in rows:
        meta = {}
        if row["metadata"]:
            try:
                meta = json.loads(row["metadata"])
            except json.JSONDecodeError:
                meta = {}
        status = meta.get("status", "queued")
        results.append(
            {
                "id": row["id"],
                "project_id": row["project_id"],
                "scheduled_at": row["scheduled_at"],
                "status": status,
            }
        )

    return results
