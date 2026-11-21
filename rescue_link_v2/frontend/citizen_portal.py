# ============================================================
# MEMBER 2 — FRONTEND
# FILE: frontend/citizen_portal.py
# PURPOSE: SOS submission form + recent requests table
# ============================================================

import streamlit as st
import pandas as pd
from backend.sos import create_sos, get_all_requests
from utils.helpers import (
    CATEGORIES, SEVERITIES,
    validate_coordinates, priority_badge, comm_badge, rescue_badge,
)

# Quick demo locations for hackathon demo
DEMO_LOCATIONS = {
    "Custom": (None, None),
    "Patna, Bihar (Flood Zone)":    (25.5941, 85.1376),
    "Kedarnath, Uttarakhand":        (30.7346, 79.0669),
    "Bhopal, MP":                    (23.2599, 77.4126),
    "Leh, Ladakh":                   (34.1526, 77.5771),
    "Kolkata, WB":                   (22.5726, 88.3639),
}


def show():
    st.markdown("""
    <div class="hero-banner">
        <h1>🆘 Citizen SOS Portal</h1>
        <p>Submit an emergency request — works online or offline via satellite uplink</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_recent = st.columns([1.1, 0.9])

    # ── SOS Form ─────────────────────────────────────────────
    with col_form:
        st.subheader("📋 Submit Emergency SOS")

        with st.form("sos_form", clear_on_submit=True):
            category = st.selectbox("Emergency Category", CATEGORIES)
            severity = st.selectbox("Severity Level", SEVERITIES, index=1)
            people   = st.number_input("People Affected", min_value=1, max_value=500, value=1)
            danger   = st.checkbox("⚠️ Immediate life danger")
            desc     = st.text_area("Description", placeholder="Describe the emergency situation...", height=90)

            st.markdown("**📍 Location**")
            preset = st.selectbox("Quick Location", list(DEMO_LOCATIONS.keys()))
            preset_lat, preset_lon = DEMO_LOCATIONS[preset]

            c1, c2 = st.columns(2)
            with c1:
                lat = st.number_input("Latitude",  value=float(preset_lat) if preset_lat else 23.2599,
                                      format="%.4f", step=0.0001)
            with c2:
                lon = st.number_input("Longitude", value=float(preset_lon) if preset_lon else 77.4126,
                                      format="%.4f", step=0.0001)

            submitted = st.form_submit_button("🚨 SUBMIT SOS", use_container_width=True)

        if submitted:
            valid, err = validate_coordinates(lat, lon)
            if not valid:
                st.error(f"Invalid coordinates: {err}")
            else:
                result = create_sos(
                    category=category, latitude=lat, longitude=lon,
                    people_affected=people, severity=severity,
                    immediate_danger=danger, description=desc,
                )
                color = "#FF4444" if result["priority"] == "critical" else "#00D4FF"
                st.markdown(f"""
                <div style="background:#0F1629;border:2px solid {color};border-radius:10px;padding:20px;margin-top:12px;">
                    <div style="color:{color};font-size:1.2rem;font-weight:700;">✅ SOS Submitted</div>
                    <div style="color:#E8F4FD;margin-top:8px;">
                        <b>ID:</b> {result['id']}<br>
                        <b>Priority:</b> {priority_badge(result['priority'])}<br>
                        <b>Transmission:</b> {comm_badge(result['comm_status'])}<br>
                        <b>Channel:</b> {result['channel']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Recent Requests ───────────────────────────────────────
    with col_recent:
        st.subheader("📋 Recent SOS Requests")
        requests = get_all_requests()[:10]
        if not requests:
            st.info("No SOS requests yet. Submit one using the form.")
        else:
            rows = []
            for r in requests:
                rows.append({
                    "ID":         r["id"],
                    "Category":   r["category"],
                    "Priority":   priority_badge(r["priority"]),
                    "Comm":       comm_badge(r["comm_status"]),
                    "Rescue":     rescue_badge(r["rescue_status"]),
                    "People":     r["people_affected"],
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
