# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/sos.py
# PURPOSE: Priority Engine (Slide 7), create SOS, fetch requests + logs
# ============================================================

import json
import uuid
import hashlib
from datetime import datetime
from backend.db import get_connection
from backend.connectivity import can_transmit

# Slide 7 response tiers
RESPONSE_TIERS = {
    "critical": {"min": 70, "max": 100, "action": "Life at risk — dispatch now", "queue": "Immediate", "color": "#C84D50"},
    "high":     {"min": 40, "max": 69,  "action": "Urgent — assign within 10 minutes", "queue": "Priority queue", "color": "#D77B42"},
    "moderate": {"min": 20, "max": 39,  "action": "Serious but stable", "queue": "Next available", "color": "#B38D3D"},
    "low":      {"min": 0,  "max": 19,  "action": "Queue for next available team", "queue": "Standard queue", "color": "#44856D"},
}


def calculate_priority_score(category: str, severity: str, people_affected: int,
                             immediate_danger: bool, is_medical: bool = False,
                             comm_cutoff: bool = False) -> dict:
    """
    Intelligent Triage Engine conforming strictly to Slide 7 of ASTRA PPT:
    - Immediate Danger to Life: +40 pts
    - Medical Emergency:        +30 pts
    - Multiple People Affected: +20 pts
    - Communication Cut Off:    +10 pts
    Total max: 100 -> AUTO CRITICAL
    """
    # Auto-flag medical if category indicates it
    effective_medical = is_medical or (category == "Medical Assistance")
    # Multiple people affected (mass casualty risk)
    effective_multiple = (people_affected > 1)

    pts_danger = 40 if immediate_danger else 0
    pts_medical = 30 if effective_medical else 0
    pts_people = 20 if effective_multiple else 0
    pts_comms = 10 if comm_cutoff else 0

    score = pts_danger + pts_medical + pts_people + pts_comms

    # If no factors were ticked, provide baseline score from selected severity
    base_pts = 0
    if score == 0:
        base_map = {"Critical": 70, "High": 45, "Moderate": 25, "Low": 10}
        base_pts = base_map.get(severity, 15)
        score = base_pts

    # Clamp between 0 and 100
    score = max(0, min(100, score))

    if score >= 70:
        tier = "critical"
    elif score >= 40:
        tier = "high"
    elif score >= 20:
        tier = "moderate"
    else:
        tier = "low"

    tier_info = RESPONSE_TIERS[tier]

    return {
        "score": score,
        "tier": tier,
        "action": tier_info["action"],
        "queue": tier_info["queue"],
        "color": tier_info["color"],
        "breakdown": {
            "danger": pts_danger,
            "medical": pts_medical,
            "people": pts_people,
            "comms": pts_comms,
            "base": base_pts,
        }
    }


def create_sos(category: str, latitude: float, longitude: float,
               people_affected: int, severity: str, immediate_danger: bool,
               description: str = "", is_medical: bool = False,
               comm_cutoff: bool = False) -> dict:
    """
    Create and persist a new SOS request.
    Uses Priority Engine to evaluate score (0-100) and response tier.
    Automatically checks connectivity: transmits if link available,
    otherwise queues safely into local SQLite (store-and-forward).
    """
    request_id = f"SOS-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

    # Check connectivity
    can_send, channel = can_transmit()
    comm_status = "synchronised" if can_send else "pending"

    # If network is down, comms is automatically cut off (+10 pts)
    effective_cutoff = comm_cutoff or (not can_send)

    # Calculate priority using exact Slide 7 triage algorithm
    triage = calculate_priority_score(
        category=category,
        severity=severity,
        people_affected=people_affected,
        immediate_danger=immediate_danger,
        is_medical=is_medical,
        comm_cutoff=effective_cutoff,
    )
    priority = triage["tier"]
    priority_score = triage["score"]
    score_breakdown_json = json.dumps(triage["breakdown"])

    # Cryptographic transmission fingerprint for the Delivery Receipt
    hash_payload = f"{request_id}:{now}:{category}:{latitude}:{longitude}:{priority_score}"
    hash_fingerprint = f"RL-SHA256-{hashlib.sha256(hash_payload.encode()).hexdigest()[:12].upper()}"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sos_requests
        (id, created_at, category, latitude, longitude, people_affected,
         severity, immediate_danger, is_medical, comm_cutoff, priority_score,
         score_breakdown, description, comm_status, rescue_status, priority,
         synced_at, sync_channel, hash_fingerprint)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?)
    """, (
        request_id, now, category, latitude, longitude, people_affected,
        severity, int(immediate_danger), int(is_medical), int(effective_cutoff),
        priority_score, score_breakdown_json, description, comm_status, priority,
        now if can_send else None,
        channel if can_send else None,
        hash_fingerprint
    ))

    # Log creation event
    cur.execute("""
        INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
        VALUES (?, 'SOS_CREATED', 'citizen_portal', ?, ?)
    """, (request_id, now, f"Stored locally in SQLite queue. Priority score: {priority_score}/100 ({priority.upper()})."))

    # Log transmission or offline queue status
    if can_send:
        cur.execute("""
            INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
            VALUES (?, 'SYNCHRONISED', ?, ?, ?)
        """, (request_id, channel, now, f"Immediate transmission via {channel}. Delivery receipt {hash_fingerprint} generated."))
    else:
        cur.execute("""
            INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
            VALUES (?, 'STORE_AND_FORWARD_PENDING', 'sqlite_local_cache', ?, ?)
        """, (request_id, now, "No terrestrial or satellite link. Safely stored in local SQLite cache. Awaiting uplink."))

    conn.commit()
    conn.close()

    return {
        "id": request_id,
        "created_at": now,
        "comm_status": comm_status,
        "priority": priority,
        "priority_score": priority_score,
        "score_breakdown": triage["breakdown"],
        "action": triage["action"],
        "channel": channel,
        "hash_fingerprint": hash_fingerprint,
    }


def get_all_requests(filters: dict = None) -> list:
    """Fetch all SOS requests with optional filters, ordered by priority score then date."""
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
    query += " ORDER BY priority_score DESC, created_at DESC"

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
    """Fetch all communication log entries for a request, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comm_logs WHERE request_id=? ORDER BY timestamp DESC, id DESC",
        (request_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

