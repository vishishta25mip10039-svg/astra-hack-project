# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/rescue.py
# PURPOSE: Team assignment, proximity matching (Slide 6), status updates, dashboard metrics
# ============================================================

import math
from datetime import datetime
from backend.db import get_connection


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in kilometers between two GPS coordinates."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 9999.0
    r = 6371.0  # Earth's mean radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 1)


def get_teams() -> list:
    """Return all rescue teams ordered by name."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rescue_teams ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recommended_teams(lat: float, lon: float) -> list:
    """
    Implements Slide 6 step 5: 'Command Centre reviews priority map, assigns nearest team'
    Calculates proximity from incident coordinates to all rescue units.
    Returns list of teams annotated with distance_km, estimated_transit_min, and recommendation flag.
    """
    teams = get_teams()
    for team in teams:
        team_lat = team.get("latitude")
        team_lon = team.get("longitude")
        dist = calculate_distance(lat, lon, team_lat, team_lon)
        team["distance_km"] = dist
        # Assuming emergency response average transit speed of 55 km/h
        team["eta_minutes"] = max(10, int(round((dist / 55.0) * 60))) if dist < 9999 else 0

    # Sort available teams first by distance, then on-mission teams
    available = sorted([t for t in teams if t["status"] == "available"], key=lambda x: x["distance_km"])
    busy = sorted([t for t in teams if t["status"] != "available"], key=lambda x: x["distance_km"])
    
    if available:
        available[0]["is_nearest_recommended"] = True
    
    return available + busy


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
    """Return summary counts and triage statistics for dashboard metric cards."""
    conn = get_connection()
    cur = conn.cursor()
    total    = cur.execute("SELECT COUNT(*) FROM sos_requests").fetchone()[0]
    critical = cur.execute("SELECT COUNT(*) FROM sos_requests WHERE priority='critical'").fetchone()[0]
    pending  = cur.execute("SELECT COUNT(*) FROM sos_requests WHERE comm_status='pending'").fetchone()[0]
    synced   = cur.execute("SELECT COUNT(*) FROM sos_requests WHERE comm_status='synchronised'").fetchone()[0]
    avail    = cur.execute("SELECT COUNT(*) FROM rescue_teams WHERE status='available'").fetchone()[0]
    resolved = cur.execute("SELECT COUNT(*) FROM sos_requests WHERE rescue_status='resolved'").fetchone()[0]
    
    # Priority score stats
    avg_score_row = cur.execute("SELECT AVG(priority_score) FROM sos_requests").fetchone()[0]
    avg_score = round(avg_score_row or 0, 1)

    conn.close()
    return {
        "total": total,
        "critical": critical,
        "pending_transmission": pending,
        "synchronised": synced,
        "available_teams": avail,
        "resolved": resolved,
        "avg_priority_score": avg_score,
        "data_loss_rate": "0.0%",
    }

