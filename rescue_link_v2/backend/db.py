# ============================================================
# MEMBER 1 — BACKEND
# FILE: backend/db.py
# PURPOSE: Database schema creation + demo seed data + migrations
# ============================================================

import sqlite3
import os
import json
import uuid
from datetime import datetime, timedelta

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
            is_medical        INTEGER NOT NULL DEFAULT 0,
            comm_cutoff       INTEGER NOT NULL DEFAULT 0,
            priority_score    INTEGER NOT NULL DEFAULT 0,
            score_breakdown   TEXT,
            description       TEXT,
            comm_status       TEXT NOT NULL DEFAULT 'pending',
            rescue_status     TEXT NOT NULL DEFAULT 'open',
            priority          TEXT NOT NULL DEFAULT 'moderate',
            assigned_team     TEXT,
            synced_at         TEXT,
            sync_channel      TEXT,
            hash_fingerprint  TEXT,
            resolved_at       TEXT
        )
    """)

    # Schema migration: check and add missing columns if upgrading existing db
    existing_cols = [row[1] for row in cur.execute("PRAGMA table_info(sos_requests)").fetchall()]
    new_columns = [
        ("is_medical", "INTEGER NOT NULL DEFAULT 0"),
        ("comm_cutoff", "INTEGER NOT NULL DEFAULT 0"),
        ("priority_score", "INTEGER NOT NULL DEFAULT 0"),
        ("score_breakdown", "TEXT"),
        ("sync_channel", "TEXT"),
        ("hash_fingerprint", "TEXT"),
    ]
    for col_name, col_def in new_columns:
        if col_name not in existing_cols:
            cur.execute(f"ALTER TABLE sos_requests ADD COLUMN {col_name} {col_def}")

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
            base_location       TEXT,
            latitude            REAL,
            longitude           REAL,
            specialty           TEXT,
            contact             TEXT
        )
    """)

    # Schema migration for rescue_teams
    team_cols = [row[1] for row in cur.execute("PRAGMA table_info(rescue_teams)").fetchall()]
    for col_name, col_def in [
        ("latitude", "REAL"),
        ("longitude", "REAL"),
        ("specialty", "TEXT"),
        ("contact", "TEXT"),
    ]:
        if col_name not in team_cols:
            cur.execute(f"ALTER TABLE rescue_teams ADD COLUMN {col_name} {col_def}")

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
        ("TEAM_ALPHA", "NDRF Unit Alpha", "available", None, "Delhi HQ", 28.6139, 77.2090, "Urban Search & Heavy Rescue", "+91-11-2343-8000"),
        ("TEAM_BETA",  "NDRF Unit Beta",  "available", None, "Mumbai HQ", 19.0760, 72.8777, "Coastal & Cyclone Relief", "+91-22-2266-9000"),
        ("TEAM_GAMMA", "NDRF Unit Gamma", "available", None, "Chennai HQ", 13.0827, 80.2707, "Flood & Swift Water Rescue", "+91-44-2536-7000"),
        ("TEAM_DELTA", "NDRF Unit Delta", "available", None, "Kolkata HQ", 22.5726, 88.3639, "Mass Evacuation & Logistics", "+91-33-2214-6000"),
        ("TEAM_ECHO",  "SDRF Unit Echo",  "available", None, "Bhopal HQ", 23.2599, 77.4126, "Medical Triage & Field Support", "+91-755-244-5000"),
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO rescue_teams (id, name, status, current_assignment, base_location, latitude, longitude, specialty, contact)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, teams)

    conn.commit()
    conn.close()


def seed_demo_data():
    """Load realistic demo SOS requests aligned with ASTRA 2026 presentation."""
    now = datetime.utcnow()
    
    demo_requests = [
        {
            "id": f"SOS-{uuid.uuid4().hex[:8].upper()}",
            "created_at": (now - timedelta(hours=2, minutes=45)).isoformat(),
            "category": "Flood",
            "latitude": 25.5941,
            "longitude": 85.1376,
            "people_affected": 12,
            "severity": "Critical",
            "immediate_danger": 1,
            "is_medical": 1,
            "comm_cutoff": 0,
            "priority_score": 90,
            "score_breakdown": json.dumps({"danger": 40, "medical": 30, "people": 20, "comms": 0, "base": 0}),
            "description": "Village submerged up to first floor. 12 citizens trapped on roof, pregnant woman requires urgent evacuation.",
            "comm_status": "synchronised",
            "rescue_status": "in_progress",
            "priority": "critical",
            "assigned_team": "TEAM_ALPHA",
            "synced_at": (now - timedelta(hours=2, minutes=44)).isoformat(),
            "sync_channel": "cellular/internet",
            "hash_fingerprint": f"RL-SHA256-{uuid.uuid4().hex[:12].upper()}",
        },
        {
            "id": f"SOS-{uuid.uuid4().hex[:8].upper()}",
            "created_at": (now - timedelta(hours=1, minutes=15)).isoformat(),
            "category": "Landslide",
            "latitude": 30.7346,
            "longitude": 79.0669,
            "people_affected": 5,
            "severity": "High",
            "immediate_danger": 1,
            "is_medical": 0,
            "comm_cutoff": 1,
            "priority_score": 70,
            "score_breakdown": json.dumps({"danger": 40, "medical": 0, "people": 20, "comms": 10, "base": 0}),
            "description": "Mountain road blocked by debris near Kedarnath valley. 5 pilgrims stranded with falling rocks risk.",
            "comm_status": "pending",
            "rescue_status": "open",
            "priority": "critical",
            "assigned_team": None,
            "synced_at": None,
            "sync_channel": None,
            "hash_fingerprint": f"RL-SHA256-{uuid.uuid4().hex[:12].upper()}",
        },
        {
            "id": f"SOS-{uuid.uuid4().hex[:8].upper()}",
            "created_at": (now - timedelta(minutes=28)).isoformat(),
            "category": "Medical Assistance",
            "latitude": 23.2599,
            "longitude": 77.4126,
            "people_affected": 2,
            "severity": "Moderate",
            "immediate_danger": 0,
            "is_medical": 1,
            "comm_cutoff": 1,
            "priority_score": 60,
            "score_breakdown": json.dumps({"danger": 0, "medical": 30, "people": 20, "comms": 10, "base": 0}),
            "description": "Elderly patients with oxygen shortage after local transformer explosion. Road access restricted.",
            "comm_status": "pending",
            "rescue_status": "open",
            "priority": "high",
            "assigned_team": None,
            "synced_at": None,
            "sync_channel": None,
            "hash_fingerprint": f"RL-SHA256-{uuid.uuid4().hex[:12].upper()}",
        },
    ]

    conn = get_connection()
    cur = conn.cursor()
    for r in demo_requests:
        cur.execute("""
            INSERT OR REPLACE INTO sos_requests
            (id, created_at, category, latitude, longitude, people_affected,
             severity, immediate_danger, is_medical, comm_cutoff, priority_score, score_breakdown,
             description, comm_status, rescue_status, priority, assigned_team, synced_at, sync_channel, hash_fingerprint)
            VALUES (:id, :created_at, :category, :latitude, :longitude, :people_affected,
                    :severity, :immediate_danger, :is_medical, :comm_cutoff, :priority_score, :score_breakdown,
                    :description, :comm_status, :rescue_status, :priority, :assigned_team, :synced_at, :sync_channel, :hash_fingerprint)
        """, r)
        cur.execute("""
            INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
            VALUES (?, 'SOS_CREATED', 'citizen_portal', ?, 'Recorded in local SQLite queue')
        """, (r["id"], r["created_at"]))
        if r["comm_status"] == "synchronised":
            cur.execute("""
                INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
                VALUES (?, 'SYNCHRONISED', ?, ?, 'Immediate uplink confirmation via terrestrial network')
            """, (r["id"], r["sync_channel"], r["synced_at"]))
        if r["assigned_team"]:
            cur.execute("""
                INSERT INTO comm_logs (request_id, event, channel, timestamp, notes)
                VALUES (?, 'TEAM_ASSIGNED', 'command_centre', ?, 'NDRF Unit Alpha dispatched')
            """, (r["id"], r["synced_at"]))
    conn.commit()
    conn.close()


def reset_demo_data():
    """Clear all SOS records and re-seed clean baseline."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM comm_logs")
    cur.execute("DELETE FROM sos_requests")
    cur.execute("UPDATE rescue_teams SET status='available', current_assignment=NULL")
    cur.execute("UPDATE connectivity_state SET cellular=1, internet=1, satellite=0, last_updated=datetime('now') WHERE id=1")
    conn.commit()
    conn.close()
    seed_demo_data()

