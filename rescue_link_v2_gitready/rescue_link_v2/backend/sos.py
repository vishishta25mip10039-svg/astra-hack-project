# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/sos.py
# PURPOSE: Create SOS requests, fetch requests + logs
# ============================================================

import uuid
from datetime import datetime
from backend.db import get_connection
from backend.connectivity import can_transmit

PRIORITY_MAP = {
    "Critical": "critical",
    "High":     "high",
    "Moderate": "moderate",
    "Low":      "low",
}


def create_sos(category: str, latitude: float, longitude: float,
               people_affected: int, severity: str, immediate_danger: bool,
               description: str = "") -> dict:
    """
    Create and persist a new SOS request.
    Automatically sets comm_status based on current channel state.
    Returns saved record summary dict.
    """
    request_id = f"SOS-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

    # Derive priority
    priority = "critical" if (immediate_danger or severity == "Critical") \
               else PRIORITY_MAP.get(severity, "moderate")

    # Check connectivity
    can_send, channel = can_transmit()
    comm_status = "synchronised" if can_send else "pending"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sos_requests
        (id, created_at, category, latitude, longitude, people_affected,
         severity, immediate_danger, description, comm_status, rescue_status,
         priority, synced_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)
    """, (
        request_id, now, category, latitude, longitude, people_affected,
        severity, int(immediate_danger), description, comm_status, priority,
        now if can_send else None
    ))

    # Log creation
    cur.execute("""
        INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
        VALUES (?, 'SOS_CREATED', 'citizen_portal', ?, ?)
    """, (request_id, now, f"Created via {channel}. Status: {comm_status}"))

    # Log immediate sync if applicable
    if can_send:
        cur.execute("""
            INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
            VALUES (?, 'SYNCHRONISED', ?, ?, 'Immediate sync on creation')
        """, (request_id, channel, now))

    conn.commit()
    conn.close()

    return {
        "id": request_id,
        "created_at": now,
        "comm_status": comm_status,
        "priority": priority,
        "channel": channel,
    }


def get_all_requests(filters: dict = None) -> list:
    """Fetch all SOS requests with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM sos_requests"
    clauses, params = [], []

    if filters:
        if filters.get("category") and filters["category"] != "All":
            clauses.append("category = ?")
            params.append(filters["category"])
        if filters.get("priority") and filters["priority"] != "All":
            clauses.append("priority = ?")
            params.append(filters["priority"])
        if filters.get("comm_status") and filters["comm_status"] != "All":
            clauses.append("comm_status = ?")
            params.append(filters["comm_status"])
        if filters.get("rescue_status") and filters["rescue_status"] != "All":
            clauses.append("rescue_status = ?")
            params.append(filters["rescue_status"])

    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY created_at DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_request(request_id: str):
    """Fetch a single SOS request by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM sos_requests WHERE id=?", (request_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_comm_logs(request_id: str) -> list:
    """Fetch all communication log entries for a request."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comm_logs WHERE request_id=? ORDER BY timestamp DESC",
        (request_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
