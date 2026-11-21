# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/db.py
# PURPOSE: Database schema creation + demo seed data
# ============================================================

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rescue_link.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sos_requests (
            id                TEXT PRIMARY KEY,
            created_at        TEXT NOT NULL,
            category          TEXT NOT NULL,
            latitude          REAL NOT NULL,
            longitude         REAL NOT NULL,
            people_affected   INTEGER NOT NULL DEFAULT 1,
            severity          TEXT NOT NULL DEFAULT 'Moderate',
            immediate_danger  INTEGER NOT NULL DEFAULT 0,
            description       TEXT,
            comm_status       TEXT NOT NULL DEFAULT 'pending',
            rescue_status     TEXT NOT NULL DEFAULT 'open',
            priority          TEXT NOT NULL DEFAULT 'moderate',
            assigned_team     TEXT,
            synced_at         TEXT,
            resolved_at       TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comm_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id  TEXT NOT NULL,
            event       TEXT NOT NULL,
            channel     TEXT,
            timestamp   TEXT NOT NULL,
            notes       TEXT,
            FOREIGN KEY (request_id) REFERENCES sos_requests(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rescue_teams (
            id                  TEXT PRIMARY KEY,
            name                TEXT NOT NULL,
            status              TEXT NOT NULL DEFAULT 'available',
            current_assignment  TEXT,
            base_location       TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS connectivity_state (
            id           INTEGER PRIMARY KEY DEFAULT 1,
            cellular     INTEGER NOT NULL DEFAULT 1,
            internet     INTEGER NOT NULL DEFAULT 1,
            satellite    INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO connectivity_state (id, cellular, internet, satellite, last_updated)
        VALUES (1, 1, 1, 0, datetime('now'))
    """)

    teams = [
        ("TEAM_ALPHA", "Team Alpha", "available", None, "Delhi HQ"),
        ("TEAM_BETA",  "Team Beta",  "available", None, "Mumbai HQ"),
        ("TEAM_GAMMA", "Team Gamma", "available", None, "Chennai HQ"),
        ("TEAM_DELTA", "Team Delta", "available", None, "Kolkata HQ"),
        ("TEAM_ECHO",  "Team Echo",  "available", None, "Bhopal HQ"),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO rescue_teams (id, name, status, current_assignment, base_location)
        VALUES (?, ?, ?, ?, ?)
    """, teams)

    conn.commit()
    conn.close()


def seed_demo_data():
    """Load 3 realistic demo SOS requests for hackathon demo."""
    import uuid
    from datetime import datetime, timedelta

    demo_requests = [
        {
            "id": f"SOS-{uuid.uuid4().hex[:8].upper()}",
            "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "category": "Flood",
            "latitude": 25.5941,
            "longitude": 85.1376,
            "people_affected": 12,
            "severity": "Critical",
            "immediate_danger": 1,
            "description": "Village submerged, roof rescue needed",
            "comm_status": "synchronised",
            "rescue_status": "in_progress",
            "priority": "critical",
            "assigned_team": "TEAM_ALPHA",
        },
        {
            "id": f"SOS-{uuid.uuid4().hex[:8].upper()}",
            "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "category": "Landslide",
            "latitude": 27.1767,
            "longitude": 78.0081,
            "people_affected": 4,
            "severity": "High",
            "immediate_danger": 1,
            "description": "Road blocked, injured persons trapped",
            "comm_status": "pending",
            "rescue_status": "open",
            "priority": "high",
            "assigned_team": None,
        },
        {
            "id": f"SOS-{uuid.uuid4().hex[:8].upper()}",
            "created_at": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
            "category": "Medical Assistance",
            "latitude": 23.2599,
            "longitude": 77.4126,
            "people_affected": 2,
            "severity": "Moderate",
            "immediate_danger": 0,
            "description": "Elderly persons require evacuation",
            "comm_status": "pending",
            "rescue_status": "open",
            "priority": "moderate",
            "assigned_team": None,
        },
    ]

    conn = get_connection()
    cur = conn.cursor()
    for r in demo_requests:
        cur.execute("""
            INSERT OR IGNORE INTO sos_requests
            (id, created_at, category, latitude, longitude, people_affected,
             severity, immediate_danger, description, comm_status, rescue_status,
             priority, assigned_team)
            VALUES (:id, :created_at, :category, :latitude, :longitude, :people_affected,
                    :severity, :immediate_danger, :description, :comm_status, :rescue_status,
                    :priority, :assigned_team)
        """, r)
        cur.execute("""
            INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
            VALUES (?, 'SOS_CREATED', 'citizen_portal', datetime('now'), 'Demo seed data')
        """, (r["id"],))
    conn.commit()
    conn.close()
