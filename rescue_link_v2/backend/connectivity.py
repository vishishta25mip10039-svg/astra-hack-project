# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/connectivity.py
# PURPOSE: Simulate network channel states + satellite telemetry + store-and-forward sync
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


def apply_demo_preset(preset: str) -> dict:
    """
    Apply a one-click demo preset matching the ASTRA presentation demo script:
    - 'normal': Primary terrestrial channels active (Cellular + Internet ON, Satellite OFF)
    - 'blackout': Total ground network collapse (All channels OFF -> local SQLite queue test)
    - 'satellite': Disaster fallback active (Cellular + Internet OFF, Satellite Sim ON)
    """
    if preset == "normal":
        set_state(True, True, False)
    elif preset == "blackout":
        set_state(False, False, False)
    elif preset == "satellite":
        set_state(False, False, True)
    return get_state()


def can_transmit() -> tuple:
    """
    Returns (can_send: bool, channel_name: str)
    Priority: cellular/internet (Primary) > satellite_sim (Domain 04 Fallback) > none
    """
    state = get_state()
    if state["cellular"] or state["internet"]:
        return True, "cellular/internet"
    if state["satellite"]:
        return True, "satellite_sim"
    return False, "none"


def get_satellite_telemetry() -> dict:
    """
    Simulated satellite constellation telemetry parameters.
    Models ISRO NavIC / GSAT-7 Series and Starlink LEO burst link for ASTRA 2026 Domain 04.
    """
    state = get_state()
    active = bool(state["satellite"])
    return {
        "active": active,
        "status": "Simulated Active Burst Link" if active else "Simulated Standby / Inactive",
        "constellation": "ISRO NavIC (IRNSS-1I) & Starlink Fallback (Domain 04)",
        "frequency": "S-Band (2492.028 MHz) / Ku-Band Direct-to-Device",
        "protocol": "Store-and-Forward Micro-Burst Packet (ASTRA-04)",
        "simulated_latency_ms": 620 if active else 0,
        "packet_integrity": "100% CRC32 Checksum Verified" if active else "N/A",
        "elevation_angle": "48.2° NNE (Optimal Line-of-Sight)",
    }


def sync_pending_requests():
    """
    Store-and-Forward: Flush all pending SOS requests if any channel is active.
    Returns (count_synced: int, message: str)
    """
    can_send, channel = can_transmit()
    if not can_send:
        return 0, "No communication channel available. Requests remain safely queued in local SQLite."

    conn = get_connection()
    now = datetime.utcnow().isoformat()
    cur = conn.cursor()

    pending = cur.execute(
        "SELECT id FROM sos_requests WHERE comm_status='pending'"
    ).fetchall()

    count = 0
    route_label = "Satellite Simulation (NavIC / Starlink Protocol)" if channel == "satellite_sim" else "Terrestrial Cellular/Internet"

    for row in pending:
        rid = row["id"]
        cur.execute("""
            UPDATE sos_requests
            SET comm_status='synchronised', synced_at=?, sync_channel=?
            WHERE id=?
        """, (now, channel, rid))
        cur.execute("""
            INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
            VALUES (?, 'SYNCHRONISED', ?, ?, ?)
        """, (rid, channel, now, f"Burst transmission via {route_label}. Store-and-forward queue flushed."))
        count += 1

    conn.commit()
    conn.close()
    return count, f"Synchronised {count} request(s) via {route_label}."

