# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/rescue.py
# PURPOSE: Team assignment, status updates, dashboard metrics
# ============================================================

from datetime import datetime
from backend.db import get_connection


def get_teams() -> list:
    """Return all rescue teams ordered by name."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rescue_teams ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def assign_team(request_id: str, team_id: str, notes: str = "") -> bool:
    """Assign a rescue team to an SOS request."""
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    cur.execute("""
        UPDATE sos_requests
        SET assigned_team=?, rescue_status='assigned'
        WHERE id=?
    """, (team_id, request_id))

    cur.execute("""
        UPDATE rescue_teams SET status='on_mission', current_assignment=?
        WHERE id=?
    """, (request_id, team_id))

    cur.execute("""
        INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
        VALUES (?, 'TEAM_ASSIGNED', 'command_centre', ?, ?)
    """, (request_id, now, f"Team {team_id} assigned. {notes}"))

    conn.commit()
    conn.close()
    return True


def update_rescue_status(request_id: str, new_status: str, notes: str = "") -> bool:
    """Update rescue status and free team if resolved."""
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    update_fields = "rescue_status=?"
    params = [new_status]

    if new_status == "resolved":
        update_fields += ", resolved_at=?"
        params.append(now)
        team_row = cur.execute(
            "SELECT assigned_team FROM sos_requests WHERE id=?", (request_id,)
        ).fetchone()
        if team_row and team_row["assigned_team"]:
            cur.execute("""
                UPDATE rescue_teams SET status='available', current_assignment=NULL
                WHERE id=?
            """, (team_row["assigned_team"],))

    params.append(request_id)
    cur.execute(f"UPDATE sos_requests SET {update_fields} WHERE id=?", params)

    cur.execute("""
        INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
        VALUES (?, 'STATUS_UPDATE', 'command_centre', ?, ?)
    """, (request_id, now, f"Status -> {new_status}. {notes}"))

    conn.commit()
    conn.close()
    return True


def get_metrics() -> dict:
    """Return summary counts for dashboard metric cards."""
    conn = get_connection()
    cur = conn.cursor()
    total    = cur.execute("SELECT COUNT(*) FROM sos_requests").fetchone()[0]
    critical = cur.execute("SELECT COUNT(*) FROM sos_requests WHERE priority='critical'").fetchone()[0]
    pending  = cur.execute("SELECT COUNT(*) FROM sos_requests WHERE comm_status='pending'").fetchone()[0]
    avail    = cur.execute("SELECT COUNT(*) FROM rescue_teams WHERE status='available'").fetchone()[0]
    resolved = cur.execute("SELECT COUNT(*) FROM sos_requests WHERE rescue_status='resolved'").fetchone()[0]
    conn.close()
    return {
        "total": total,
        "critical": critical,
        "pending_transmission": pending,
        "available_teams": avail,
        "resolved": resolved,
    }
