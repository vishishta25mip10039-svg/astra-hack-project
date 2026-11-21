# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/connectivity.py
# PURPOSE: Simulate network channel states + sync pending SOS
# ============================================================

from backend.db import get_connection
from datetime import datetime


def get_state() -> dict:
    """Read current channel state from DB."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM connectivity_state WHERE id=1").fetchone()
    conn.close()
    return dict(row) if row else {"cellular": 1, "internet": 1, "satellite": 0}


def set_state(cellular: bool, internet: bool, satellite: bool):
    """Update channel toggles in DB."""
    conn = get_connection()
    conn.execute("""
        UPDATE connectivity_state
        SET cellular=?, internet=?, satellite=?, last_updated=?
        WHERE id=1
    """, (int(cellular), int(internet), int(satellite), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def can_transmit() -> tuple:
    """
    Returns (can_send: bool, channel_name: str)
    Priority: cellular/internet > satellite_sim > none
    """
    state = get_state()
    if state["cellular"] or state["internet"]:
        return True, "cellular/internet"
    if state["satellite"]:
        return True, "satellite_sim"
    return False, "none"


def sync_pending_requests():
    """
    Flush all pending SOS requests if any channel is active.
    Returns (count_synced: int, message: str)
    """
    can_send, channel = can_transmit()
    if not can_send:
        return 0, "No communication channel available. Requests remain in queue."

    conn = get_connection()
    now = datetime.utcnow().isoformat()
    cur = conn.cursor()

    pending = cur.execute(
        "SELECT id FROM sos_requests WHERE comm_status='pending'"
    ).fetchall()

    count = 0
    for row in pending:
        rid = row["id"]
        cur.execute("""
            UPDATE sos_requests
            SET comm_status='synchronised', synced_at=?
            WHERE id=?
        """, (now, rid))
        cur.execute("""
            INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
            VALUES (?, 'SYNCHRONISED', ?, ?, ?)
        """, (rid, channel, now, f"Auto-sync via {channel}"))
        count += 1

    conn.commit()
    conn.close()
    return count, f"Synchronised {count} request(s) via {channel}"
