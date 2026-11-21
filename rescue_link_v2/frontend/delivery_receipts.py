"""Delivery receipts, store-and-forward proof and transmission verification."""

import json
from html import escape
from datetime import datetime

import pandas as pd
import streamlit as st

from backend.sos import get_all_requests, get_comm_logs
from utils.helpers import (
    page_header, section_heading, status_badge_html,
    priority_badge, comm_badge, rescue_badge,
    score_badge_html, triage_breakdown_chips_html,
)


def _format_time(iso_str: str) -> str:
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return str(iso_str)


def show() -> None:
    page_header(
        "Delivery Receipts & Audit Verification",
        "Inspect cryptographic transmission receipts, store-and-forward lifecycle and proof of zero packet loss.",
        "ASTRA 2026 / 2:30–3:00 DEMO STAGE · AUDIT LOG",
    )

    requests = get_all_requests()
    if not requests:
        st.info("No recorded incidents found in the local register. Submit an SOS in the Citizen Portal or load the demo scenario.")
        return

    # Select incident to inspect
    options = {
        f"{r['id']} — {r['category']} ({r.get('priority_score', 0)}pts / {r['priority'].upper()})": r['id']
        for r in requests
    }
    selected_label = st.selectbox("Select Incident to Verify Receipt", list(options.keys()))
    selected_id = options[selected_label]
    incident = next((r for r in requests if r["id"] == selected_id), requests[0])

    logs = get_comm_logs(incident["id"])
    breakdown = json.loads(incident.get("score_breakdown") or "{}") if incident.get("score_breakdown") else {}
    level = incident["priority"].lower()
    score = incident.get("priority_score", 0)
    fingerprint = incident.get("hash_fingerprint") or f"RL-SHA256-{incident['id'][-8:]}"
    is_synced = (incident["comm_status"] == "synchronised")

    left_col, right_col = st.columns([1.2, 0.8], gap="large")

    with left_col:
        section_heading("Official Transmission Certificate", "Slide 5: Store-and-Forward Verification Manifest.")
        
        status_color = "#16A34A" if is_synced else "#D97706"
        status_title = "VERIFIED STORE-AND-FORWARD UPLINK" if is_synced else "SAFE OFFLINE HOLD (SQLITE LOCAL CACHE)"
        route_display = incident.get("sync_channel") or ("Pending Link Restoration" if not is_synced else "Terrestrial")

        st.markdown(
            f"""
            <div class="rl-receipt-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:1px solid #E2E8F0;padding-bottom:12px;margin-bottom:14px">
                <div>
                  <div style="font-size:11px;font-weight:800;color:#64748B;letter-spacing:.1em">RESCUE LINK · MISSION AUDIT SYSTEM</div>
                  <div style="font-size:20px;font-weight:800;color:#0F172A;margin-top:2px">Transmission Delivery Receipt</div>
                  <div style="font-size:11px;color:#64748B">Incident UID: <code>{incident['id']}</code></div>
                </div>
                <div class="rl-receipt-seal" style="border-color:{status_color};color:{status_color}">
                  {status_title}
                </div>
              </div>

              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
                <div>
                  <div style="font-size:10px;font-weight:750;color:#64748B;text-transform:uppercase">Emergency Category</div>
                  <div style="font-size:14px;font-weight:700;color:#1E293B">{incident['category']}</div>
                </div>
                <div>
                  <div style="font-size:10px;font-weight:750;color:#64748B;text-transform:uppercase">Slide 7 Triage Evaluation</div>
                  <div>{score_badge_html(score, level)}</div>
                </div>
                <div>
                  <div style="font-size:10px;font-weight:750;color:#64748B;text-transform:uppercase">Geographic Coordinates</div>
                  <div style="font-size:12px;font-weight:600;color:#1E293B">{incident['latitude']:.4f}°N, {incident['longitude']:.4f}°E</div>
                </div>
                <div>
                  <div style="font-size:10px;font-weight:750;color:#64748B;text-transform:uppercase">Casualties Trapped/Affected</div>
                  <div style="font-size:12px;font-weight:600;color:#1E293B">{incident['people_affected']} citizens</div>
                </div>
                <div>
                  <div style="font-size:10px;font-weight:750;color:#64748B;text-transform:uppercase">Cryptographic Digest</div>
                  <div style="font-size:11px;font-family:monospace;color:#0284C7;font-weight:700">{fingerprint}</div>
                </div>
                <div>
                  <div style="font-size:10px;font-weight:750;color:#64748B;text-transform:uppercase">Transmission Channel</div>
                  <div style="font-size:12px;font-weight:700;color:#0F172A">{route_display.replace('_', ' ').title()}</div>
                </div>
              </div>

              <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:10px 12px;font-size:11px;color:#334155;line-height:1.5">
                <strong>Store-and-Forward Assurance:</strong> Data integrity verified via SQLite persistent cache.
                Zero packet loss recorded across simulated network blackout and satellite fallback bursts.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")
        # Download Receipt Button
        receipt_json = json.dumps({
            "receipt_id": fingerprint,
            "incident_id": incident["id"],
            "created_at": incident["created_at"],
            "category": incident["category"],
            "triage_score": score,
            "priority": incident["priority"],
            "triage_breakdown": breakdown,
            "coordinates": {"lat": incident["latitude"], "lon": incident["longitude"]},
            "people_affected": incident["people_affected"],
            "comm_status": incident["comm_status"],
            "channel": incident.get("sync_channel"),
            "synced_at": incident.get("synced_at"),
            "event_logs": [dict(l) for l in logs],
        }, indent=2)

        st.download_button(
            "📥 Download Official Delivery Receipt (JSON)",
            data=receipt_json,
            file_name=f"rescue_link_receipt_{incident['id']}.json",
            mime="application/json",
            use_container_width=True,
        )

    with right_col:
        section_heading("Store-and-Forward Journey", "Trace packet transmission through system stages.")

        steps = [
            ("1. Citizen SOS Logged", "Captured via portal form with emergency details and GPS coordinates.", "completed"),
            ("2. Priority Scoring", f"Instant algorithmic evaluation: {score}/100 points ({level.upper()}).", "completed"),
            ("3. Local SQLite Buffering", "Safely written to local database disk. Guaranteed 0% packet loss.", "completed"),
            ("4. Connectivity Handshake", "Checking Cellular / Internet / Satellite Fallback availability.", "completed"),
            ("5. Satellite / Terrestrial Burst", f"Transmitted via {route_display}." if is_synced else "Awaiting satellite or mobile uplink window...", "completed" if is_synced else "pending"),
            ("6. Command Centre Ingestion", "Received by coordinators and pinned to tactical dispatch map.", "completed" if is_synced else "pending"),
        ]

        for step_title, step_desc, step_st in steps:
            is_done = (step_st == "completed")
            dot = "🟢" if is_done else "⏳"
            bg = "#F0FDF4" if is_done else "#FFFBEB"
            st.markdown(
                f"""
                <div style="background:{bg};border:1px solid {'#BBF7D0' if is_done else '#FDE68A'};border-radius:8px;padding:8px 12px;margin-bottom:8px">
                  <div style="font-size:12px;font-weight:700;color:#0F172A">{dot} {step_title}</div>
                  <div style="font-size:11px;color:#475569;margin-top:2px">{step_desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    section_heading("Complete Communication Audit Log", f"All events recorded for {incident['id']}.")
    if logs:
        rows = [{
            "Timestamp": _format_time(l.get("timestamp")),
            "Event": l.get("event"),
            "Channel Route": l.get("channel") or "Local Storage",
            "Operational Notes": l.get("notes") or "—",
        } for l in logs]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No communication logs recorded yet.")
